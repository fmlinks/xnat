# XNAT SHINY Bulk Uploader

A small, **GitHub-ready** tool to bulk upload three NIfTI files per subject (image + vessel label + aneurysm label) into an XNAT **Project** (as *Subject-level resource files*).  
Optionally, it can also populate basic demographics for each subject (**M/F**, **Hand**, **YOB** in the XNAT UI).

This repository is tailored for the following local layout:

- `raw_data/images/<subject>.nii.gz`
- `raw_data/labels_vessel/<subject>.nii.gz`
- `raw_data/labels_aneurysm/<subject>.nii.gz`

After upload, the three files are stored **without any subfolders** under the same subject resource (default: `RAW`).

---

## 1. Features

- ✅ **One-command bulk upload**: auto-discover subjects, auto-create subjects, auto-create the subject resource
- ✅ **No subfolders on XNAT**: files are placed directly under the resource root
- ✅ **Avoid name collisions**: locally all three files are named `<subject>.nii.gz`. On XNAT they are renamed to:
  - `image.nii.gz`
  - `labels_vessel.nii.gz`
  - `labels_aneurysm.nii.gz`
- ✅ **Optional demographics**: randomly generate and set `gender / handedness / yob` (shown as `M/F`, `Hand`, `YOB` in the UI)
- ✅ **Config-driven**: XNAT URL, project ID, local paths, overwrite policy, demographics, etc. are controlled in `config.yaml`
- ✅ **Safe-by-default**: `config/config.yaml` is included in `.gitignore` to avoid accidentally committing credentials

---

## 2. Expected local data structure

Example (Windows):

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

Rule: for the same subject (e.g. `147`) the file `147.nii.gz` should exist in **all three** folders.

> The subject list is derived from `images/*.nii.gz` by default.

---

## 3. What it looks like on XNAT after upload

Example for subject `147`:

- Project: `Aneurysm_ISBI`
- Subject: `147`
- Resource: `RAW` (configurable)

Files inside the resource (**no subfolders**):

```
image.nii.gz
labels_vessel.nii.gz
labels_aneurysm.nii.gz
```

Why do we rename the files?

- Because locally all three files are named `147.nii.gz`. If we uploaded them “as-is” into the same folder, they would overwrite each other.

---

## 4. Quick start (Windows / PowerShell)

### 4.1 Requirements

- Windows 10/11
- Python **3.9+** (recommended: 3.10 / 3.11)
- Network access to your XNAT instance (e.g. `https://multi-x.com/xnat/`)

### 4.2 Clone / unzip the repo

Assume you place it at:

```
C:\lfm\code\xnat-shiny-uploader
```

### 4.3 Create a virtual environment and install dependencies

```powershell
cd C:\lfm\code\xnat-shiny-uploader

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 First run: auto-create `config/config.yaml`

You can run once:

```powershell
python run.py
```

If `config/config.yaml` does not exist, the program will create it from `config/config.example.yaml` and exit, asking you to edit it.

### 4.5 Edit the configuration (most important step)

Open:

```
config/config.yaml
```

At minimum, set:

- `xnat.base_url` (example: `https://multi-x.com/xnat`)
- `xnat.project` (example: `Aneurysm_ISBI`)
- `local_data.root_dir` (example: `D:\lfm\data\domain\SHINY\raw_data`)

#### How to provide credentials (alias/secret)

Two options:

**Option A (simplest): put them in `config.yaml` (do NOT commit them)**

```yaml
xnat:
  alias: "YOUR_ALIAS"
  secret: "YOUR_SECRET"
```

**Option B (recommended): use environment variables**

```powershell
$env:XNAT_ALIAS="YOUR_ALIAS"
$env:XNAT_SECRET="YOUR_SECRET"
```

…and keep `alias: null` / `secret: null` in `config.yaml`.

### 4.6 One-command upload

From the repo root:

```powershell
python run.py
```

Optional: explicitly specify the config path:

```powershell
python run.py --config .\config\config.yaml
```

### 4.7 Dry run (print actions, do not upload)

```powershell
python run.py --dry-run
```

### 4.8 “Super simple” one-click scripts (optional)

- Windows: run `scripts\windows\run.bat`
- Linux/WSL/macOS: run `scripts/linux/run.sh` (first time: `chmod +x scripts/linux/run.sh`)

They will create `.venv`, install dependencies, and then run `run.py`.

---

## 5. Quick start (Linux / WSL / macOS)

```bash
cd /path/to/xnat-shiny-uploader

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python run.py
```

If you are on WSL and your data is on a Windows drive, the path usually looks like:

- Windows: `D:\lfm\data\...`
- WSL: `/mnt/d/lfm/data/...`

Set `local_data.root_dir` accordingly.

---

## 6. Optional: populate random demographics (M/F, Hand, YOB)

In the XNAT Subjects table:

- **M/F** maps to `gender`
- **Hand** maps to `handedness`
- **YOB** maps to `yob` (year of birth)

Enable demographics in `config/config.yaml`:

```yaml
demographics:
  enabled: true
  mode: "random"         # supported: random
  only_missing: true     # true = do not overwrite existing values

  seed: 20250107         # fixed seed for reproducibility
  yob_min: 1940
  yob_max: 1980

  include_unknown: false
  unknown_probability: 0.05

  out_csv: "outputs/random_demographics.csv"
```

Then run the same command:

```powershell
python run.py
```

A CSV record will be written to `outputs/random_demographics.csv` (recommended for audit / reproducibility).

---

## 7. Key config options (short version)

Common options in `config/config.yaml`:

- `upload.resource`: resource name (default: `RAW`)
- `upload.overwrite`: overwrite remote files with the same name (default: `true`)
- `upload.require_all_files`:
  - `true`: require all 3 files per subject (default)
  - `false`: upload whatever exists (still requires at least 1 file)

Full explanation: see `docs/CONFIG.md`.

---

## 8. How to verify after upload (recommended)

Examples below use `curl.exe` (available on Windows).

Prepare `AUTH`:

```powershell
$AUTH="$env:XNAT_ALIAS`:$env:XNAT_SECRET"
```

### 8.1 List subjects in the project

```powershell
curl.exe -sS -u $AUTH "https://multi-x.com/xnat/data/projects/Aneurysm_ISBI/subjects?format=json"
```

### 8.2 List resource files for a subject (example: 147)

```powershell
curl.exe -sS -u $AUTH "https://multi-x.com/xnat/data/projects/Aneurysm_ISBI/subjects/147/resources/RAW/files?format=json"
```

You should see `image.nii.gz / labels_vessel.nii.gz / labels_aneurysm.nii.gz`.

### 8.3 Check subject demographics (example: 147)

```powershell
curl.exe -sS -u $AUTH "https://multi-x.com/xnat/data/projects/Aneurysm_ISBI/subjects/147?format=json"
```

---

## 9. Troubleshooting

See `docs/TROUBLESHOOTING.md`.

Common issues:

- **401/403**: wrong alias/secret or no permission on the project
- **404**: wrong `base_url` (missing `/xnat` or duplicated `/xnat/xnat`)
- **HTML response instead of JSON**: you are hitting the UI page, not the REST API

---

## 10. Security notes (important)

- Do **not** commit `alias/secret` to GitHub.
- `config/config.yaml` is ignored by default (`.gitignore`).
- If your secret was ever pasted into logs or chat, rotate/revoke it in XNAT.

---

## 11. Repo layout

```
.
├─ run.py                       # entrypoint (reads config/config.yaml by default)
├─ config/
│  ├─ config.example.yaml       # template
│  └─ config.yaml               # your local config (gitignored)
├─ src/xnat_shiny_uploader/
│  ├─ main.py                   # pipeline
│  ├─ upload.py                 # upload logic
│  ├─ demographics.py           # demographics logic
│  ├─ xnat_client.py            # requests wrapper + retries
│  └─ config.py                 # YAML config loader
└─ docs/
   ├─ CONFIG.md
   └─ TROUBLESHOOTING.md
```
