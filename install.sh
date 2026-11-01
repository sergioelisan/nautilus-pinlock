#!/usr/bin/env bash
# Instala a extensão PinLock para o Nautilus (no usuário atual).
set -euo pipefail
cd "$(dirname "$0")"

missing=()
command -v gocryptfs >/dev/null || missing+=(gocryptfs)
command -v zenity    >/dev/null || missing+=(zenity)
python3 -c 'import gi; gi.require_version("Nautilus","4.1")' 2>/dev/null \
  || python3 -c 'import gi; gi.require_version("Nautilus","4.0")' 2>/dev/null \
  || missing+=(python3-nautilus)
if ((${#missing[@]})); then
  echo "Instalando dependências: ${missing[*]}"
  sudo apt install -y "${missing[@]}"
fi

DATA="$HOME/.local/share/pinlock"
install -Dm755 pinlock-helper       "$DATA/pinlock-helper"
install -Dm644 folder-locked.svg    "$DATA/folder-locked.svg"
install -Dm644 pinlock_extension.py "$HOME/.local/share/nautilus-python/extensions/pinlock_extension.py"

# Ao entrar na sessão, devolve o nome original a pastas que ficaram abertas.
install -Dm644 /dev/stdin "$HOME/.config/autostart/pinlock-repair.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=PinLock (reparo)
Exec=$DATA/pinlock-helper repair
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF

nautilus -q 2>/dev/null || true
echo "PinLock instalado. Abra o Nautilus e clique com o botão direito em uma pasta."
