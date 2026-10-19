#!/usr/bin/env bash
# Engine tests for 港式拼音: types pinyin into librime and checks the first candidate.
# Needs: gcc, librime-dev, rime-data-luna-pinyin, librime-plugin-lua
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
# shellcheck disable=SC2046  # pkg-config output must be word-split
gcc -O1 -o "$WORK/rime_probe" "$HERE/tests/rime_probe.c" $(pkg-config --cflags --libs rime)
cp -r "$HERE/rime/." "$WORK/user/" 2>/dev/null || { mkdir -p "$WORK/user"; cp -r "$HERE/rime/." "$WORK/user/"; }

# input  expected-first-candidate  [expected-second]
CASES=(
  "xianggang 香港"
  "ruanjian 軟件"
  "ruanti 軟件 軟體"
  "wangluo 網絡"
  "bingxiang 雪櫃 冰箱"
  "jichengche 的士 計程車"
  "xinxikeji 資訊科技 信息科技"
  "weishenme 為甚麼 為什麼"
  "weisheng 衞生"
  "yonghu 用戶"
  "renqun 人群"
  "gangtie 港鐵"
  "dianyou 電郵"
  "bashizhan 巴士站"
  "qudi 佢哋"
  "wugai 唔該"
  "zhishi 只是"
  "xihuan 喜歡"
  "nihao, 你好，"
  "[ 「"
  "\\ 、"
  "^ ……"
  "_ ——"
)
pass=0; fail=0
inputs=(); for c in "${CASES[@]}"; do inputs+=("${c%% *}"); done
mapfile -t out < <("$WORK/rime_probe" "$WORK/user" /usr/share/rime-data "${inputs[@]}" 2>/dev/null)
for i in "${!CASES[@]}"; do
  read -r input exp1 exp2 <<<"${CASES[$i]}"
  line="${out[$i]#*⇒ }"
  line="${line#\[commit\] }"
  first="${line%% |*}"; first="${first%%〔*}"
  rest="${line#*| }"; second="${rest%% |*}"; second="${second%%〔*}"
  if [ "$first" = "$exp1" ] && { [ -z "${exp2:-}" ] || [ "$second" = "$exp2" ]; }; then
    pass=$((pass+1)); printf '  ok    %-14s %s\n' "$input" "$first${exp2:+ | $second}"
  else
    fail=$((fail+1)); printf '  FAIL  %-14s got: %s   want: %s %s\n' "$input" "${out[$i]}" "$exp1" "${exp2:-}"
  fi
done
# date/time translators produce something that starts with the year / a period of day
datel="$("$WORK/rime_probe" "$WORK/user" /usr/share/rime-data rq sj xq 2>/dev/null)"
grep -q "^rq ⇒ $(date +%Y)年" <<<"$datel" && { pass=$((pass+1)); echo "  ok    rq             $(date +%Y)年…"; } || { fail=$((fail+1)); echo "  FAIL  rq"; }
grep -qE "^sj ⇒ (凌晨|上午|下午|晚上)" <<<"$datel" && { pass=$((pass+1)); echo "  ok    sj             上午/下午…"; } || { fail=$((fail+1)); echo "  FAIL  sj"; }
grep -q "^xq ⇒ 星期" <<<"$datel" && { pass=$((pass+1)); echo "  ok    xq             星期…"; } || { fail=$((fail+1)); echo "  FAIL  xq"; }
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
