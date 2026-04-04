#!/bin/bash
for f in mods/*.toml; do
  url=$(grep '^url =' "$f" | sed 's/url = "//;s/"$//')
  
  # Extract Modrinth project ID from URL
  if [[ "$url" =~ cdn.modrinth.com/data/([^/]+) ]]; then
    project_id="${BASH_REMATCH[1]}"
    
    # Query Modrinth API
    response=$(curl -s "https://api.modrinth.com/v2/project/$project_id")
    
    # Extract client_side and server_side
    client_side=$(echo "$response" | grep -o '"client_side":"[^"]*"' | head -1 | cut -d'"' -f4)
    server_side=$(echo "$response" | grep -o '"server_side":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    echo "$f: client=$client_side server=$server_side"
    
    # Determine the side value
    if [ "$client_side" = "required" ] && [ "$server_side" = "required" ]; then
      side="both"
    elif [ "$client_side" = "required" ]; then
      side="client"
    elif [ "$server_side" = "required" ]; then
      side="server"
    else
      side="both"
    fi
    
    # Update the file
    if grep -q "^side = " "$f"; then
      sed -i "s/^side = .*/side = \"$side\"/" "$f"
    else
      # Add side after filename line
      sed -i "/^filename = /a side = \"$side\"" "$f"
    fi
  else
    echo "$f: Non-Modrinth URL ($url)"
  fi
  
  sleep 0.1  # Rate limiting
done
