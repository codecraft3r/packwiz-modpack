#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import zipfile
import shutil
import re
import urllib.request
import urllib.parse
import subprocess
import tempfile
import time

# Default CurseForge API key (Prism Launcher developer key)
DEFAULT_CF_KEY = "$2a$10$bLgCcQ5OthzW3wfKDVYx5.sn9FMaNu8aCLdLO5qFiclZ/UMODUXT."

# Common client-side keyword patterns for heuristic side checks
CLIENT_SIDE_KEYWORDS = [
    r"hud", r"minimap", r"map", r"jei", r"rei", r"nei", r"controlling", r"searchables",
    r"advancement", r"screen", r"menu", r"shader", r"iris", r"sodium", r"oculus",
    r"embeddium", r"rubidium", r"zoom", r"tooltip", r"skin", r"darkmode", r"dark-mode",
    r"inventory-tweaks", r"mouse-tweaks", r"item-physic", r"sound", r"animation",
    r"chat-reports", r"auth", r"dynamiclights", r"fancymenu", r"drippy", r"rebind",
    r"visual", r"client", r"optifine", r"graphics"
]

# Common server-side keyword patterns for heuristic side checks
SERVER_SIDE_KEYWORDS = [
    r"server", r"pregen", r"chunkpregen", r"backups", r"admin", r"ftb-essentials",
    r"ftbessentials", r"ranks", r"permissions", r"command", r"restart", r"kick", r"ban",
    r"login-protection"
]

def compute_hashes(filepath):
    """Computes SHA-1, SHA-512, and CurseForge Murmur2 fingerprint."""
    sha1 = hashlib.sha1()
    sha512 = hashlib.sha512()
    
    with open(filepath, 'rb') as f:
        data = f.read()
        
    sha1.update(data)
    sha512.update(data)
    
    # Compute CurseForge Murmur2
    # Normalization: remove bytes 9 (\t), 10 (\n), 13 (\r), and 32 (space)
    normalized = bytearray(b for b in data if b not in (9, 10, 13, 32))
    m = 0x5bd1e995
    r = 24
    seed = 1
    h = seed ^ len(normalized)
    
    length = len(normalized)
    i = 0
    while length >= 4:
        k = normalized[i] | (normalized[i+1] << 8) | (normalized[i+2] << 16) | (normalized[i+3] << 24)
        k = (k * m) & 0xFFFFFFFF
        k ^= (k >> r)
        k = (k * m) & 0xFFFFFFFF
        
        h = (h * m) & 0xFFFFFFFF
        h ^= k
        
        i += 4
        length -= 4
        
    if length == 3:
        h ^= normalized[i+2] << 16
    if length >= 2:
        h ^= normalized[i+1] << 8
    if length >= 1:
        h ^= normalized[i]
        h = (h * m) & 0xFFFFFFFF
        
    h ^= (h >> 13)
    h = (h * m) & 0xFFFFFFFF
    h ^= (h >> 15)
    murmur2 = h & 0xFFFFFFFF
    
    return sha1.hexdigest(), sha512.hexdigest(), murmur2

def make_post_request(url, headers, body_dict):
    """Performs an HTTP POST request returning parsed JSON."""
    data = json.dumps(body_dict).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"HTTP Request failed to {url}: {e}", file=sys.stderr)
        return None

def query_modrinth_bulk(sha512_list):
    """Queries Modrinth bulk version file matching."""
    if not sha512_list:
        return {}
    url = "https://api.modrinth.com/v2/version_files"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "packwiz-modpack-helper/1.0 (contact@codecraft3r.com)"
    }
    body = {
        "hashes": sha512_list,
        "algorithm": "sha512"
    }
    res = make_post_request(url, headers, body)
    return res if res else {}

def query_curseforge_bulk(murmur_list, api_key):
    """Queries CurseForge bulk fingerprint matching."""
    if not murmur_list:
        return {}
    url = "https://api.curseforge.com/v1/fingerprints"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    body = {
        "fingerprints": murmur_list
    }
    res = make_post_request(url, headers, body)
    if res and "data" in res and "exactMatchesByFingerprint" in res["data"]:
        return res["data"]["exactMatchesByFingerprint"]
    return {}

PROJECT_SIDE_CACHE = {}

def get_modrinth_project_sides(project_id):
    """Retrieves client/server side support for a Modrinth project with caching."""
    if project_id in PROJECT_SIDE_CACHE:
        return PROJECT_SIDE_CACHE[project_id]
    time.sleep(0.35)
    url = f"https://api.modrinth.com/v2/project/{project_id}"
    headers = {
        "User-Agent": "packwiz-modpack-helper/1.0 (contact@codecraft3r.com)"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            sides = (data.get("client_side", "required"), data.get("server_side", "required"))
            PROJECT_SIDE_CACHE[project_id] = sides
            return sides
    except Exception as e:
        print(f"Failed to fetch Modrinth project {project_id} sides: {e}", file=sys.stderr)
        return ("required", "required")

def determine_side(filename, modrinth_data=None, cf_data=None):
    """Deduces the correct side based on hosting metadata and filename heuristics."""
    # Apply keyword heuristics first to avoid hitting Modrinth API rate limits
    filename_lower = filename.lower()
    for kw in CLIENT_SIDE_KEYWORDS:
        if re.search(kw, filename_lower):
            return "client"
    for kw in SERVER_SIDE_KEYWORDS:
        if re.search(kw, filename_lower):
            return "server"
            
    # Fallback to Modrinth metadata if available
    if modrinth_data and "project_id" in modrinth_data:
        client_side, server_side = get_modrinth_project_sides(modrinth_data["project_id"])
        if client_side == "unsupported":
            return "server"
        if server_side == "unsupported":
            return "client"
            
    return "both"

def find_new_pw_toml(base_dir, before_files):
    """Scans for newly added .pw.toml files in mods/ or resourcepacks/."""
    current_files = set()
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.pw.toml'):
                current_files.add(os.path.join(root, f))
    new_files = current_files - before_files
    return list(new_files)[0] if new_files else None

def get_current_pw_tomls(base_dir):
    """Gets all .pw.toml files in base_dir."""
    pw_tomls = set()
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.pw.toml'):
                pw_tomls.add(os.path.join(root, f))
    return pw_tomls

def set_pw_toml_side(toml_path, side):
    """Modifies the side key in a .pw.toml file."""
    if not os.path.exists(toml_path):
        return
    with open(toml_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    modified = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('side ='):
            new_lines.append(f'side = "{side}"\n')
            modified = True
        else:
            new_lines.append(line)
            
    # If side was not found, insert it under name/filename
    if not modified:
        inserted = False
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if not inserted and line.strip().startswith('filename ='):
                new_lines.append(f'side = "{side}"\n')
                inserted = True
                
    with open(toml_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Set side to '{side}' in {os.path.basename(toml_path)}")

def run_command(args, cwd=None):
    """Helper to run system commands."""
    try:
        res = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
        return (res.stdout or '').strip()
    except subprocess.CalledProcessError as e:
        print(f"Command {' '.join(args)} failed with exit code {e.returncode}:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return None

def process_file_import(file_path, modrinth_match, cf_match, target_side, workspace_dir):
    """Registers a mod using packwiz CLI and updates side configuration."""
    before_files = get_current_pw_tomls(workspace_dir)
    filename = os.path.basename(file_path)
    
    if modrinth_match:
        project_id = modrinth_match.get("project_id")
        version_id = modrinth_match.get("id")
        print(f"Adding from Modrinth: {filename} (Project: {project_id}, Version: {version_id})")
        
        args = ["packwiz", "-y", "modrinth", "add", "--project-id", project_id, "--version-id", version_id]
        if run_command(args, workspace_dir) is not None:
            new_toml = find_new_pw_toml(workspace_dir, before_files)
            if new_toml:
                set_pw_toml_side(new_toml, target_side)
            return True
            
    elif cf_match:
        # cf_match is list of matches
        match = cf_match[0]
        addon_id = str(match["id"])
        file_id = str(match["file"]["id"])
        print(f"Adding from CurseForge: {filename} (Addon: {addon_id}, File: {file_id})")
        
        args = ["packwiz", "-y", "curseforge", "add", "--addon-id", addon_id, "--file-id", file_id]
        if run_command(args, workspace_dir) is not None:
            new_toml = find_new_pw_toml(workspace_dir, before_files)
            if new_toml:
                set_pw_toml_side(new_toml, target_side)
            return True
            
    return False

def import_raw_files(source_dir, workspace_dir, cf_key):
    """Imports raw mods and copy over overrides from a folder structure."""
    print(f"Scanning raw files from {source_dir}...")
    
    # Locate files
    mod_files = []
    override_dirs = {}
    
    # Check for .minecraft structure
    scan_root = source_dir
    dot_minecraft = os.path.join(source_dir, ".minecraft")
    minecraft = os.path.join(source_dir, "minecraft")
    if os.path.exists(dot_minecraft) and os.path.isdir(dot_minecraft):
        scan_root = dot_minecraft
    elif os.path.exists(minecraft) and os.path.isdir(minecraft):
        scan_root = minecraft
        
    for root, dirs, files in os.walk(scan_root):
        rel_dir = os.path.relpath(root, scan_root)
        
        if rel_dir == "." or rel_dir == "":
            continue
            
        parts = rel_dir.split(os.sep)
        first_part = parts[0]
        
        if first_part == "mods":
            for f in files:
                if f.endswith('.jar'):
                    mod_files.append(os.path.join(root, f))
        elif first_part in ["config", "kubejs", "local", "resourcepacks"]:
            # We treat configs, scripts, local overrides as small files
            # resourcepacks are large but if not matched, user request states:
            # "Large files (.jar & resourcepacks) should never be locally included/commited to the repo."
            # Small files can be, provided a match can't be found.
            # So we separate them:
            # We will search for all files in resourcepacks and try to match them. If not matched, we warning.
            # For configs/kubejs/local, we copy them directly.
            if first_part == "resourcepacks":
                for f in files:
                    if f.endswith('.zip') or f.endswith('.jar'):
                        mod_files.append(os.path.join(root, f))
            else:
                for f in files:
                    src_file = os.path.join(root, f)
                    dest_file = os.path.join(workspace_dir, rel_dir, f)
                    override_dirs[src_file] = dest_file

    if not mod_files:
        print("No mods or resourcepacks found.")
    else:
        # Calculate hashes
        print(f"Calculating hashes for {len(mod_files)} files...")
        hashes = {}
        for f in mod_files:
            try:
                sha1, sha512, murmur = compute_hashes(f)
                hashes[f] = {
                    "sha1": sha1,
                    "sha512": sha512,
                    "murmur": murmur
                }
            except Exception as e:
                print(f"Error hashing {f}: {e}")

        # Bulk lookups
        sha512_list = [h["sha512"] for h in hashes.values()]
        print("Querying Modrinth bulk API...")
        mr_matches = query_modrinth_bulk(sha512_list)
        
        # Determine unmatched hashes for CurseForge
        remaining_files = []
        murmur_list = []
        murmur_to_file = {}
        for f, h in hashes.items():
            sha512 = h["sha512"]
            if sha512 not in mr_matches:
                remaining_files.append(f)
                murmur_list.append(h["murmur"])
                murmur_to_file[h["murmur"]] = f
                
        cf_matches = {}
        if remaining_files:
            print(f"Querying CurseForge bulk API for {len(remaining_files)} files...")
            cf_matches = query_curseforge_bulk(murmur_list, cf_key)
            
        # Process matching
        unresolved_large_files = []
        for f in mod_files:
            h = hashes[f]
            sha512 = h["sha512"]
            murmur = h["murmur"]
            filename = os.path.basename(f)
            
            mr_match = mr_matches.get(sha512)
            cf_match = cf_matches.get(str(murmur))
            
            target_side = determine_side(filename, mr_match, cf_match)
            
            success = process_file_import(f, mr_match, cf_match, target_side, workspace_dir)
            if not success:
                unresolved_large_files.append(f)

        if unresolved_large_files:
            print("\n" + "="*50)
            print("WARNING: The following large files could not be matched on Modrinth or CurseForge:")
            for f in unresolved_large_files:
                size_mb = os.path.getsize(f) / (1024*1024)
                print(f"  - {os.path.basename(f)} ({size_mb:.2f} MB)")
            print("Per safety requirements, these large files have NOT been committed or added to the index.")
            print("Please upload them to Modrinth/CurseForge or host them on a direct URL and add them using:")
            print("  packwiz url add <name> <url>")
            print("="*50 + "\n")

    # Copy override files
    if override_dirs:
        print(f"Copying {len(override_dirs)} small override files...")
        for src, dest in override_dirs.items():
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            print(f"  Copied override: {os.path.relpath(dest, workspace_dir)}")
            
    # Run refresh
    print("Refreshing packwiz index...")
    run_command(["packwiz", "refresh"], workspace_dir)
    print("Import complete.")

def import_modrinth_pack(mrpack_path, workspace_dir, cf_key):
    """Extracts .mrpack, parses modrinth.index.json, adds files, and copies overrides."""
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Extracting {mrpack_path}...")
        with zipfile.ZipFile(mrpack_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        index_path = os.path.join(temp_dir, "modrinth.index.json")
        if not os.path.exists(index_path):
            print("Error: Invalid .mrpack (missing modrinth.index.json)", file=sys.stderr)
            return
            
        with open(index_path, 'r', encoding='utf-8') as f:
            pack_index = json.load(f)
            
        print(f"Importing Modrinth Pack: {pack_index.get('name', 'Unknown')}")
        
        files_list = pack_index.get("files", [])
        sha512_list = []
        file_by_sha512 = {}
        for entry in files_list:
            sha512 = entry.get("hashes", {}).get("sha512")
            if sha512:
                sha512_list.append(sha512)
                file_by_sha512[sha512] = entry

        # Match files via Modrinth API
        print(f"Resolving {len(files_list)} files via Modrinth...")
        mr_matches = query_modrinth_bulk(sha512_list)
        
        # Check unmatched files for CurseForge (requires downloading them to compute Murmur2)
        remaining_files = []
        for sha512, entry in file_by_sha512.items():
            if sha512 not in mr_matches:
                remaining_files.append(entry)
                
        cf_matches = {}
        if remaining_files:
            print(f"Downloading {len(remaining_files)} unmatched files to resolve on CurseForge...")
            murmur_list = []
            murmur_to_entry = {}
            for entry in remaining_files:
                urls = entry.get("downloads", [])
                if not urls:
                    continue
                # Download file to a temp location
                try:
                    tfile = tempfile.NamedTemporaryFile(delete=False)
                    tfile.close()
                    urllib.request.urlretrieve(urls[0], tfile.name)
                    _, _, murmur = compute_hashes(tfile.name)
                    os.unlink(tfile.name)
                    murmur_list.append(murmur)
                    murmur_to_entry[murmur] = entry
                except Exception as e:
                    print(f"Failed to hash download {urls[0]}: {e}")
            if murmur_list:
                cf_matches = query_curseforge_bulk(murmur_list, cf_key)

        # Register files
        unresolved = []
        for sha512, entry in file_by_sha512.items():
            filename = os.path.basename(entry.get("path", ""))
            mr_match = mr_matches.get(sha512)
            
            # Determine CurseForge fingerprint match
            cf_match = None
            for murmur_str, entries in cf_matches.items():
                # Locate entry with matching filename or path
                for m in entries:
                    if m["file"]["fileName"] == filename:
                        cf_match = entries
                        break
                        
            # Determine side from Modrinth env info or keywords
            env_client = entry.get("env", {}).get("client", "required")
            env_server = entry.get("env", {}).get("server", "required")
            if env_client == "unsupported":
                target_side = "server"
            elif env_server == "unsupported":
                target_side = "client"
            else:
                target_side = determine_side(filename, mr_match)
                
            success = process_file_import(filename, mr_match, cf_match, target_side, workspace_dir)
            if not success:
                # Add as external URL
                urls = entry.get("downloads", [])
                if urls:
                    print(f"Adding as external URL: {filename}")
                    args = ["packwiz", "url", "add", filename, urls[0]]
                    run_command(args, workspace_dir)
                else:
                    unresolved.append(filename)

        if unresolved:
            print(f"Could not resolve the following files: {', '.join(unresolved)}")

        # Copy overrides
        for folder in ["overrides", "client-overrides", "server-overrides"]:
            src_folder = os.path.join(temp_dir, folder)
            if os.path.exists(src_folder) and os.path.isdir(src_folder):
                print(f"Copying overrides from {folder}...")
                for root, dirs, files in os.walk(src_folder):
                    rel_path = os.path.relpath(root, src_folder)
                    for f in files:
                        dest_rel = f if rel_path == "." else os.path.join(rel_path, f)
                        # Filter client/server overrides if needed
                        if folder == "client-overrides":
                            # Copy but register as client-only?
                            # Packwiz handles client/server overrides by using side ignores,
                            # for now we copy them directly to the instance root.
                            pass
                        elif folder == "server-overrides":
                            pass
                        dest_file = os.path.join(workspace_dir, dest_rel)
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        shutil.copy2(os.path.join(root, f), dest_file)
                        print(f"  Copied override: {dest_rel}")

        print("Refreshing packwiz index...")
        run_command(["packwiz", "refresh"], workspace_dir)
        print("Modrinth pack import complete.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Packwiz helper script for modpack imports")
    parser.add_argument("--source", required=True, help="Path or URL to the source modpack / directory")
    parser.add_argument("--type", choices=["curseforge", "modrinth", "raw", "auto"], default="auto", help="Import source type")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    parser.add_argument("--cf-key", default=None, help="CurseForge API Key")
    
    args = parser.parse_args()
    
    workspace_dir = os.path.abspath(args.workspace)
    cf_key = args.cf_key or os.environ.get("CF_API_KEY") or os.environ.get("CURSEFORGE_API_KEY") or DEFAULT_CF_KEY
    
    # Handle auto type detection
    import_type = args.type
    source = args.source
    
    # Check if URL
    is_url = source.startswith("http://") or source.startswith("https://")
    
    if is_url:
        print(f"Source is a URL: {source}")
        # Download first
        temp_dir = tempfile.mkdtemp()
        parsed_url = urllib.parse.urlparse(source)
        filename = os.path.basename(parsed_url.path) or "downloaded_pack.zip"
        download_path = os.path.join(temp_dir, filename)
        print(f"Downloading to temporary file {download_path}...")
        try:
            urllib.request.urlretrieve(source, download_path)
            source = download_path
        except Exception as e:
            print(f"Failed to download source URL: {e}", file=sys.stderr)
            sys.exit(1)
            
    if import_type == "auto":
        if os.path.isdir(source):
            import_type = "raw"
        elif source.endswith(".mrpack"):
            import_type = "modrinth"
        elif source.endswith(".zip"):
            # Could be CurseForge pack or Prism Launcher zip.
            # Inspect ZIP structure
            try:
                with zipfile.ZipFile(source, 'r') as zip_ref:
                    names = zip_ref.namelist()
                    if "modrinth.index.json" in names:
                        import_type = "modrinth"
                    elif "manifest.json" in names:
                        import_type = "curseforge"
                    elif any("instance.cfg" in n or ".minecraft/" in n or "minecraft/" in n for n in names):
                        import_type = "raw"
                    else:
                        # Default fallback
                        import_type = "curseforge"
            except Exception as e:
                print(f"Failed to read ZIP structure: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Could not auto-detect source type. Defaulting to raw.", file=sys.stderr)
            import_type = "raw"
            
    print(f"Resolved Import Type: {import_type.upper()}")
    
    if import_type == "curseforge":
        print(f"Importing CurseForge zip from {source}...")
        args_cf = ["packwiz", "-y", "curseforge", "import", source]
        run_command(args_cf, workspace_dir)
        print("Refreshing packwiz index...")
        run_command(["packwiz", "refresh"], workspace_dir)
    elif import_type == "modrinth":
        import_modrinth_pack(source, workspace_dir, cf_key)
    elif import_type == "raw":
        if zipfile.is_zipfile(source):
            # Extract to temp dir
            with tempfile.TemporaryDirectory() as extract_dir:
                print(f"Extracting raw zip archive {source}...")
                with zipfile.ZipFile(source, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                import_raw_files(extract_dir, workspace_dir, cf_key)
        else:
            import_raw_files(source, workspace_dir, cf_key)
            
    # Clean up temp downloads if URL was used
    if is_url:
        shutil.rmtree(os.path.dirname(source), ignore_errors=True)

if __name__ == "__main__":
    main()
