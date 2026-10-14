# >>> claude-code-cat >>>
# 螃蟹换成猫：套 ~/.claude/kecat.py 那层壳（必须关动效，理由见那个文件开头）。
# 想要原样的 claude：command claude
claude() {
  if [ -t 0 ] && [ -t 1 ]; then
    local mode=plain
    if [ $# -eq 0 -o "$1" = "-c" -o "$1" = "--continue" -o "$1" = "-r" -o "$1" = "--resume" ]; then
      mode=$(python3 ~/.claude/kecode_start.py 2>/dev/null)
    fi
    if [ "$mode" = "cream" ]; then
      COLORTERM=truecolor python3 ~/.claude/kecat.py --settings '{"theme":"custom:cream-cat","prefersReducedMotion":true}' "$@"; local rc=$?
      printf '\033]111\007\033]110\007'; return $rc
    fi
    python3 ~/.claude/kecat.py --settings '{"prefersReducedMotion":true}' "$@"; return $?
  fi
  command claude "$@"
}
# <<< claude-code-cat <<<
