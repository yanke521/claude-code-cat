#!/bin/bash
# 小猫状态栏：小猫 + 模型 + 目录 + 上下文用了多少。颜色跟 themes/cream-cat.json 一套。
in=$(cat)
P=$'\033[38;2;196;74;110m'; G=$'\033[38;2;98;120;70m'; D=$'\033[38;2;160;146;132m'; R=$'\033[0m'
model=$(jq -r '.model.display_name // "Claude"' <<<"$in")
dir=$(jq -r '.workspace.current_dir // .cwd // ""' <<<"$in"); dir=${dir/#$HOME/\~}
pct=$(jq -r '(.context_window.used_percentage // empty) | floor' <<<"$in" 2>/dev/null)
h=$(date +%H); face='•ω•'; [ "$h" -ge 0 ] && [ "$h" -lt 6 ] && face='-ω-'
out="${P}ฅ(${face})ฅ KeCode${R} ${D}·${R} ${G}${model}${R} ${D}·${R} ${G}${dir}${R}"
[ -n "$pct" ] && out="$out ${D}· 肚子 ${pct}%${R}"
printf '%s' "$out"
