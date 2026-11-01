#!/usr/bin/env bash
# Remove a extensão. Pastas protegidas continuam cifradas e intactas
# (podem ser abertas manualmente com: gocryptfs PASTA PONTO_DE_MONTAGEM).
set -euo pipefail
rm -f  "$HOME/.local/share/nautilus-python/extensions/pinlock_extension.py"
rm -f  "$HOME/.config/autostart/pinlock-repair.desktop"
rm -rf "$HOME/.local/share/pinlock"
nautilus -q 2>/dev/null || true
echo "PinLock removido."
