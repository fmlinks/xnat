# 配置参考（config.yaml）

本项目所有运行参数都由一个 YAML 配置文件驱动：

- 默认路径：`config/config.yaml`
- 模板文件：`config/config.example.yaml`

第一次运行 `python run.py` 时，如果 `config/config.yaml` 不存在，会自动从模板生成并提示你编辑。

> 提醒：`config/config.yaml` 默认已加入 `.gitignore`，避免把凭据提交到 GitHub。

---

## 完整示例

```yaml
xnat:
  base_url: "https://multi-x.com/xnat"
  project: "Aneurysm_ISBI"
  alias: null
  secret: null
  verify_tls: true

local_data:
  root_dir: 'D:\\lfm\\data\\domain\\SHINY\\raw_data'
  images_subdir: "images"
  labels_vessel_subdir: "labels_vessel"
  labels_aneurysm_subdir: "labels_aneurysm"

upload:
  resource: "RAW"
  overwrite: true
  require_all_files: true
  remote_filenames:
    image: "image.nii.gz"
    labels_vessel: "labels_vessel.nii.gz"
    labels_aneurysm: "labels_aneurysm.nii.gz"

demographics:
  enabled: false
  mode: "random"
  only_missing: true
  seed: 20250107
  yob_min: 1940
  yob_max: 1980
  include_unknown: false
  unknown_probability: 0.05
  out_csv: "outputs/random_demographics.csv"

run:
  dry_run: false
```

---

## xnat

### `xnat.base_url`

- 类型：字符串
- 例子：`https://multi-x.com/xnat`

注意：这是 **XNAT 的根路径**，通常以 `/xnat` 结尾。

### `xnat.project`

- 类型：字符串
- 例子：`Aneurysm_ISBI`

这是 XNAT Project 的 **Project ID**（一般等同于你在网页里看到的 project label）。

### `xnat.alias` / `xnat.secret`

- 类型：字符串或 `null`

两种方式：

1) 直接写入 config（最省事，但注意不要提交 GitHub）
2) 留空（null），改用环境变量：

```powershell
$env:XNAT_ALIAS="..."
$env:XNAT_SECRET="..."
```

### `xnat.verify_tls`

- 类型：bool
- 默认：`true`

如果你的 XNAT 是自签名证书且你明确知道安全，可设 `false`。

---

## local_data

### `local_data.root_dir`

- 类型：路径字符串
- 例子：`D:\\lfm\\data\\domain\\SHINY\\raw_data`

建议 Windows 下用**单引号**包住，并写双反斜杠 `\\`，避免 YAML 转义问题。

### `images_subdir` / `labels_vessel_subdir` / `labels_aneurysm_subdir`

默认就是你现在的数据结构：

- `images`
- `labels_vessel`
- `labels_aneurysm`

如果你改了文件夹名字，可以在这里对应修改。

---

## upload

### `upload.resource`

- 类型：字符串
- 默认：`RAW`

资源（resource）名字，上传的文件会放在：

`Project / Subject / Resources / <resource> / files`

### `upload.overwrite`

- 类型：bool
- 默认：`true`

是否允许覆盖远端同名文件。

### `upload.require_all_files`

- 类型：bool
- 默认：`true`

控制「一个 subject 是否必须三份文件齐全」：

- `true`：只要缺一个（image 或任一 label）就会报错/失败
- `false`：会上传存在的文件（但至少需要存在 1 个文件）

### `upload.remote_filenames`

因为本地三份文件都叫 `<subject>.nii.gz`，会重名冲突，所以远端用三个固定文件名（可自定义）：

- `image` → 默认 `image.nii.gz`
- `labels_vessel` → 默认 `labels_vessel.nii.gz`
- `labels_aneurysm` → 默认 `labels_aneurysm.nii.gz`

---

## demographics

### `demographics.enabled`

- 类型：bool
- 默认：`false`

开启后，会对每个 subject 额外调用一次 XNAT REST API 写入：

- `gender`（male/female/unknown）
- `handedness`（right/left/unknown）
- `yob`（year of birth）

### `demographics.mode`

目前仅支持：

- `random`

（后续可以很容易扩展为从 CSV 读真实 demographic。）

### `demographics.only_missing`

- `true`：只填空字段，不覆盖已有值（更安全）
- `false`：每次都会用随机值覆盖

### `demographics.seed`

随机种子。设一个固定整数就能保证每次生成结果一致（便于复现实验）。

### `demographics.out_csv`

把分配结果写入 CSV（推荐打开），例如：

- `outputs/random_demographics.csv`

---

## run

### `run.dry_run`

- 类型：bool
- 默认：`false`

为 `true` 时只打印计划执行内容，不向 XNAT 发起写请求。
