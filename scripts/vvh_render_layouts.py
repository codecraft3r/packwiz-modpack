#!/usr/bin/env python3
"""Deterministic source-level VvH layout diagnostics (not client screenshots)."""
from __future__ import annotations
import argparse, hashlib, io, itertools, json, math, re, zipfile
from pathlib import Path
from typing import Any, Iterable
from PIL import Image, ImageDraw, ImageFont
try:
    from vvh_validate import parse_snbt
except ImportError:  # pragma: no cover
    from scripts.vvh_validate import parse_snbt

COLORS = {"VvH 00": (154,119,70), "VvH 01": (130,130,130), "VvH 02": (130,35,55),
          "VvH 03": (55,95,135), "VvH 04": (80,120,75), "VvH 05": (145,100,45),
          "VvH 06": (95,85,70), "VvH 07": (115,50,100), "VvH 08": (170,120,35), "VvH 09": (80,105,95)}
SHAPES = {"circle", "square", "diamond", "hexagon", "octagon", "gear", "star"}

def clean(value: Any) -> str: return re.sub(r"&.", "", str(value or ""))
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()

def read_snbt(path: Path):
    """Parse through the campaign validator so malformed source fails closed."""
    return parse_snbt(path)
def normalize_quest(q: dict[str, Any]) -> dict[str, Any]:
    q = dict(q); q.setdefault("id", ""); q.setdefault("title", q.get("id", "Untitled")); q.setdefault("x", 0); q.setdefault("y", 0)
    q.setdefault("size", 1.0); q.setdefault("shape", ""); q.setdefault("dependencies", []); q.setdefault("optional", False)
    q.setdefault("hide_dependency_lines", None); q.setdefault("icon", {})
    if isinstance(q["icon"], dict): q["icon"] = q["icon"].get("id", "")
    return q
def chapters_from_root(root: Path) -> dict[str, Any]:
    root = root.resolve(); chapter_dir = root / "chapters" if (root / "chapters").is_dir() else root
    chapters = []
    for path in sorted(chapter_dir.glob("*.snbt")):
        value = read_snbt(path)
        if not isinstance(value, dict) or not value.get("quests"): continue
        value.setdefault("filename", path.stem); value.setdefault("title", path.stem); value.setdefault("default_hide_dependency_lines", False); value.setdefault("images", [])
        value["quests"] = [normalize_quest(q) for q in value.get("quests", []) if isinstance(q, dict)]; chapters.append(value)
    data_path = root / "data.snbt"; data = read_snbt(data_path) if data_path.exists() else {}
    return {"architecture": "actual-snbt", "source_root": str(root), "data": data, "chapters": chapters}
def normalize_manifest(m: dict[str, Any]) -> dict[str, Any]:
    m = dict(m); default_shape = (m.get("data") or {}).get("default_quest_shape", "circle")
    for ch in m.get("chapters", []):
        ch.setdefault("default_hide_dependency_lines", False); ch.setdefault("images", []); ch["quests"] = [normalize_quest(q) for q in ch.get("quests", [])]
        for q in ch["quests"]:
            if not q.get("shape"): q["shape"] = default_shape
    return m
def load_resource_images(paths: Iterable[Path]):
    images, models, sources = {}, {}, []
    for path in paths:
        path = path.resolve(); sources.append({"path": str(path), "sha256": sha256(path)})
        try:
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    match = re.fullmatch(r"assets/([^/]+)/(textures/.+?\.png)", name)
                    if name.startswith("assets/") and "/models/" in name and name.endswith(".json"):
                        try:
                            models[name] = json.loads(z.read(name).decode("utf-8"))
                        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                            pass
                    if match:
                        key = f"{match.group(1)}:{match.group(2)}"
                        try: images[key] = Image.open(io.BytesIO(z.read(name))).convert("RGBA")
                        except OSError: pass
        except (OSError, zipfile.BadZipFile): pass
    return images, models, sources
def icon_keys(item: str):
    if not item or ":" not in item: return []
    ns, name = item.split(":", 1); return [f"{ns}:textures/item/{name}.png", f"{ns}:textures/block/{name}.png"]
def model_texture_keys(item: str, models: dict[str, dict[str, Any]], seen: set[str] | None = None):
    """Resolve item/block model layer0/all/particle references to texture keys."""
    if not item or ":" not in item:
        return []
    namespace, path = item.split(":", 1)
    seen = set() if seen is None else seen
    result = []
    for kind in ("item", "block"):
        model_key = f"assets/{namespace}/models/{kind}/{path}.json"
        if model_key in seen:
            continue
        seen.add(model_key)
        model = models.get(model_key)
        if not model:
            continue
        textures = model.get("textures", {})
        refs = [textures.get("layer0"), textures.get("all"), textures.get("particle")]
        for ref in refs:
            if not ref:
                continue
            if ref.startswith("#"):
                ref = textures.get(ref[1:], "")
            if not ref:
                continue
            if ":" not in ref:
                ref = f"{namespace}:{ref}"
            ref_ns, ref_path = ref.split(":", 1)
            if ref_path.startswith("textures/"):
                ref_path = ref_path[len("textures/"):]
            if not ref_path.endswith(".png"):
                ref_path += ".png"
            result.append(f"{ref_ns}:textures/{ref_path}")
        parent = model.get("parent")
        if parent and parent not in {"builtin/generated", "builtin/entity"}:
            if ":" in parent:
                parent_ns, parent_path = parent.split(":", 1)
            else:
                parent_ns, parent_path = namespace, parent
            parent_item = f"{parent_ns}:{parent_path.removeprefix('item/').removeprefix('block/')}"
            result.extend(model_texture_keys(parent_item, models, seen))
    return result
def resolve_icon_source(item: str, images: dict[str, Image.Image], models: dict[str, dict[str, Any]]):
    for key in icon_keys(item) + model_texture_keys(item, models):
        if key in images:
            return images[key]
    return None
def paste_contained(canvas, source, center, box, alpha=255):
    source = source.convert("RGBA")
    ratio = min(box[0] / max(1, source.width), box[1] / max(1, source.height))
    target = (max(1, round(source.width * ratio)), max(1, round(source.height * ratio)))
    layer = source.resize(target, Image.Resampling.NEAREST)
    if alpha < 255: layer.putalpha(layer.getchannel("A").point(lambda v: v * alpha // 255))
    canvas.alpha_composite(layer, (round(center[0]-layer.width/2), round(center[1]-layer.height/2)))
def font(size: int, bold=False):
    for path in (Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")):
        if path.exists(): return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()
def shape_points(shape, center, radius):
    if shape == "circle": return None
    n = {"square":4,"diamond":4,"hexagon":6,"octagon":8,"star":10,"gear":16}.get(shape,8); start = -math.pi/4 if shape == "square" else (-math.pi/2 if shape in {"diamond","star","gear"} else 0)
    out=[]
    for i in range(n):
        r = radius * (0.68 if shape == "gear" and i%2 else (0.48 if shape == "star" and i%2 else 1.0)); a=start+i*2*math.pi/n; out.append((center[0]+math.cos(a)*r, center[1]+math.sin(a)*r))
    return out
def effective_hidden(ch, q):
    return bool(q.get("hide_dependency_lines")) if q.get("hide_dependency_lines") is not None else bool(ch.get("default_hide_dependency_lines", False))
def orient(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def segments_cross(e1,e2):
    a,b=e1; c,d=e2
    if a in (c,d) or b in (c,d): return False
    return orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0
def chapter_viewport(ch, detail=False, canvas_size=None):
    """Return one centered coordinate transform shared by boards and metrics."""
    quests = ch.get("quests", [])
    xs = [float(q.get("x", 0)) for q in quests] or [0]
    ys = [float(q.get("y", 0)) for q in quests] or [0]
    xmin, xmax = min(xs) - 3, max(xs) + 3
    ymin, ymax = min(ys) - 3, max(ys) + 3
    # Chapter art is part of the authored composition, not disposable overflow.
    # Include its complete rotated rectangle with a small frame margin.
    for art in ch.get("images", []) or []:
        x, y = float(art.get("x", 0)), float(art.get("y", 0))
        w, h = float(art.get("width", 1)), float(art.get("height", 1))
        angle = math.radians(float(art.get("rotation", 0)))
        half_w = (abs(w * math.cos(angle)) + abs(h * math.sin(angle))) / 2
        half_h = (abs(w * math.sin(angle)) + abs(h * math.cos(angle))) / 2
        xmin, xmax = min(xmin, x-half_w-0.75), max(xmax, x+half_w+0.75)
        ymin, ymax = min(ymin, y-half_h-0.75), max(ymax, y+half_h+0.75)
    if canvas_size:
        width, height = canvas_size
        margin = round(min(width, height) * 0.096)
        header = round(height * 0.061)
    else:
        width, height = (2400, 1550) if detail else (1800, 1150)
        margin = 145 if detail else 110
        header = 70
    scale = min((width - 2 * margin) / (xmax - xmin or 1),
                (height - 2 * margin - header) / (ymax - ymin or 1))
    graph_width = (xmax - xmin) * scale
    graph_height = (ymax - ymin) * scale
    origin_x = (width - graph_width) / 2
    origin_y = header + (height - header - graph_height) / 2
    def point(x, y):
        return origin_x + (x - xmin) * scale, origin_y + (y - ymin) * scale
    return width, height, scale, point
def estimated_label_collisions(ch):
    """Estimate overlaps using the natural above-node placement before routing."""
    quests = ch.get("quests", [])
    if not quests:
        return 0
    width, height, _scale, point = chapter_viewport(ch, detail=False)

    draw = ImageDraw.Draw(Image.new("RGB", (2, 2)))
    label_font = font(18)
    labels, nodes = [], []
    for quest in quests:
        center = point(float(quest.get("x", 0)), float(quest.get("y", 0)))
        radius = 29.0 * float(quest.get("size", 1.0))
        lines = wrap_lines(quest.get("title", quest.get("id", "")), draw,
                           label_font, max(150, min(260, int(radius * 4.2))))
        label_width = max((draw.textbbox((0, 0), line, font=label_font)[2]
                           for line in lines), default=30) + 18
        label_height = len(lines) * (label_font.size + 3) + 12
        labels.append((center[0] - label_width / 2,
                       center[1] - radius - label_height - 9,
                       center[0] + label_width / 2,
                       center[1] - radius - 9))
        nodes.append((center[0] - radius - 5, center[1] - radius - 5,
                      center[0] + radius + 5, center[1] + radius + 5))

    def overlap(a, b):
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    label_pairs = sum(overlap(a, b) for a, b in itertools.combinations(labels, 2))
    label_nodes = sum(overlap(label, node) for label in labels for node in nodes)
    return label_pairs + label_nodes
def graph_metrics(ch):
    qs=ch.get("quests",[]); by={q.get("id"):q for q in qs}; pos={q.get("id"):(float(q.get("x",0)),float(q.get("y",0))) for q in qs}; overlaps=0; spacing=[]
    for a,b in itertools.combinations(qs,2):
        d=math.dist(pos[a["id"]],pos[b["id"]]); spacing.append(d)
        if d < (float(a.get("size",1))+float(b.get("size",1)))*.75: overlaps+=1
    edges=[]; hidden=missing=0
    for q in qs:
        for dep in q.get("dependencies",[]) or []:
            if dep not in by: missing+=1; continue
            if effective_hidden(ch,q): hidden+=1
            else: edges.append((pos[dep],pos[q["id"]]))
    adjacency={q.get("id"):set() for q in qs}
    for q in qs:
        for dep in q.get("dependencies",[]) or []:
            if dep in adjacency: adjacency[q["id"]].add(dep); adjacency[dep].add(q["id"])
    comps=0; unseen=set(adjacency)
    while unseen:
        comps+=1; stack=[unseen.pop()]
        while stack:
            for nxt in adjacency[stack.pop()] & unseen: unseen.remove(nxt); stack.append(nxt)
    xs=[p[0] for p in pos.values()]; spine=sum(xs)/len(xs) if xs else 0; align=math.sqrt(sum((x-spine)**2 for x in xs)/len(xs)) if xs else 0
    core_xs=[float(q.get("x",0)) for q in qs if not q.get("optional")]
    core_spine=round(sum(core_xs)/len(core_xs),3) if core_xs else None
    core_align=round(math.sqrt(sum((x-(core_spine or 0))**2 for x in core_xs)/len(core_xs)),3) if core_xs else None
    lens=[math.dist(a,b) for a,b in edges]; cluster={"left_right_gap":None}
    if "market" in str(ch.get("filename","")).lower() or str(ch.get("title","")).startswith("05"):
        left=[x for x in xs if x < -1]; right=[x for x in xs if x > 1]; cluster["left_right_gap"]=round(min(right)-max(left),3) if left and right else None
    return {"node_overlaps":overlaps,"estimated_label_collisions":estimated_label_collisions(ch),"visible_edge_crossings":sum(segments_cross(a,b) for a,b in itertools.combinations(edges,2)),"visible_edge_count":len(edges),"hidden_dependency_edges":hidden,"missing_dependency_nodes":missing,"edge_lengths":{"count":len(lens),"mean":round(sum(lens)/len(lens),3) if lens else 0,"max":round(max(lens,default=0),3)},"node_spacing":{"mean":round(sum(spacing)/len(spacing),3) if spacing else 0,"min":round(min(spacing),3) if spacing else 0},"cluster_separation":cluster,"spine_alignment":{"core_x":core_spine,"core_rms":core_align,"all_nodes_rms":round(align,3)},"spine_alignment_rms":round(align,3),"disconnected_components":comps}
def wrap_lines(text, draw, fnt, max_width):
    lines=[]; cur=""
    for word in clean(text).split() or ["Untitled"]:
        candidate=f"{cur} {word}".strip()
        if cur and draw.textbbox((0,0),candidate,font=fnt)[2] > max_width: lines.append(cur); cur=word
        else: cur=candidate
    if cur: lines.append(cur)
    return lines
def label_box(q, center, radius, draw, fnt, occupied, canvas_size):
    lines=wrap_lines(q.get("title",q.get("id","")),draw,fnt,max(150,min(260,int(radius*4.2)))); w=max((draw.textbbox((0,0),s,font=fnt)[2] for s in lines),default=30)+18; h=len(lines)*(fnt.size+3)+12; x,y=center
    candidates=[(0,-radius-h/2-9),(0,radius+h/2+9),(-radius-w/2-12,0),(radius+w/2+12,0),(-radius-w/2,-radius-h/2),(radius+w/2,-radius-h/2),(-radius-w/2,radius+h/2),(radius+w/2,radius+h/2)]
    def box(dx,dy): return (x+dx-w/2,y+dy-h/2,x+dx+w/2,y+dy+h/2)
    def bad(b): return any(not (b[2]+3<o[0] or b[0]-3>o[2] or b[3]+3<o[1] or b[1]-3>o[3]) for o in occupied)
    chosen=next((box(dx,dy) for dx,dy in candidates if not bad(box(dx,dy))),box(*candidates[0])); clipped=chosen[0]<4 or chosen[1]<42 or chosen[2]>canvas_size[0]-4 or chosen[3]>canvas_size[1]-4; occupied.append(chosen); return chosen,lines,int(clipped)
def render_chapter(ch,images,models,unresolved,unresolved_icons,out,index,detail=False,orthogonal=False):
    qs=ch.get("quests",[]); W,H,scale,pt=chapter_viewport(ch, detail=detail)
    base=next((v for k,v in COLORS.items() if str(ch.get("title","")).startswith(k)),(80,90,105)); img=Image.new("RGBA",(W,H),(21,24,30,255)); draw=ImageDraw.Draw(img); title_font=font(28 if detail else 23,True); lf=font(22 if detail else 18); tiny=font(16)
    draw.text((28,20),f"SOURCE-LEVEL DIAGNOSTIC · {ch.get('title',ch.get('filename','chapter'))}",fill=(248,243,226),font=title_font); draw.text((28,55),"Stored coordinates and visibility; not a Minecraft client screenshot.",fill=(240,175,96),font=tiny)
    for art in sorted(ch.get("images",[]) or [],key=lambda v:v.get("order",0)):
        key=art.get("image",""); center=pt(float(art.get("x",0)),float(art.get("y",0))); source=images.get(key); w=max(40,round(float(art.get("width",1))*scale)); h=max(40,round(float(art.get("height",1))*scale))
        if source is None:
            unresolved.add(key); layer=Image.new("RGBA",(w,h),(70,73,85,38)); ImageDraw.Draw(layer).rectangle((0,0,w-1,h-1),outline=(164,157,150,95),width=2); img.alpha_composite(layer,(round(center[0]-w/2),round(center[1]-h/2))); draw=ImageDraw.Draw(img); draw.text((center[0]-w/2+6,center[1]-8),"MISSING ART",fill=(226,181,130,185),font=tiny)
        else: paste_contained(img,source,center,(w,h),int(art.get("alpha",255)))
    draw=ImageDraw.Draw(img); by={q.get("id"):q for q in qs}; pos={q.get("id"):pt(float(q.get("x",0)),float(q.get("y",0))) for q in qs}
    for q in qs:
        if effective_hidden(ch,q): continue
        for dep in q.get("dependencies",[]) or []:
            if dep in by:
                start,end=pos[dep],pos[q["id"]]
                if orthogonal:
                    mid=((start[0]+end[0])/2,start[1]); draw.line((*start,*mid),fill=(177,148,103,215),width=4 if detail else 3); draw.line((*mid,*end),fill=(177,148,103,215),width=4 if detail else 3)
                else: draw.line((*start,*end),fill=(120,132,149,210),width=4 if detail else 3)
    # Reserve node footprints as well as earlier labels so a title cannot be
    # placed over a neighbouring quest marker in a dense branch.
    occupied=[]
    for q in qs:
        c=pos[q["id"]]; r=29.*float(q.get("size",1.)); occupied.append((c[0]-r-5,c[1]-r-5,c[0]+r+5,c[1]+r+5))
    collisions=0
    for q in qs:
        center=pos[q["id"]]; radius=29.*float(q.get("size",1.)); shape=clean(q.get("shape")) or clean(ch.get("default_quest_shape")) or "circle"; shape=shape if shape in SHAPES else "circle"; fill=tuple(min(255,int(c*1.08)) for c in base); outline=(247,220,125) if not q.get("optional") else (170,185,200); points=shape_points(shape,center,radius)
        if points is None: draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),fill=fill,outline=outline,width=4)
        else: draw.polygon(points,fill=fill,outline=outline); draw.line(points+[points[0]],fill=outline,width=4,joint="curve")
        icon=clean(q.get("icon")); src=resolve_icon_source(icon, images, models)
        if src: paste_contained(img,src,center,(round(radius*1.1),round(radius*1.1)),235)
        else:
            if icon: unresolved_icons.add(icon)
        suffix = clean(q.get("id", ""))[-4:]
        suffix_width = draw.textbbox((0,0), suffix, font=tiny)[2]
        draw.text((center[0]-suffix_width/2, center[1]+radius*.35), suffix, fill=(250,250,250), font=tiny)
        if q.get("min_required_dependencies"): draw.text((center[0]-radius,center[1]+radius+5),f"{q['min_required_dependencies']}/{len(q.get('dependencies',[]))}",fill=(255,220,130),font=tiny)
        box,lines,clipped=label_box(q,center,radius,draw,lf,occupied,(W,H)); collisions+=clipped; draw.rounded_rectangle(box,radius=8,fill=(12,15,21,225),outline=(177,190,203,165),width=1); yy=box[1]+6
        for line in lines:
            tw=draw.textbbox((0,0),line,font=lf)[2]; draw.text(((box[0]+box[2]-tw)/2,yy),line,fill=(250,249,241),font=lf); yy+=lf.size+3
    metrics=graph_metrics(ch); metrics["review_label_clipping"]=collisions; suffix="_detail" if detail else ""; route="_orthogonal" if orthogonal else ""; path=out/f"{index:02d}_{ch.get('filename',f'chapter_{index}')}{route}{suffix}.png"; img.convert("RGB").save(path,optimize=True); return path,metrics
def dense_crops(ch,overview,out,index,orthogonal=False):
    qs=ch.get("quests",[]); dense=[q for a,b in itertools.combinations(qs,2) if math.dist((float(a.get("x",0)),float(a.get("y",0))),(float(b.get("x",0)),float(b.get("y",0))))<4 for q in (a,b)]
    if not dense: return []
    source=Image.open(overview); _w,_h,_scale,point=chapter_viewport(ch, canvas_size=(source.width,source.height)); centers=[point(float(q.get("x",0)),float(q.get("y",0))) for q in dense]; cx=sum(p[0] for p in centers)/len(centers); cy=sum(p[1] for p in centers)/len(centers); size=620; box=(max(0,int(cx-size/2)),max(70,int(cy-size/2)),min(source.width,int(cx+size/2)),min(source.height,int(cy+size/2))); route="_orthogonal" if orthogonal else ""; path=out/f"{index:02d}_{ch.get('filename',f'chapter_{index}')}{route}_dense_01.png"; source.crop(box).save(path,optimize=True); return [path.name]
def render_set(manifest, out, images, models, unresolved, unresolved_icons, orthogonal=False):
    paths=[]; metrics={}
    for i,ch in enumerate(manifest.get("chapters",[])):
        overview,values=render_chapter(ch,images,models,unresolved,unresolved_icons,out,i,False,orthogonal); detail,detail_values=render_chapter(ch,images,models,unresolved,unresolved_icons,out,i,True,orthogonal); paths.extend([overview.name,detail.name]); paths.extend(dense_crops(ch,overview,out,i,orthogonal)); metrics[ch.get("filename",str(i))]={"overview":values,"detail":detail_values}
    return paths,metrics
def main(argv=None):
    ap=argparse.ArgumentParser(description="Render source-level VvH layout diagnostics, not client screenshots."); ap.add_argument("manifest",type=Path); ap.add_argument("out",type=Path); ap.add_argument("--resource-zip",action="append",default=[],type=Path); ap.add_argument("--metadata-out",type=Path); ap.add_argument("--baseline-root",type=Path); ap.add_argument("--live-root",type=Path); ap.add_argument("--edge-view",choices=("source-faithful","orthogonal","both"),default="source-faithful",help="Stored straight edges, optional Manhattan diagnostic, or both."); args=ap.parse_args(argv); args.out.mkdir(parents=True,exist_ok=True)
    current=normalize_manifest(json.loads(args.manifest.read_text(encoding="utf-8"))); imgs,models,sources=load_resource_images(args.resource_zip); unresolved=set(); unresolved_icons=set(); outputs=[]; after={};
    if args.edge_view in {"source-faithful","both"}: outputs,after=render_set(current,args.out,imgs,models,unresolved,unresolved_icons,False)
    if args.edge_view in {"orthogonal","both"}: orth_outputs,orth_after=render_set(current,args.out,imgs,models,unresolved,unresolved_icons,True); outputs.extend(orth_outputs); after["_orthogonal"] = orth_after
    before=live=None; bp=lp=None
    if args.baseline_root:
        base=chapters_from_root(args.baseline_root); before={ch.get("filename",str(i)):graph_metrics(ch) for i,ch in enumerate(base["chapters"])}; bp={"root":str(args.baseline_root.resolve()),"files":[{"path":str(p.resolve()),"sha256":sha256(p)} for p in sorted((args.baseline_root/"chapters").glob("*.snbt"))]}
    if args.live_root:
        current_live=chapters_from_root(args.live_root); live={ch.get("filename",str(i)):graph_metrics(ch) for i,ch in enumerate(current_live["chapters"])}; lp={"root":str(args.live_root.resolve()),"files":[{"path":str(p.resolve()),"sha256":sha256(p)} for p in sorted((args.live_root/"chapters").glob("*.snbt"))]}
    over=[p for p in sorted(args.out.glob("[0-9][0-9]_*.png")) if "_detail" not in p.stem and "_dense_" not in p.stem and "_orthogonal" not in p.stem]; thumbs=[]
    for p in over: im=Image.open(p); im.thumbnail((600,390)); thumbs.append((p,im.copy()))
    sheet=Image.new("RGB",(1200,max(430,math.ceil(len(thumbs)/2)*430)),(15,17,22)); sd=ImageDraw.Draw(sheet); sf=font(17,True)
    for i,(p,im) in enumerate(thumbs): x,y=(i%2)*600,(i//2)*430; sheet.paste(im,(x,y+31)); sd.text((x+8,y+8),p.stem,fill=(240,240,240),font=sf)
    sheet.save(args.out/"contact_sheet.png",optimize=True); outputs.append("contact_sheet.png")
    unresolved_list=sorted(x for x in unresolved if x)
    shape_warnings=[f"unsupported quest shape {q.get('shape')!r} for {q.get('id')} (rendered as circle)" for ch in current.get("chapters",[]) for q in ch.get("quests",[]) if q.get("shape") and q.get("shape") not in SHAPES]
    unresolved_icon_list=sorted(unresolved_icons)
    warnings=[f"background art unresolved: {key}" for key in unresolved_list]+shape_warnings+[f"quest icon unresolved: {key}" for key in unresolved_icon_list]
    meta={"artifact_type":"source-level diagnostic; not runtime or in-client evidence","edge_views":{"default":"source-faithful stored geometry","requested":args.edge_view,"orthogonal":"Manhattan diagnostic routes are explicitly suffixed _orthogonal; source-faithful remains authoritative"},"manifest":{"path":str(args.manifest.resolve()),"sha256":sha256(args.manifest)},"resource_sources":sources,"resolved_resource_images":sorted(imgs),"model_reference_count":len(models),"unresolved_references":unresolved_list,"unresolved_icon_references":unresolved_icon_list,"warnings":warnings,"outputs":sorted(set(outputs+[p.name for p in args.out.glob("*.png")])),"metrics":{"after":after,"before":before,"live":live},"baseline_provenance":bp,"live_provenance":lp}; target=args.metadata_out or args.out/"render-metadata.json"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(meta,indent=2,ensure_ascii=False)); return 0
if __name__ == "__main__": raise SystemExit(main())
