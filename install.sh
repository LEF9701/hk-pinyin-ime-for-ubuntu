#!/usr/bin/env bash
# 港式拼音 HK Pinyin — installer for Ubuntu / Debian (fcitx5 + Rime)
#
#   ./install.sh                 install for the current user
#   ./install.sh --no-apt        skip package installation
#   ./install.sh --layout gb     keyboard layout for the English source (default: detected, else us)
#   ./install.sh --no-config     only install the Rime schema and themes; leave fcitx5 settings alone
#
# Run as your normal user (not with sudo); it asks for sudo only for apt.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RIME_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/rime"
THEME_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/themes"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/fcitx5"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$CONF_DIR/hk-pinyin-backup-$STAMP"
MANIFEST="$RIME_DIR/.hk_pinyin_manifest"

DO_APT=1
DO_CONFIG=1
LAYOUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --no-apt) DO_APT=0 ;;
    --no-config) DO_CONFIG=0 ;;
    --layout) LAYOUT="${2:?--layout needs a value}"; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

say()  { printf '\033[1;34m▸\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -ne 0 ] || die "Run this as your normal user, not root. It will call sudo for apt."

backup() {  # backup <file>
  if [ -e "$1" ]; then
    mkdir -p "$BACKUP"
    cp -a "$1" "$BACKUP/$(echo "${1#$HOME/}" | tr '/' '_')"
  fi
}

# ── 1. packages ──────────────────────────────────────────────────────
pkg_available() { apt-cache show "$1" >/dev/null 2>&1; }

if [ "$DO_APT" -eq 1 ]; then
  command -v apt-get >/dev/null || die "apt-get not found. Use --no-apt and install fcitx5 + fcitx5-rime yourself."
  say "Installing packages (sudo password may be asked)…"
  sudo apt-get update -qq
  PKGS=(fcitx5 fcitx5-rime fcitx5-config-qt fcitx5-frontend-gtk3 fcitx5-frontend-qt5
        rime-data-luna-pinyin librime-bin im-config fonts-noto-cjk)
  for p in fcitx5-frontend-gtk4 fcitx5-frontend-qt6 librime-plugin-lua; do
    pkg_available "$p" && PKGS+=("$p")
  done
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "${PKGS[@]}"
  ok "Packages installed"
fi

command -v fcitx5 >/dev/null || die "fcitx5 is not installed."
[ -f /usr/share/rime-data/luna_pinyin.dict.yaml ] || die "rime-data-luna-pinyin is missing."

HAVE_LUA=0
if ls /usr/lib/*/rime-plugins/librime-lua.so >/dev/null 2>&1 || ls /usr/lib/rime-plugins/librime-lua.so >/dev/null 2>&1; then
  HAVE_LUA=1
fi

# fcitx5 rewrites its config when it exits, so stop it before touching files
if pgrep -x fcitx5 >/dev/null; then
  say "Stopping the running fcitx5…"
  pkill -x fcitx5 || true
  for _ in $(seq 20); do pgrep -x fcitx5 >/dev/null || break; sleep 0.2; done
fi

# ── 2. Rime schema, dictionaries, Lua, OpenCC tables ─────────────────
say "Installing the 港式拼音 schema into $RIME_DIR"
mkdir -p "$RIME_DIR/lua" "$RIME_DIR/opencc"
backup "$RIME_DIR/default.custom.yaml"

: > "$MANIFEST.new"
install_file() {  # install_file <src relative to rime/> [--keep]
  local src="$HERE/rime/$1" dst="$RIME_DIR/$1"
  if [ "${2:-}" = "--keep" ] && [ -e "$dst" ]; then
    return  # never overwrite the user's own word list
  fi
  install -m 644 -D "$src" "$dst"
  echo "$1" >> "$MANIFEST.new"
}
install_file hk_pinyin.schema.yaml
install_file hk_pinyin.dict.yaml
install_file hk_pinyin.hk_terms.dict.yaml
install_file hk_pinyin.user_terms.dict.yaml --keep
install_file default.custom.yaml
install_file lua/hk_datetime.lua
install_file lua/hk_terms_filter.lua
install_file opencc/hk_terms.json
install_file opencc/hk_terms.txt
install_file opencc/hk_glyph.json
install_file opencc/hk_glyph.txt
mv "$MANIFEST.new" "$MANIFEST"

if [ "$HAVE_LUA" -eq 0 ]; then
  warn "librime-lua not found: using the fallback (no rq/sj/xq dates; HK terms replace instead of being listed first)."
  backup "$RIME_DIR/hk_pinyin.custom.yaml"
  cat > "$RIME_DIR/hk_pinyin.custom.yaml" <<'YAML'
# Written by hk-pinyin-ime install.sh: fallback for systems without librime-lua
patch:
  engine/translators:
    - punct_translator
    - script_translator
  engine/filters:
    - simplifier@hk_terms
    - simplifier@hk_glyph
    - uniquifier
  hk_terms:
    opencc_config: hk_terms.json
    option_name: hk_terms
    tips: none
YAML
  echo "hk_pinyin.custom.yaml" >> "$MANIFEST"
fi

# Compile now so problems show up here rather than silently in the tray
if command -v rime_deployer >/dev/null; then
  say "Compiling dictionaries (first run takes ~10 s)…"
  if rime_deployer --build "$RIME_DIR" /usr/share/rime-data "$RIME_DIR/build" >/tmp/hk-pinyin-deploy.log 2>&1; then
    ok "Schema compiled"
  else
    warn "rime_deployer reported problems — see /tmp/hk-pinyin-deploy.log"
  fi
fi

# ── 3. themes ────────────────────────────────────────────────────────
say "Installing macOS-style themes"
for t in macos-light macos-dark; do
  mkdir -p "$THEME_DIR/$t"
  install -m 644 "$HERE/themes/$t/"* "$THEME_DIR/$t/"
done
ok "Themes installed"

# ── 4. fcitx5 settings ───────────────────────────────────────────────
if [ "$DO_CONFIG" -eq 1 ]; then
  if [ -z "$LAYOUT" ]; then
    LAYOUT="$(localectl status 2>/dev/null | awk -F': ' '/X11 Layout/ {print $2}' | cut -d, -f1 | tr -d ' ' || true)"
    LAYOUT="${LAYOUT:-us}"
  fi
  say "Configuring fcitx5 (English layout: $LAYOUT)"
  mkdir -p "$CONF_DIR/conf"
  for f in profile config conf/classicui.conf conf/rime.conf; do backup "$CONF_DIR/$f"; done

  cat > "$CONF_DIR/profile" <<EOF
[Groups/0]
Name=Default
Default Layout=$LAYOUT
DefaultIM=rime

[Groups/0/Items/0]
Name=keyboard-$LAYOUT
Layout=

[Groups/0/Items/1]
Name=rime
Layout=

[GroupOrder]
0=Default
EOF

  cat > "$CONF_DIR/config" <<'EOF'
[Hotkey]
EnumerateWithTriggerKeys=True
EnumerateSkipFirst=False

[Hotkey/TriggerKeys]
0=Control+space

[Hotkey/AltTriggerKeys]

[Hotkey/EnumerateForwardKeys]

[Hotkey/EnumerateBackwardKeys]

[Hotkey/ActivateKeys]

[Hotkey/DeactivateKeys]

[Behavior]
ActiveByDefault=False
ShareInputState=All
PreeditEnabledByDefault=True
ShowInputMethodInformation=True
showInputMethodInformationWhenFocusIn=False
CompactInputMethodInformation=True
EOF

  cat > "$CONF_DIR/conf/classicui.conf" <<'EOF'
Vertical Candidate List=False
WheelForPaging=True
Font="Noto Sans CJK HK 13"
MenuFont="Noto Sans CJK HK 11"
TrayFont="Noto Sans CJK HK Bold 10"
PreferTextIcon=True
ShowLayoutNameInIcon=True
UseInputMethodLanguageToDisplayText=True
Theme=macos-light
DarkTheme=macos-dark
UseDarkTheme=True
UseAccentColor=False
EnableFractionalScale=True
EOF

  cat > "$CONF_DIR/conf/rime.conf" <<'EOF'
PreeditMode="Composing text"
PreeditCursorPositionAtBeginning=False
InputState=All
EOF
  ok "fcitx5 configured"

  # make fcitx5 the system input-method framework
  if command -v im-config >/dev/null; then
    im-config -n fcitx5 >/dev/null 2>&1 && ok "im-config set to fcitx5"
  fi
  mkdir -p "$HOME/.config/environment.d"
  cat > "$HOME/.config/environment.d/90-hk-pinyin-fcitx5.conf" <<'EOF'
# written by hk-pinyin-ime
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
SDL_IM_MODULE=fcitx
GLFW_IM_MODULE=ibus
EOF
  # start fcitx5 on login (GNOME Wayland does not run im-config's launcher)
  if [ -f /usr/share/applications/org.fcitx.Fcitx5.desktop ]; then
    mkdir -p "$HOME/.config/autostart"
    cp /usr/share/applications/org.fcitx.Fcitx5.desktop "$HOME/.config/autostart/"
  fi
fi

# ── 5. start it ──────────────────────────────────────────────────────
if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
  say "Starting fcitx5…"
  (setsid fcitx5 -d --replace >/dev/null 2>&1 &) || true
fi

echo
ok "港式拼音 installed."
[ -d "$BACKUP" ] && echo "   Previous settings were saved to: $BACKUP"
cat <<'EOF'

   Next:  log out and log back in once.
   Then:  Ctrl+Space  switch between English and 港式拼音
          Shift       quick Chinese / English toggle while typing
          Ctrl+`      option menu (香港字形 / 香港詞彙 / 全形 …)

   GNOME on Wayland: also install the "Input Method Panel" (kimpanel)
   GNOME Shell extension so the candidate window follows the cursor.
EOF
