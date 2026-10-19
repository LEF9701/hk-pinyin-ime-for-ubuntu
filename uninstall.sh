#!/usr/bin/env bash
# 港式拼音 HK Pinyin — remove the schema and themes for the current user.
#
#   ./uninstall.sh            remove 港式拼音 files, restore default fcitx5 theme
#   ./uninstall.sh --purge    also delete your learned words and own word list
#
# Packages (fcitx5, fcitx5-rime …) are left installed; remove them with apt if wanted.

set -euo pipefail

RIME_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/rime"
THEME_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/themes"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/fcitx5"
MANIFEST="$RIME_DIR/.hk_pinyin_manifest"
PURGE=0
[ "${1:-}" = "--purge" ] && PURGE=1

pgrep -x fcitx5 >/dev/null && { pkill -x fcitx5 || true; sleep 1; }

if [ -f "$MANIFEST" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] && rm -f "$RIME_DIR/$f"
  done < "$MANIFEST"
  rm -f "$MANIFEST"
fi
rm -f "$RIME_DIR"/build/hk_pinyin.* 2>/dev/null || true
if [ "$PURGE" -eq 1 ]; then
  rm -rf "$RIME_DIR"/hk_pinyin.userdb "$RIME_DIR"/hk_pinyin.user_terms.dict.yaml
fi
rm -rf "$THEME_DIR/macos-light" "$THEME_DIR/macos-dark"

if [ -f "$CONF_DIR/conf/classicui.conf" ]; then
  sed -i -e 's/^Theme=macos-light/Theme=default/' -e 's/^DarkTheme=macos-dark/DarkTheme=default-dark/' \
    "$CONF_DIR/conf/classicui.conf"
fi
rm -f "$HOME/.config/environment.d/90-hk-pinyin-fcitx5.conf"

echo "港式拼音 removed."
ls -d "$CONF_DIR"/hk-pinyin-backup-* 2>/dev/null | sed 's/^/  backup kept: /' || true
echo "fcitx5 itself is still installed. Run 'fcitx5 -d' to restart it, or"
echo "'sudo apt remove fcitx5 fcitx5-rime' and 'im-config -n ibus' to go back to IBus."
