# img-rev — 图片反推工程师

**给一张图片，反推出它的风格、光线、镜头、调色与质感，并给出可复用的提示词。**

img-rev 是一个 Agent Skill（`SKILL.md` 格式）：它分析一张成品图，产出一份**逐项标注证据等级**的拆解报告——哪些是从画面里直接看出来的，哪些是合理推测，哪些凭成图根本判断不了。报告之后附视觉锚点和一段可直接复用的风格提示词（中英双语）。

它融合了两个开源项目的长处：[LunarXuan/image-prompt-reverse](https://github.com/LunarXuan/image-prompt-reverse) 的分析框架与证据纪律（内核），和 Zemon 的 `image-style-reverse-engineer` 的结构化报告层（14 维报告 + 5 色卡 + JSON 校验器）。关键改造：原报告层「每张图必须给出具体焦段 / 色温 / 胶片型号，否则校验失败」的强制规则被**证据分级**取代——没有证据的参数绝不许编。

---

## 三种模式

| 模式 | 什么时候用 | 产出 |
|---|---|---|
| **A · 提取报告**（默认） | 「拆一下这张图的风格和参数」 | 14 维逐项报告（每项标证据等级）+ 3–5 个视觉锚点 + 中英双语风格后缀提示词 |
| **B · 同图还原** | 「给我能重生成这张图的提示词」 | 中文还原提示词（450–700 字，锚点织入前 1/3）+ 英文等义版 + 10–15 条本图专属负面词 |
| **C · 只提风格** | 「只要风格，换个主体」 | 先列剥离清单（原图主体、身份、专属物件不带走），再给去主体化的风格档案 + 带 `[SUBJECT]` 占位的主提示词 + 分组负面词 |

## 证据分级（本技能的铁律）

报告里的每个数值、每条判断，必须属于且标明以下三级之一：

- **观察 observed** — 画面里直接可见或可测量的：构图、景别、可读的阴影方向、实测色值。
- **推测 inferred** — 由可见效果反推的：焦段、光圈、色温、光比、胶片 / LUT。**只能以推测出现，必须带波浪号或区间，并写明依据的可见效果**（如「背景压缩与虚化形态 → ~85mm, ~f/1.8–2.8」）。
- **未知 unknown** — 凭成图判断不了的：是实拍还是 AI 生成、具体设备型号、无证据的胶片型号。**如实写未知，不许拿推测填空。**

色卡固定 5 色 HEX，并标明来源：`eyeballed`（目测近似）或 `measured`（工具采样，注明工具；采样要取饱和核心点，区域平均会被高光洗淡）。

## 快速开始

### 安装

把整个 `img-rev` 文件夹放进你的 agent 的技能目录即可，例如：

- Muse：`~/workspace/custom-skills/img-rev/`
- 其他兼容 Agent Skills 规范的 agent：其 `skills/` 目录

`skill.yaml` 是 Muse 的注册卡；其他平台只读 `SKILL.md` 也可工作。

### 使用

把图片发给 agent 并说明意图即可，例如：

```text
用 A 模式拆这张图：风格、光、镜头、调色都要，给我报告和可复用的提示词。
```

```text
只要风格，不要原图的人物和服装，我要换我自己的角色资产（C 模式）。
```

```text
给我能 1:1 还原这张图的提示词，中英双语（B 模式）。
```

### JSON 报告与校验

任一模式都可要求输出 JSON，结构见 [`references/report-schema.json`](references/report-schema.json)。交付前用自带校验器验一遍（仅用 Python 标准库）：

```bash
python3 scripts/validate_report.py path/to/report.json
```

校验器会拦下：证据等级缺失、推测型参数写成裸精确值（如 `85mm f/1.4`、`5500K` 不带波浪号 / 区间）、色卡不足 5 色、C 模式缺风格档案等问题。示例报告在 [`examples/example_report.json`](examples/example_report.json)。

## 文件结构

```text
img-rev/
├── SKILL.md                              # 技能本体：三模式流程 + 证据分级铁律
├── skill.yaml                            # Muse 注册卡
├── references/
│   ├── analysis-framework.md             # 14 维报告框架（含速查短表）
│   ├── category-guides.md                # 15+ 分类专项（人像 / 风景 / 插画 / 商品…）
│   ├── light-and-color-vocabulary.md     # 光色词表：色温、光比、光质、胶片感
│   └── report-schema.json                # JSON 报告结构
├── scripts/
│   └── validate_report.py                # 报告校验器（stdlib only）
├── examples/
│   └── example_report.json               # 一份通过校验的完整示例
├── SOURCES.md                            # 上游来源与融合说明
└── LICENSE                               # GPL-3.0
```

## 实测记录

建成当天的首跑（山茶花园汉服人像）：A 模式报告的色卡走 PIL 采样（`measured`），采样点取花瓣饱和核心而非区域平均；焦段与色温以推测区间给出。随后用同一张图的 C 模式把风格迁移到另一位人物资产（古代纱裙版），风格档案与构图规则完整迁移、原图主体零串入，报告 JSON 均通过自家校验器。

## 来源与许可

- 内核（分析框架、分类专项、媒介边界、双语还原格式）源自 [LunarXuan/image-prompt-reverse](https://github.com/LunarXuan/image-prompt-reverse)，GPL-3.0。
- 报告层（维度结构、色卡、光色词表、校验器思路）参考 Zemon-tech/contentCreationAgent 的 `image-style-reverse-engineer`（该仓库未给该技能附许可文件，详见 [`SOURCES.md`](SOURCES.md)）；其「强制具体参数」规则被本技能的证据分级**有意替换**，未予沿用。
- 本仓库整体以 **GPL-3.0** 发布。
