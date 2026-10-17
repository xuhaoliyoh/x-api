# X-API 开发说明

## 改动边界

保留上游 Go 模块名与复杂转发、调度、鉴权实现，X-API 产品层改动集中于：

- `backend/internal/server/middleware/xapi_edition.go`：关闭自助额度入口。
- `backend/internal/service/xapi_catalog.go`：按分组读取明确配置的实际模型。
- `backend/internal/handler/xapi_catalog.go`：登录用户的模型目录和 Chat Completions 模型准入。
- `backend/migrations/246_xapi_defaults.sql`：首次安装默认值，只插入缺失设置。
- `frontend/src/xapi.ts`：第一版页面访问范围。
- `frontend/src/views/HomeView.vue`：X-API 首页。
- `frontend/src/views/user/XAPI*View.vue`：模型目录与接入指南。
- `scripts/local.py`：独立本地生命周期。
- `scripts/smoke.py`：可重复运行的隔离 API 集成验证。

通过 `main` 直接开发，每个完整功能或修复独立提交，使用 `chore` / `feat` / `fix` / `test` / `docs` 前缀。没有自动推送远端的步骤。

## 开发模式

运行本地后端后，可以单独启动 Vite：

```bash
cd frontend
VITE_DEV_PROXY_TARGET=http://127.0.0.1:18080 VITE_DEV_PORT=13000 pnpm dev --host 127.0.0.1
```

开发页访问 `http://127.0.0.1:13000`，API 代理到 18080。普通启动使用嵌入式前端，仅需一个 18080 地址。

修改后端或需要更新嵌入页面时，在根目录执行：

```bash
python3 scripts/local.py build
python3 scripts/local.py restart
```

上游自动发布/CLA 工作流已归档，管理后台的上游二进制更新与回滚入口已关闭，避免覆盖 X-API 自定义代码。升级使用上述构建与重启命令。

数据库与 Redis 由 Docker 运行；应用由本地 Go 构建运行。后续 Ubuntu 部署将单独提供 X-API 镜像，不沿用上游镜像覆盖自定义代码。

## 验证口径

- 前端：TypeScript 检查、语言键检查、登录注册/密钥/个人资料测试、X-API 页面测试、生产构建。
- 后端：X-API 模型目录、权限隔离、账号/密钥相关回归。
- 集成：临时库 + 临时 Redis + 本地 mock，不依赖外部模型账号。
- 浏览器：实际访问本地页面，检查首页、登录注册和导航。

集成测试中的管理员确认状态由 SQL 夹具写入**随机命名的临时库**，不会接受真实管理员的承诺，也不会修改正式库。测试使用临时的模拟模型凭证，完成或失败后都清理数据库与 Redis 容器，日志保留在 `.local/smoke-*/` 便于诊断。

## 当前限制

- 尚未配置真实豆包密钥、验证真实供应商推理；没有订阅账号接入验收。
- 暂未配置邮件服务器。登录后的密码修改可用，邮件找回流程需要 SMTP。
- 第一版重点覆盖标准分组下的 Chat Completions；继承的其他高级协议不作为本版验收范围。
- 继承的支付与订阅源码保留，以便后续开发，但第一版接口和入口均关闭。
- 本地数据库有持久化，自动备份与服务器部署属于下一阶段。
