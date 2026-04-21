# Configuration reference (`config.yaml`)

All runtime parameters are driven by a single YAML configuration file.

- Default path: `config/config.yaml`
- Template: `config/config.example.yaml`

On the first run (`python run.py`), if `config/config.yaml` does not exist, the program will create it from the template and ask you to edit it.

> Tip: `config/config.yaml` is included in `.gitignore` by default so you don't accidentally commit credentials.

---

## Full example

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

## `xnat`

### `xnat.base_url`

- Type: string
- Example: `https://multi-x.com/xnat`

This must be the **XNAT base path** for REST API calls and typically ends with `/xnat`.

### `xnat.project`

- Type: string
- Example: `Aneurysm_ISBI`

The XNAT **Project ID** (usually what you see as the project label in the UI).

### `xnat.alias` / `xnat.secret`

- Type: string or `null`

Two recommended ways:

1) Put them directly into `config.yaml` (simplest, but never commit the file)

2) Keep them `null` in config and provide credentials via environment variables:

```powershell
$env:XNAT_ALIAS="..."
$env:XNAT_SECRET="..."
```

### `xnat.verify_tls`

- Type: bool
- Default: `true`

If your XNAT uses a normal public TLS certificate, keep this as `true`.  
Only set it to `false` if you **know** you need to bypass TLS verification (e.g. self-signed cert in a trusted internal network).

---

## `local_data`

### `local_data.root_dir`

- Type: path string
- Example: `D:\\lfm\\data\\domain\\SHINY\\raw_data`

On Windows, we recommend using **single quotes** and double backslashes (`\\`) to avoid YAML escaping issues.

### `images_subdir` / `labels_vessel_subdir` / `labels_aneurysm_subdir`

Defaults match the SHINY layout:

- `images`
- `labels_vessel`
- `labels_aneurysm`

If you rename local folders, update these values accordingly.

---

## `upload`

### `upload.resource`

- Type: string
- Default: `RAW`

Subject-level resource name. Files will be uploaded under:

`Project / Subject / Resources / <resource> / files`

### `upload.overwrite`

- Type: bool
- Default: `true`

If `true`, uploads will overwrite existing remote files with the same name.

### `upload.require_all_files`

- Type: bool
- Default: `true`

Controls whether each subject must have all three files:

- `true`: subject must have **image + 2 labels**; otherwise the subject fails
- `false`: upload whatever exists for that subject (still requires at least 1 file)

### `upload.remote_filenames`

Locally the three files are all named `<subject>.nii.gz`, so they would collide on XNAT if placed in the same folder.  
Therefore, this tool uses fixed remote names (configurable):

- `image` → default `image.nii.gz`
- `labels_vessel` → default `labels_vessel.nii.gz`
- `labels_aneurysm` → default `labels_aneurysm.nii.gz`

---

## `demographics`

### `demographics.enabled`

- Type: bool
- Default: `false`

When enabled, the tool also sets these subject-level fields via the XNAT REST API:

- `gender` (`male` / `female` / `unknown`)
- `handedness` (`right` / `left` / `unknown`)
- `yob` (year of birth)

### `demographics.mode`

Currently supported:

- `random`

(It's straightforward to extend this to read demographics from a CSV if needed.)

### `demographics.only_missing`

- `true`: fill only empty fields (safer; does not overwrite existing values)
- `false`: always overwrite with the generated values

### `demographics.seed`

Random seed for reproducibility.  
Set any integer to ensure the same random assignments across runs.

### `demographics.out_csv`

Write assigned values to a CSV file (recommended), e.g.:

- `outputs/random_demographics.csv`

If the path is relative, it is resolved relative to the repo root.

---

## `run`

### `run.dry_run`

- Type: bool
- Default: `false`

If `true`, the tool prints planned actions without making any write requests to XNAT.
