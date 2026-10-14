#!/usr/bin/env bash
# 卸掉：删 ~/.claude 里那几个文件、把 shell 配置里的 claude() 摘掉、settings.json 里的三项去掉。
set -e
C="$HOME/.claude"
rm -f "$C/kecat.py" "$C/kecode_start.py" "$C/statusline-cat.sh" "$C/themes/cream-cat.json"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [ -f "$rc" ] && sed -i.bak-cat '/>>> claude-code-cat >>>/,/<<< claude-code-cat <<</d' "$rc"
done
S="$C/settings.json"
[ -f "$S" ] && python3 - "$S" "$C/statusline-cat.sh" <<'PY'
import json, sys
path, sl = sys.argv[1], sys.argv[2]
d = json.load(open(path, encoding="utf-8"))
if d.get("statusLine", {}).get("command") == sl:
    d.pop("statusLine")
d.pop("spinnerVerbs", None); d.pop("spinnerTipsOverride", None)
if d.get("theme") == "custom:cream-cat":
    d.pop("theme")
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
echo "卸干净了。新开一个终端就是原样的 claude。"
