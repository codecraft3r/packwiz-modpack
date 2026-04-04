#!/bin/bash
MAX_JOBS=8

get_side() {
  local file="$1"
  local url=$(grep '^url =' "$file" | sed 's/url = "//;s/"$//')
  
  if [[ "$url" =~ cdn.modrinth.com/data/([^/]+) ]]; then
    local project_id="${BASH_REMATCH[1]}"
    local response=$(curl -s "https://api.modrinth.com/v2/project/$project_id" 2>/dev/null)
    local client_side=$(echo "$response" | grep -o '"client_side":"[^"]*"' | head -1 | cut -d'"' -f4)
    local server_side=$(echo "$response" | grep -o '"server_side":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    local side="both"
    if [ "$client_side" = "required" ] && [ "$server_side" = "unsupported" ]; then
      side="client"
    elif [ "$server_side" = "required" ] && [ "$client_side" = "unsupported" ]; then
      side="server"
    elif [ "$client_side" = "required" ] && [ "$server_side" = "required" ]; then
      side="both"
    elif [ "$client_side" = "optional" ] && [ "$server_side" = "unsupported" ]; then
      side="client"
    elif [ "$server_side" = "optional" ] && [ "$client_side" = "unsupported" ]; then
      side="server"
    fi
    
    echo "$file|$side"
  else
    echo "$file|both"
  fi
}
export -f get_side

# Process files in parallel
find mods -name '*.toml' | xargs -P$MAX_JOBS -I{} bash -c 'get_side "$0"' {} | while IFS='|' read -r file side; do
  if grep -q "^side = " "$file"; then
    sed -i "s/^side = .*/side = \"$side\"/" "$file"
  else
    sed -i "/^filename = /a side = \"$side\"" "$file"
  fi
  echo "Updated $file -> $side"
done
