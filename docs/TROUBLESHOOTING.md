# Troubleshooting / 常见报错排查

这份文档主要帮助你在批量上传时快速定位问题。

---

## 1) 401 / 403（未授权 / 无权限）

典型表现：

- HTTP 401 Unauthorized
- HTTP 403 Forbidden

排查建议：

1. 检查 alias/secret 是否正确
2. 检查该账号是否对目标 Project 有权限（至少要能创建 subject 并上传 resource）
3. 如果你之前把 secret 泄露到日志/聊天，建议在 XNAT 里撤销旧 key，重新生成一对

---

## 2) 404（资源不存在 / base_url 错误）

常见原因是 `xnat.base_url` 写错。

例子：

- ✅ 正确：`https://multi-x.com/xnat`
- ❌ 错误：`https://multi-x.com/`（缺少 `/xnat`）
- ❌ 错误：`https://multi-x.com/xnat/xnat`（重复了 `/xnat`）

你可以用浏览器打开 `https://multi-x.com/xnat/` 看看是否能进入 XNAT UI。

---

## 3) 返回 HTML 而不是 JSON

有时你用 `curl` 验证接口，会看到返回的是 HTML 页面（比如一个 status page），不是 JSON。

典型原因：

- URL 路径写错，访问到了 Web 页面而不是 REST API
- 服务器反向代理/跳转导致

建议：

- 用浏览器确认 `base_url`
- 用 `curl -i` 看响应头（状态码/Location/Content-Type）

---

## 4) 500（服务器内部错误）

XNAT 在某些情况下可能返回 500：

- 服务器端异常
- 上传的参数/字段不符合预期

建议：

1. 先用 `--dry-run` 确认本地文件都齐全
2. 尝试只对一个 subject 重跑（缩小范围）
3. 联系 XNAT 管理员查看 server logs

---

## 5) “Missing files” / 本地缺文件

如果你看到：

- `Missing files (require_all_files=true)`

说明某个 subject 在三类目录下没有都齐全。

解决方案：

- 补齐缺失文件；或
- 将 `config.yaml` 里 `upload.require_all_files: false`，允许缺哪个就跳过哪个（至少要有一个文件存在）。

---

## 6) 上传很慢 / 大文件超时

NIfTI 通常很大，上传慢是正常的。

建议：

- 确保网络稳定
- 如果你有大量 subject（几百/几千），可以考虑：
  - 分批上传
  - 并行上传（需要改代码；如果你需要我可以帮你加一个并行参数）
