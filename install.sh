#!/usr/bin/env bash
# 一键装：拷文件进 ~/.claude、改 settings.json（先备份）、往 shell 配置里加 claude() 函数。
# 跑第二遍不会重复加。
set -e
cd "$(dirname "$0")"
C="$HOME/.claude"
mkdir -p "$C/themes"

cp files/kecat.py files/kecode_start.py files/statusline-cat.sh "$C/"
cp files/themes/cream-cat.json "$C/themes/"
chmod +x "$C/kecat.py" "$C/kecode_start.py" "$C/statusline-cat.sh"
echo "· 文件已拷进 $C"

command -v jq >/dev/null || echo "! 状态栏要用 jq，没装的话：sudo apt install jq / brew install jq"

S="$C/settings.json"
[ -f "$S" ] && cp "$S" "$S.bak-cat-$(date +%Y%m%d%H%M%S)" && echo "· settings.json 已备份"
python3 - "$S" "$C/statusline-cat.sh" <<'PY'
import json, os, sys
path, sl = sys.argv[1], sys.argv[2]
d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
if "statusLine" in d and d["statusLine"].get("command") != sl:
    print("· 你原来有自己的状态栏，没动它（想换成小猫的看 README 第 4 块）")
else:
    d["statusLine"] = {"type": "command", "command": sl, "padding": 1}
d["spinnerVerbs"] = {"mode": "replace", "verbs": [
    "舔爪子中", "踩奶中", "揣手手中", "翻肚皮中", "追尾巴中",
    "蹭蹭中", "打呼噜中", "偷看中", "叼毛线中", "伸懒腰中"]}
d["spinnerTipsOverride"] = {"excludeDefault": True, "label": "喵", "tips": [
    "敲 /theme 能换回原来的样子",
    "状态栏里「肚子」是上下文用了多少，满了会自动压缩",
    "Esc 打断我，两下 Esc 回到上一句"]}
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("· settings.json 已写好")
PY

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [ -f "$rc" ] || continue
  if grep -q '>>> claude-code-cat >>>' "$rc"; then
    echo "· $rc 里已经有了，跳过"
  else
    printf '\n' >> "$rc"; cat files/bashrc-snippet.sh >> "$rc"
    echo "· 已加进 $rc"
  fi
done

echo
echo "装好了。新开一个终端（或者 source ~/.bashrc），再敲 claude。"
