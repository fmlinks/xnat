# XNAT SHINY Bulk Uploader

一个**可直接放到 GitHub** 的小工具：把本地三类 NIfTI（影像 + vessel label + aneurysm label）按 **Subject** 批量上传到 XNAT 的指定 **Project**，并且（可选）为每个 Subject 写入 demographics（`M/F`、`Hand`、`YOB`）。

> 适配你当前的数据结构：
>
> - `raw_data/images/<subject>.nii.gz`
> - `raw_data/labels_vessel/<subject>.nii.gz`
> - `raw_data/labels_aneurysm/<subject>.nii.gz`
>
> 上传到 XNAT 后：每个 subject 的同一个资源（resource，默认 `RAW`）里**不建子文件夹**，直接放 3 个文件。

---

## 1. 功能特性

- ✅ **一键批量上传**：自动遍历 subject、自动创建 subject、自动创建资源（resource）
- ✅ **文件不建子目录**：直接上传到 subject 的 resource 根目录
- ✅ **避免重名冲突**：本地三份文件都叫 `<subject>.nii.gz`，上传时会重命名为：
  - `image.nii.gz`
  - `labels_vessel.nii.gz`
  - `labels_aneurysm.nii.gz`
- ✅ **可选 demographics**：随机生成并写入 `gender / handedness / yob`（对应 UI 的 `M/F`、`Hand`、`YOB`）
- ✅ **配置驱动**：把 XNAT 地址、项目名、数据路径、是否 overwrite、是否写 demographics 等都写到 `config.yaml`
- ✅ **安全默认**：`config/config.yaml` 默认已加入 `.gitignore`，避免把凭据提交到 GitHub

---

## 2. 你的数据应当长这样（本地）

例如：

```
D:\lfm\data\domain\SHINY\raw_data
├─ images
│  ├─ 147.nii.gz
│  ├─ 149.nii.gz
│  └─ ...
├─ labels_vessel
│  ├─ 147.nii.gz
│  ├─ 149.nii.gz
│  └─ ...
└─ labels_aneurysm
   ├─ 147.nii.gz
   ├─ 149.nii.gz
   └─ ...
```

规则：同一个 subject（例如 `147`）在三个目录里都应该有同名文件 `147.nii.gz`。

> Subject 列表默认来自 `images/*.nii.gz`。

---

## 3. 上传到 XNAT 后会变成什么（远端）

以 subject `147` 为例：

- Project：`Aneurysm_ISBI`
- Subject：`147`
- Resource：`RAW`（可配置）

Resource 下文件（**没有任何子文件夹**）：

```
image.nii.gz
labels_vessel.nii.gz
labels_aneurysm.nii.gz
```

为什么要改名？

- 因为本地三份文件都叫 `147.nii.gz`，如果直接放在同一目录会互相覆盖。

---

## 4. 快速开始（Windows / PowerShell）

### 4.1 前置要求

- Windows 10/11
- Python **3.9+**（建议 3.10/3.11）
- 能访问你的 XNAT：例如 `https://multi-x.com/xnat/`

### 4.2 克隆/解压 repo

假设你把 repo 放到：

```
C:\lfm\code\xnat-shiny-uploader
```

### 4.3 创建虚拟环境并安装依赖

```powershell
cd C:\lfm\code\xnat-shiny-uploader

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 第一次运行：自动生成 config.yaml

你可以直接先跑一次：

```powershell
python run.py
```

如果 `config/config.yaml` 不存在，程序会自动用 `config/config.example.yaml` 生成一个模板并退出，然后提示你去编辑。

### 4.5 编辑配置文件（最重要的一步）

打开：

```
config/config.yaml
```

至少改这几项：

- `xnat.base_url`：例如 `https://multi-x.com/xnat`
- `xnat.project`：例如 `Aneurysm_ISBI`
- `local_data.root_dir`：例如 `D:\lfm\data\domain\SHINY\raw_data`

#### 凭据（alias/secret）怎么填？

两种方式任选一种：

**方式 A（最省事）：直接写进 config.yaml（注意不要提交到 GitHub）**

```yaml
xnat:
  alias: "YOUR_ALIAS"
  secret: "YOUR_SECRET"
```

**方式 B（更安全，推荐）：用环境变量**

```powershell
$env:XNAT_ALIAS="YOUR_ALIAS"
$env:XNAT_SECRET="YOUR_SECRET"
```

然后 `config.yaml` 里保持 `alias: null` / `secret: null` 即可。

### 4.6 一键上传

在 repo 根目录执行：

```powershell
python run.py
```

#### 你想更“傻瓜式”一点？（可选）

本 repo 也提供了两个一键脚本：

- Windows：双击或命令行运行 `scripts\windows\run.bat`
- Linux/WSL/macOS：运行 `scripts/linux/run.sh`（首次需 `chmod +x scripts/linux/run.sh`）

它们会自动创建 `.venv` 并安装依赖，然后执行 `run.py`。

（可选）你也可以显式指定配置：

```powershell
python run.py --config .\config\config.yaml
```

### 4.7 只预演不上传（Dry run）

```powershell
python run.py --dry-run
```

---

## 4.8 快速开始（Linux / WSL / macOS）

```bash
cd /path/to/xnat-shiny-uploader

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python run.py
```

如果你在 WSL 中访问 Windows 磁盘，路径通常形如：

- Windows：`D:\lfm\data\...`
- WSL：`/mnt/d/lfm/data/...`

把 `config/config.yaml` 里的 `local_data.root_dir` 改为你的实际路径即可。

---

## 5. 可选：随机写入 demographics（M/F、Hand、YOB）

你截图里 Subjects 表格的 `M/F`、`Hand`、`YOB` 分别对应 XNAT Subject 的字段：

- `gender`
- `handedness`
- `yob`

在 `config/config.yaml` 里把 demographics 打开：

```yaml
demographics:
  enabled: true
  mode: "random"         # 当前支持：random
  only_missing: true     # true = 不覆盖已有值

  seed: 20250107         # 固定随机种子，便于复现
  yob_min: 1940
  yob_max: 1980

  include_unknown: false
  unknown_probability: 0.05

  out_csv: "outputs/random_demographics.csv"
```

然后还是同一个命令：

```powershell
python run.py
```

跑完会生成 `outputs/random_demographics.csv`（记录每个 subject 被分配的随机值，方便留档）。

---

## 6. 配置项说明（精简版）

`config/config.yaml` 里最常用的配置：

- `upload.resource`：资源名（默认 `RAW`）
- `upload.overwrite`：是否覆盖远端同名文件（默认 `true`）
- `upload.require_all_files`：
  - `true`：缺一个就报错（默认）
  - `false`：缺哪个就跳过哪个，但至少要有 1 个文件

更完整说明见：`docs/CONFIG.md`

---

## 7. 上传后如何验证（推荐你做一次）

> 下面用 `curl.exe`（Windows 自带）举例。

先准备 AUTH：

```powershell
$AUTH="$env:XNAT_ALIAS`:$env:XNAT_SECRET"
```

### 7.1 列出项目里的 subjects

```powershell
curl.exe -sS -u $AUTH "https://multi-x.com/xnat/data/projects/Aneurysm_ISBI/subjects?format=json"
```

### 7.2 查看某个 subject 的 resource 文件列表（以 147 为例）

```powershell
curl.exe -sS -u $AUTH "https://multi-x.com/xnat/data/projects/Aneurysm_ISBI/subjects/147/resources/RAW/files?format=json"
```

你应该能看到 `image.nii.gz / labels_vessel.nii.gz / labels_aneurysm.nii.gz`。

### 7.3 查看 subject 的 demographics（以 147 为例）

```powershell
curl.exe -sS -u $AUTH "https://multi-x.com/xnat/data/projects/Aneurysm_ISBI/subjects/147?format=json"
```

---

## 8. 常见问题与排错

更完整排错见：`docs/TROUBLESHOOTING.md`。

### 8.1 401/403

- 说明 alias/secret 不对，或该用户对 project 没权限

### 8.2 404

- 常见原因：`base_url` 没写对
  - ✅ 正确：`https://multi-x.com/xnat`
  - ❌ 错误：少了 `/xnat` 或者多了重复 `/xnat/xnat`

### 8.3 200 但返回 HTML（不是 JSON）

- 通常是 URL 路径写错，或访问了 Web 页面而不是 REST API

### 8.4 文件很大、上传慢

- 这是正常现象（NIfTI 很大）
- 本工具默认是顺序上传（更稳），需要并行我也可以帮你扩展

---

## 9. 安全建议（强烈建议看）

- 不要把 `alias/secret` 提交到 GitHub
- `config/config.yaml` 默认已 gitignore
- 如果你曾把 secret 贴到聊天/日志里，请在 XNAT 里**轮换/撤销**那对 API key

---

## 10. 目录结构

```
.
├─ run.py                       # 一键入口（默认读 config/config.yaml）
├─ config/
│  ├─ config.example.yaml       # 配置模板
│  └─ config.yaml               # 你自己的配置（gitignore）
├─ src/xnat_shiny_uploader/
│  ├─ main.py                   # 主流程
│  ├─ upload.py                 # 上传逻辑
│  ├─ demographics.py           # demographics 写入逻辑
│  ├─ xnat_client.py            # requests 封装 + 重试
│  └─ config.py                 # YAML 配置解析
└─ docs/
   ├─ CONFIG.md
   └─ TROUBLESHOOTING.md
```
