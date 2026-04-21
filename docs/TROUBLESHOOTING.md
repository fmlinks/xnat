# Troubleshooting

This document helps you quickly diagnose common issues during bulk uploads.

---

## 1) 401 / 403 (Unauthorized / Forbidden)

Typical symptoms:

- HTTP 401 Unauthorized
- HTTP 403 Forbidden

Checklist:

1. Verify `alias/secret` are correct
2. Verify the account has permission on the target project (must be able to create subjects and upload resources)
3. If credentials were leaked (chat/logs), rotate/revoke the old key in XNAT and generate a new one

---

## 2) 404 (Not Found / wrong `base_url`)

The most common reason is an incorrect `xnat.base_url`.

Examples:

- ✅ Correct: `https://multi-x.com/xnat`
- ❌ Wrong: `https://multi-x.com/` (missing `/xnat`)
- ❌ Wrong: `https://multi-x.com/xnat/xnat` (duplicated `/xnat`)

You can open `https://multi-x.com/xnat/` in a browser to confirm it loads the XNAT UI.

---

## 3) You get HTML instead of JSON

When validating with `curl`, you might receive an HTML page (e.g. a status page) instead of JSON.

Typical causes:

- Wrong URL path (hitting the UI endpoint, not the REST API)
- Reverse proxy redirects

Suggestions:

- Double-check `base_url`
- Use `curl -i` to inspect response headers (status code / Location / Content-Type)

---

## 4) 500 (Internal Server Error)

XNAT may return 500 in some cases:

- Server-side error
- Unexpected parameters/fields

Suggestions:

1. Run with `--dry-run` first to make sure local files are present
2. Re-run for a single subject to narrow down the problem
3. Ask the XNAT admin to check server logs for the exact failure cause

---

## 5) “Missing files” (local files not present)

If you see:

- `Missing files (require_all_files=true)`

It means at least one subject does not have all three expected files.

Fix options:

- Add the missing files; or
- Set `upload.require_all_files: false` in `config.yaml` to upload whatever exists (still requires at least 1 file)

---

## 6) Upload is slow / large files / timeouts

NIfTI files can be large; slow uploads are normal.

Suggestions:

- Ensure network stability
- For very large datasets (hundreds/thousands of subjects), consider:
  - Uploading in batches
  - Parallel uploads (requires code changes; if you want, we can add a parallelism option)
