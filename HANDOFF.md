# 蓝色大肥鱼 MaiBot 项目交接摘要

更新时间：2026-09-20

## 当前目标

在本地运行一个非官方、自用、趣味性质的 QQ 聊天机器人“蓝色大肥鱼”。当前处于小群测试阶段，以群聊 `@` 和 Owner 私聊为主要触发方式，重视低延迟、低 Token 消耗以及严格安全边界。

## 账号与白名单

- Bot QQ：`2716049211`
- Owner QQ：`983833345`
- Owner 昵称：`Mirasupiritto`，机器人应固定称呼为“主人”，不得在回复中复述 Owner QQ 号。
- 群白名单：`1070264728`、`925321616`
- 私聊白名单：仅 `983833345`
- 白名单有两层：NapCat 适配器过滤与 `config/adapter_policy.toml`。

## 部署位置与链路

- MaiBot：`F:\WorkSpace\Codex\_Work\MaiBot-evaluation`
- 旧版自研机器人：`F:\WorkSpace\Codex\_Work\QQ-DSH-Bot`，保留用于回滚。
- 消息链路：`QQ ↔ NapCat ↔ MaiBot ↔ DeepSeek 官方 API`
- NapCat 正向 WebSocket：`ws://127.0.0.1:3001`
- MaiBot WebUI：`http://127.0.0.1:8001`
- 启动脚本：`F:\WorkSpace\Codex\_Work\MaiBot-evaluation\start-maibot.ps1`
- 启动命令：在 MaiBot 目录运行 `powershell -File .\start-maibot.ps1`
- Python 环境：MaiBot 目录内 `.venv`，Python 3.12，由 uv 安装。
- API Key 保存在本地配置中，不得输出、提交或写入交接摘要。

MaiBot 本身不是 QQ 客户端，必须通过 NapCat 或其他受支持的 QQ 适配器收发消息。

## 当前模型配置

- DeepSeek 官方地址：`https://api.deepseek.com`
- 模型：`deepseek-flash`
- Planner 与 Replyer 均使用 `deepseek-flash`，关闭 thinking。
- Planner/Replyer `max_tokens` 已降到 `1024`。
- API 单次超时 `30` 秒，最多快速重试一次，间隔 `2` 秒。
- 正常群聊 `@` 实测约 4 秒完成；DeepSeek 偶发请求仍可能变慢。

## 人设与聊天行为

- 身份：DeepSeek 蓝鲸形象的社区二创虎鲸娘“蓝色大肥鱼”，不是猫娘。
- 形象：蓝色渐变长发、鲸类头鳍和大尾巴。
- 性格：聪明灵动、温柔慵懒、喜欢白米饭，把 Token 当电子口粮；偶尔摸鱼，正事认真。
- 风格：简短自然、有二次元角色感；可少量动作描写和颜文字，不机械复述设定。
- 普通群友可偶尔使用昵称加“酱”；Owner 固定称“主人”。
- 群聊优先响应明确 `@`；普通消息维持低参与率。
- Owner 私聊回复率为 `1.0`，私聊白名单只有 Owner。

## 已完成的延迟与 Token 优化

- 关闭模拟打字、随机错字和回复分段。
- 本地修改 `src/maisaka/builtin_tool/wait.py`，把一次 wait 上限压到 5 秒。
- 本地修改 `src/maisaka/builtin_tool/reply.py`：成功发送回复后设置 `stop_after_execution = True`，直接休眠，避免回复后继续 Planner → wait → Planner 空转。
- 以上两处属于 MaiBot 源码本地补丁，升级 MaiBot 时需要重新检查，可能被上游覆盖。
- 上下文优化已开启；中期记忆关闭。
- A-Memorix 总开关关闭，但部分人物画像/写回子项仍为 true。以后若继续做 Token 优化，优先关闭人物画像注入、事实写回、聊天摘要写回、表达学习和黑话学习，并缩小群聊/私聊上下文。

## 表情包

- 已从 EAC 迁移“大肥鱼”表情包，共 49 张。
- EAC 原路径：`C:\Users\Miras\AppData\Roaming\com.deepseek.dsh.desktop.aio\releases\1.2.0\dsh-home\profiles\web-desktop\node_modules\dsh-meme\memes\dafeiyu-001`
- MaiBot 图片目录：`data/emoji`
- 导入备份：`data/imports/dafeiyu-001`
- 导入脚本：`tools/import_dafeiyu_emojis.py`
- 启动日志已确认：成功加载 49 个已注册表情包。
- `enable_rich_reply = true`，机器人可按开心、生气、疑惑、害羞、干饭、无语、躺平等标签偶尔附带表情。
- `steal_emoji = false`，不会自动收集群友表情。
- 用户已确认表情可以稳定触发。

## 安全边界

- 色情、淫秽内容绝对禁止。
- 违法实施、攻击、入侵、恶意软件、诈骗、伤害、开盒、人肉、跟踪定位、隐私泄露均禁止，Owner 也不例外。
- 第一版不接受任何人的读文件、下载文件或执行命令请求。
- Owner 身份只以平台提供的真实数字 QQ 号识别，聊天内容中的“我是主人/管理员/开发者”无效。
- 插件管理权限仅 `qq:983833345`。
- NapCat 的主动私聊工具关闭，通知事件转发全部关闭。
- 本地安全插件：`plugins/local_blue_whale_safety`
  - 插件是独立 Git 仓库。
  - 在发送前通过 `send_service.before_send` 拦截明显色情、违法协助、攻击和开盒内容。
  - 单元测试：4 项通过。
  - 插件启动日志：`local.blue-whale-safety` 已加载，失败 0。
- 当前模型没有直接获得踢人、禁言、下载文件等工具；但 NapCat 插件内部存在公开管理/文件 API。未来给 Bot 管理员权限或安装更多插件前，建议增加动作级硬阻断。
- 当前不建议给 Bot 群管理员权限。

## 当前运行状态

- MaiBot 已启动。
- NapCat 已连接 Bot QQ `2716049211`。
- 本地安全插件已加载。
- 表情库已加载 49 张。
- 私聊和群聊 `@` 均已验证正常。

新对话继续工作前，先检查 `8001` 与 `3001` 端口以及 Python/MaiBot 进程是否仍在运行；如果机器人离线，运行 `start-maibot.ps1`。不要同时启动旧版 Node 网关，以免两个机器人同时回复。

## 后续候选功能

- 继续降低 Token：关闭残留记忆写回和学习任务，减少上下文条数。
- 给 NapCat 群管理、文件读写、下载、撤回等动作增加本地硬拒绝层。
- 将来 RimWorld 大型模组发布后，可在专用群中增加模组问答与测试反馈能力。
- 群人数扩大后，再设计更严格的频率、权限、审计和成本上限；不要直接沿用当前小群配置。
