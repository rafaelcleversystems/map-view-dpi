#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$#" -gt 0 ]; then
  exec python3 scripts/serve.py --port "$1"
fi
if command -v open >/dev/null 2>&1; then open index.html; elif command -v xdg-open >/dev/null 2>&1; then xdg-open index.html; else printf "%s\n" "Abra o arquivo index.html no navegador."; fi
