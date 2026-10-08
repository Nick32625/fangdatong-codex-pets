# 方小同 · 四款手绘风 Codex 桌宠

西装电吉他、15 Live 格子衬衫、蓝帽木吉他，以及安静盘腿弹琴的农人。

**[下载桌宠安装包](https://github.com/Nick32625/fangdatong-codex-pets/releases/latest/download/fangdatong-codex-pets.zip)** · [查看最新发布](https://github.com/Nick32625/fangdatong-codex-pets/releases/latest) · [反馈问题](https://github.com/Nick32625/fangdatong-codex-pets/issues)

| 西装电吉他 | 15 Live 递麦 | 蓝帽木吉他 | 农人盘腿 |
|:---:|:---:|:---:|:---:|
| ![西装款移动动作](previews/suit.gif) | ![格子衬衫款递麦动作](previews/mic.gif) | ![蓝帽款弹琴动作](previews/blue.gif) | ![农人款盘腿轻摇](previews/farmer.gif) |

每款包含 **9 种标准动作与 16 个注视方向**。上方预览直接来自安装包使用的动画图集；解压后打开 `index.html` 可以查看所有动作，暂停、逐帧播放，切换背景和显示大小。

## 适用环境

这是 **Codex 桌面环境的本地自定义桌宠资源包**，使用 v2 格式，需要宿主支持从 `~/.codex/pets/` 加载自定义桌宠。

目前提供 **macOS 一键安装脚本**，已在 Mac 上检查安装和文件完整性。它仍然依赖 Codex 的桌宠功能；本次不包含独立运行的 Mac 应用或 Windows 应用，也没有将普通 ChatGPT 网页聊天界面作为安装目标。

桌宠菜单名称和入口可能随宿主版本变化。如果你的应用中没有自定义桌宠功能，本安装包无法为它新增该功能。

## 安装：下载、解压、双击

1. 下载上方的 **`fangdatong-codex-pets.zip`**。
2. 解压整个文件夹，保留里面的文件结构。
3. 双击 **`安装到Codex.command`**。看到“四款方小同已安装”即表示文件安装完成。
4. 打开 Codex 的桌宠设置或选择面板，点击 **刷新 / Refresh**，再选择喜欢的一款。如果列表没有立即更新，重新打开应用后再查看。

安装后会出现这四个名字：

- 方小同 · 西装电吉他
- 方小同 · 15 Live 递麦
- 方小同 · 蓝帽木吉他
- 方小同 · 农人盘腿

脚本默认安装到你自己的 `~/.codex/pets/`；配置了 `CODEX_HOME` 时使用其下的 `pets/`。安装不需要 Python、Node、API 密钥或联网。

### 已有桌宠会怎样？

其他名称的桌宠保持不变。再次安装这四款时，脚本会先把已有同名文件夹完整备份到解压目录中的 `安装前备份/`，再更新图片和配置。

### 双击没有启动安装

可以使用下面的手动安装方式。也可以在终端进入**解压后的文件夹**，运行：

```bash
bash ./安装到Codex.command
```

### 手动安装

把下面四个文件夹复制到 `~/.codex/pets/`，然后在 Codex 中刷新：

```text
khalil-suit-handdrawn/
khalil-15live-handdrawn/
khalil-blue-handdrawn/
khalil-farmer-handdrawn/
```

每个文件夹中都应直接包含 `pet.json` 和 `spritesheet.webp`，不要再多嵌套一层。已有同名文件夹时，请先保留备份。

## 常见问题

**图片没有显示，或显示成大图块？** 先确认复制的是完整文件夹，`pet.json` 中的 `spriteVersionNumber` 为 `2`，并且宿主支持 v2 自定义桌宠。

**提示校验失败？** 重新下载并完整解压正式 Release。不要只下载其中某一个文件，也不要在安装前修改包内文件。

**预览怎样打开？** 下载并解压后双击 `index.html`，即可在浏览器中离线查看。GitHub 文件列表里的 HTML 页面显示的是源码。

**可以单独选一款吗？** 可以。一键安装会添加四款，之后在宿主中选择；手动安装时也可以只复制喜欢的一款。

**怎样移除？** 先在宿主里切换到其他桌宠，再移除对应的上述 `khalil-…-handdrawn` 文件夹并刷新。其他桌宠无需改动。

## 包内内容与验证

- 四套 v2 动画图集及配置。
- 四张透明设计原图，位于 `设计原图/`。
- 离线动作预览和四张 GIF 样片。
- macOS 安装脚本、检查摘要和 SHA-256 校验清单。

图集大小为 1536 × 2288，8 列 11 行，每格 192 × 208。制作阶段已完成逐帧视觉复核和独立方向检查；接近水平或垂直的少量中间注视方向幅度较小，保留为轻柔动作。

发布检查包括文件校验、图集尺寸与透明度、动作格完整性，以及隔离目录中的安装、备份和损坏文件测试。安装后的文件验证不等于对所有宿主版本的界面效果保证。

## 维护和重新打包

普通使用者下载 Release 即可。维护者可以克隆本仓库，并使用 Python 3.11+：

```bash
python -m pip install -r requirements-dev.txt
python scripts/release.py verify
python -m unittest discover -s tests -v
python scripts/release.py build
```

修改发布内容后，先运行 `python scripts/release.py prepare` 更新清单，再检查、测试和打包。`release/` 中会生成 ZIP 与 ZIP 的校验文件。

本项目为个人同人创作，角色图片采用 AI 辅助制作的手绘风格；非官方项目。
