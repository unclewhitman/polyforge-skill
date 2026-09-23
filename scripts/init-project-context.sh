#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ROUTER="$SKILL_ROOT/config/model-router.toml"
TEMPLATE="$SKILL_ROOT/templates/project-context.md"
project_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

read_cfg() {
  local section="$1" key="$2"
  awk -v sec="$section" -v key="$key" '
    BEGIN { insec=0 }
    /^[[:space:]]*\[/ { line=$0; gsub(/[[:space:]]/, "", line); insec=(line=="[" sec "]"); next }
    insec {
      line=$0; sub(/#.*/, "", line)
      if (line ~ "^[[:space:]]*" key "[[:space:]]*=") {
        sub("^[[:space:]]*" key "[[:space:]]*=[[:space:]]*", "", line)
        gsub(/^[\" ]+|[\" ]+$/, "", line); print line; exit
      }
    }
  ' "$ROUTER"
}

validate_rel_path() {
  local p="$1"
  [[ -n "$p" ]] || return 1
  case "$p" in
    /*|~*|..|../*|*/..|*/../*) return 1 ;;
  esac
  [[ "$p" != *$'\n'* && "$p" != *$'\r'* ]]
}

ctx_rel="$(read_cfg project_context path)"
[[ -n "$ctx_rel" ]] || ctx_rel=".polyforge/project-context.md"
validate_rel_path "$ctx_rel" || { echo "[x] project_context.path must be a safe path inside the project: $ctx_rel" >&2; exit 2; }

legacy_rel="$(read_cfg project_context legacy_path)"
if [[ -n "$legacy_rel" ]]; then validate_rel_path "$legacy_rel" || legacy_rel=""; fi

ctx="$project_root/$ctx_rel"
mkdir -p "$(dirname "$ctx")"

migrate="$(read_cfg project_context auto_migrate_legacy)"
if [[ ! -f "$ctx" && "$migrate" == "true" && -n "$legacy_rel" && -f "$project_root/$legacy_rel" ]]; then
  cp "$project_root/$legacy_rel" "$ctx"
  sed -i.bak '1s/.*/# PolyForge Project Context/' "$ctx" 2>/dev/null || true
  rm -f "$ctx.bak"
  echo "migrated: $legacy_rel -> $ctx_rel"
fi

if [[ ! -f "$ctx" ]]; then
  ts="$(date '+%Y-%m-%d %H:%M:%S%z')"
  sed -e "s|{{TIMESTAMP}}|$ts|g" -e "s|{{PROJECT_ROOT}}|$project_root|g" "$TEMPLATE" > "$ctx"
  echo "created: $ctx"
else
  echo "exists: $ctx"
fi

exclude="$(read_cfg project_context exclude_from_git)"
if [[ "$exclude" == "true" ]] && git -C "$project_root" rev-parse --git-dir >/dev/null 2>&1; then
  exclude_file="$(git -C "$project_root" rev-parse --git-path info/exclude)"
  mkdir -p "$(dirname "$exclude_file")"; touch "$exclude_file"
  pattern="/$ctx_rel"
  if ! grep -qxF "$pattern" "$exclude_file"; then
    printf '\n%s\n' "$pattern" >> "$exclude_file"
    echo "git-local-exclude: $pattern"
  fi
fi

printf '%s\n' "$ctx"
