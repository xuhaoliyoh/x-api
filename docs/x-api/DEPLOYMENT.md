# X-API · Ubuntu 22.04 部署

> 本机编译，服务器运行。适用于目前的 2 vCPU / 2 GB 阿里云 ECS。

## 架构与文件

```text
浏览器 / API 客户端
        │ HTTP :80（配置域名后升级 HTTPS）
      Nginx
        │ 127.0.0.1:18080
   X-API 容器 ── PostgreSQL 18
        └────── Redis 8
```

| 项目 | 位置或配置 |
|---|---|
| 部署目录 | `/opt/x-api` |
| 私密配置 | `/opt/x-api/.env`，权限 `600` |
| Nginx | `/etc/nginx/sites-available/x-api` |
| 应用 / 数据库 / Redis 内存上限 | 640 / 384 / 96 MiB |
| 持久数据 | `x-api_app-data`、`x-api_postgres-data`、`x-api_redis-data` |
| 日志 | Docker 每容器最多 3 × 10 MB；应用文件日志单文件 10 MB、历史 3 份 |
| 备份 | `/opt/x-api/backups`，每日北京时间约 03:30，保留 14 天 |

数据库和 Redis 不映射宿主机端口。网站入口仅由 Nginx 提供，应用端口仅监听回环。容器设置自动重启，Docker 和 Nginx 随系统启动。

## 1. 在开发机生成部署包

在仓库根目录执行，需要 Go、Node、pnpm 和运行中的 Docker Desktop：

```bash
python3 scripts/build-server.py
```

脚本检查并构建前端，交叉编译 Linux amd64 Go 二进制，创建 `x-api:<提交号>` 镜像，并把应用、PostgreSQL、Redis 三个镜像一起导出到 `.local/deploy/images.tar.gz`。运行镜像包含对应版本的 `pg_dump` / `psql`，以及上游许可证。

构建前先提交代码，保持工作区干净，确保镜像标签可以追溯。不要替换成上游 Sub2API 官方镜像，否则 X-API 的品牌和额度策略不会生效。

## 2. 首次准备服务器

以下针对空白 Ubuntu 22.04；已有 Nginx 站点时，应先检查配置，避免影响现有服务。

```bash
ssh aliyun-99
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 nginx
sudo install -d -m 700 /opt/x-api
sudo systemctl enable --now docker nginx
```

把 `deploy/x-api/.env.example` 复制为私密配置，生成独立的数据库密码、Redis 密码、JWT 密钥和 64 位十六进制 TOTP 密钥，填写管理员邮箱与**至少 8 位**的密码。`XAPI_IMAGE` 使用 `.local/deploy/image.txt` 的值。不要把实际配置提交 Git，也不要在聊天中粘贴配置全文。

本次操作的工作副本保存在开发机 `.local/deploy/server.env`，它与本地开发环境 `.local/environment.json` 相互独立。

```bash
# 开发机执行
scp .local/deploy/server.env aliyun-99:/opt/x-api/.env
scp .local/deploy/images.tar.gz aliyun-99:/opt/x-api/
scp deploy/x-api/compose.yaml deploy/x-api/nginx.conf deploy/x-api/backup.sh \
  deploy/x-api/x-api-backup.service deploy/x-api/x-api-backup.timer aliyun-99:/opt/x-api/
```

```bash
# 服务器执行
cd /opt/x-api
chmod 600 .env
chmod 700 backup.sh
docker load -i images.tar.gz
docker compose config -q
docker compose up -d --wait --wait-timeout 180

install -m 644 nginx.conf /etc/nginx/sites-available/x-api
ln -sfn /etc/nginx/sites-available/x-api /etc/nginx/sites-enabled/x-api
# 仅首次安装且确认它是 Ubuntu 默认欢迎页时，移除默认站点链接：
unlink /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

install -m 644 x-api-backup.service x-api-backup.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now x-api-backup.timer
./backup.sh
```

阿里云安全组需要允许 TCP 80 入站；不要开放 5432、6379 或 18080。域名和证书配置完成后再开放 443。当前 IP 入口使用明文 HTTP，适合先验收；正式提供用户登录和 API 服务前配置 HTTPS，并使用更强的管理员密码。

管理员初始化成功后，`ADMIN_PASSWORD` 不会在重启时覆盖已有账号密码。后续在个人设置修改密码；初次初始化留下的明文密码可从 `.env` 移除，同时把 `AUTO_SETUP` 改为 `false`，再重建应用容器。

## 3. 验收与日常运维

```bash
cd /opt/x-api
docker compose ps
curl -fsS http://127.0.0.1/health
docker compose logs --tail 100 app
docker stats --no-stream
systemctl list-timers x-api-backup.timer
```

还需要从服务器外部访问首页、注册页和登录页，并验证管理员登录。首次管理后台会显示上游管理员合规确认，需要管理员本人阅读后决定；部署过程不替你接受协议。

模型上游是独立配置步骤：按 [管理指南](ADMIN.md) 添加真实模型与供应商凭据、给用户分配额度，再测试真实推理。没有上游凭据时，部署成功不代表模型已经可用。

## 4. 更新与回退

1. 在开发机提交改动并重新执行构建脚本。
2. 在服务器执行 `/opt/x-api/backup.sh`，把本次备份复制到服务器以外的安全位置。
3. 上传新镜像包，执行 `docker load -i images.tar.gz`。
4. 修改 `.env` 中 `XAPI_IMAGE` 为新标签，保留原来的数据库密码、JWT 密钥和数据卷。
5. 执行 `docker compose up -d --wait --wait-timeout 180`，再进行内外网验收。

不涉及不兼容数据库迁移时，可将镜像标签改回旧版本后重建应用。若新版变更了数据库结构，先核对迁移兼容性；不能只退镜像就假定数据也已回退。

**不要使用 `docker compose down -v` 或清理项目数据卷。** 它会删除用户、额度、密钥和上游配置。

## 5. 备份与恢复

每日备份包含 PostgreSQL 自定义格式转储、应用数据目录及 `.env` / Compose。Redis 用于缓存与运行状态，保留数据卷，但不作为长期业务数据的唯一备份。

```bash
# 手动备份
sudo /opt/x-api/backup.sh

# 从开发机复制已选定的备份，文件含密钥，应存入受保护目录
scp aliyun-99:/opt/x-api/backups/具体时间.tar.gz .local/deploy/
```

同机备份只能应对误操作，不能覆盖整盘或整机丢失；目前未配置异地自动备份。

恢复时先停应用并额外备份现状；将选定备份解压到权限 `700` 的目录，使用备份中的连接密钥，向**新的空数据库**执行 `pg_restore --no-owner --no-acl`。应用数据恢复到单独数据卷并确认 UID 1000 可写。验证用户数量、额度和上游解密后，再切换应用到恢复的数据。不要在未检查备份的情况下覆盖线上数据库。

可先只读检查转储目录：

```bash
docker compose exec -T postgres pg_restore --list < /安全路径/database.dump
```
