# claude-code-cat

把 Claude Code 开屏那只方块螃蟹换成一只猫，顺手铺一层奶油色。

```
  /\_/\     Claude Code v2.1.280
 ( •ω• )    Opus 5.5
 / >♡       ~/project

ฅ(•ω•)ฅ KeCode · Opus 5.5 · ~/project · 肚子 37%
```

- 开屏的螃蟹换成粗体莓粉的颜文字猫
- 终端底色换成奶油色 `#f6e9d3`，字是可可色（终端不支持就保持原样）
- 状态栏：小猫 + 模型 + 目录 + 「肚子」（上下文用了多少），凌晨 0–6 点猫会睡着 `-ω-`
- 干活时转圈的字换成「踩奶中」「揣手手中」「翻肚皮中」……

Claude Code 本体一行都没改，所有东西都在 `~/.claude/` 和 shell 配置里，升级不受影响。

## 安装

要 Linux / macOS / WSL，Python 3，状态栏要 `jq`。

```bash
git clone https://github.com/yanke521/claude-code-cat.git
cd claude-code-cat
./install.sh
```

然后新开一个终端（或 `source ~/.bashrc`），照常敲 `claude`。

`install.sh` 会先备份 `settings.json`。你原来要是有自己的状态栏，它不会去覆盖。跑两遍也不会重复加。

想临时用原版：`command claude`。不想要了：`./uninstall.sh`。

## 文件

| 文件 | 管什么 |
| --- | --- |
| `files/themes/cream-cat.json` | 配色主题。在 Claude Code 里敲 `/theme` 也能选到「奶油小猫」 |
| `files/kecode_start.py` | 启动前试着把终端底色换成奶油色，印一张小猫卡片 |
| `files/kecat.py` | 把螃蟹换成猫的那层壳 |
| `files/statusline-cat.sh` | 状态栏 |
| `files/bashrc-snippet.sh` | 把上面几个串起来的 `claude()` 函数 |

## 猫是怎么换上去的

螃蟹不是图片，是 Claude Code 用方块字拼出来的（3 行 × 9 格），而且没有设置能关掉它。所以 `kecat.py` 不碰它的程序，只在它和终端中间夹一层：

1. 开一个伪终端（pty），把真正的 `claude` 放进去跑。`claude` 以为自己在普通终端里。
2. 你敲的键原样转给它。
3. 它吐出来的字过一遍正则，认出螃蟹那三段方块字，换成**一样宽**的颜文字猫，再交给你的终端。
4. 窗口改大小时把尺寸同步进去。

```
  螃蟹（正面）               猫
  ' ▐' '▛███▛█'             '  /\_/\ '
  '▝▜' '█████' '█▀'         ' ( •ω• ) '
  '  ▝▝ ▝▝  '               ' / >♡    '
```

必须一样宽，因为猫右边紧跟着「Claude Code v…」那几行字，宽一格窄一格右边就整体歪掉。

还有几个细节：

- **螃蟹身上夹着颜色转义**（身体和眼睛颜色不一样）。正则把这些转义一起抓住，换完猫以后原样接在后面。丢了的话，右边的字会变色。
- **螃蟹可能被切成两半**：一半在这次 read 里，一半在下次。所以末尾要是有方块字，就先压 15 毫秒，等后半截来了再换。
- **不是交互终端就不套壳**，`claude -p` 在管道里照常跑。

## 底色是怎么换的

终端背景色可以用转义码当场改：`\033]11;#f6e9d3\007`（OSC 11）。但不是每个终端都认，不认的就默默忽略。所以 `kecode_start.py` 改完以后会再问一句「你现在背景是什么色」（`\033]11;?\007`），答得上来才算成功，这时候才套浅色主题。答不上来就把颜色还原，只换猫。退出时 `claude()` 会把底色还回去。

## 踩过的坑

| 现象 | 原因 | 怎么办 |
| --- | --- | --- |
| 猫身上露出半只螃蟹 | 螃蟹启动时会跳、会左看右看，这时只重画变了的那几格，碎片认不出来 | 必须带 `prefersReducedMotion: true`（`claude()` 里已经带了） |
| 装完还是螃蟹 | 当前窗口还是旧的 shell 配置 | 新开终端，或者 `source ~/.bashrc` |
| Claude Code 升级后螃蟹又回来了 | 它换了螃蟹的拼法，正则对不上了 | 在 tmux 里 `tmux pipe-pane -o 'cat >> /tmp/raw.log'` 抓一份原始输出，对照改 `kecat.py` 里的 `ROW1`~`ROW3` |
| 黑底配可可色字，看不清 | 终端不认 OSC 11，底色没换上，却套了浅色主题 | 别在 `settings.json` 里写死 `"theme"`，让 `claude()` 根据探测结果决定 |
| 颜色发灰，不是莓粉 | 终端不支持 24 位真彩色 | 会自动退到 256 色；tmux 里加 `set -as terminal-features ',xterm-256color:RGB'` |

## 自己改

- 换颜色：三个地方用的是同一套色——`cream-cat.json`、`statusline-cat.sh` 开头的 `P/G/D`、`kecat.py` 的 `PINK`。
- 换一只别的动物：改 `kecat.py` 里的 `CAT`，**每行宽度要跟螃蟹那行一样**（9 / 9 / 9 格）。
- 换转圈的词：改 `settings.json` 里的 `spinnerVerbs.verbs`。
