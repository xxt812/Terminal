# Terminal CodingAgent —— 项目文档总目录

> 在 [Pi Agent Harness](https://github.com/earendil-works/pi)（自扩展 coding agent）基础上，用 **Python 技术栈** 落地五项差异化能力：多 Agent 协作与可视化、跨会话长期记忆、LSP+AST 双引擎代码索引、结构化分层 Token 压缩、MCP+Skill 接入。中间件钩子机制作为横切能力贯穿五项差异化。

---

## 文档清单

| 顺序 | 文档 | 用途 |
|:---:|---|---|
| 01 | [产品需求文档](01_产品需求文档.md) | PRD：功能边界、非功能指标、验收标准 |
| 02 | [系统架构文档](02_系统架构文档.md) | 技术架构：分层、模块、数据流、关键决策 |
| 03 | [项目开发文档](03_项目开发文档.md) | 实施约定：环境、目录、编码规范、构建与测试 |
| 04 | [核心模块设计](04_核心模块设计.md) | 模块设计：5 大差异化模块的接口、流程、可执行示例 |
| 05 | [测试与运维手册](05_测试与运维手册.md) | 质量门禁：测试金字塔、CI/CD、部署与运维 |

阅读顺序按编号排列。前两份定义"做什么"与"怎么搭"，后三份为落地实施、模块细节、运维保障。

---

## 五项差异化能力

| # | 能力 | 关键设计 | 详见 |
|:---:|---|---|---|
| 1 | 多 Agent 协作与可视化 | LangGraph StateGraph + 角色专家池（Orchestrator/Coder/Reviewer/Tester/Researcher）+ Maker-Checker 辩论 + Streamlit 编排面板 | 04 §1 |
| 2 | 跨会话长期记忆与知识积累 | 短期 LangGraph Checkpointer（SQLite） + 长期 ChromaDB 向量命名空间 + 后台 LLM 提炼 + 经验规则库 | 04 §2 |
| 3 | LSP + AST 双引擎索引 | tree-sitter 语法广度 + pygls/pyright 语义深度，AST 快速过滤 → LSP 精确确认 + 上下文 Token 预算注入 | 04 §3 |
| 4 | 结构化分层 Token 压缩与持久化 | L1 摘要 / L2 细节 / L3 归档 + SessionState 序列化 + Intent→Context→Action→Observe→Adjustment 五段闭环 | 04 §4 |
| 5 | MCP + Skill 接入 | MCP 官方 Python SDK 桥接（stdio/SSE）+ Skill 三层懒加载（SKILL.md + scripts/references）+ 标准库 Skills | 04 §5 |

中间件钩子（大模型19）作为横切能力贯穿上述五项，实现观测、拦截、转换的可插拔。

## 与原 pi 项目的对应关系

| TCA 模块 | 原 pi 对应 | 差异化 |
|---|---|---|
| LangGraph 多 Agent 编排 | pi-agent-core / pi-orchestrator | 新增：角色专家池、协调/辩论、可视化 |
| 跨会话记忆 + 知识积累 | JSONL 会话 | 新增：短期 Checkpointer + 长期 ChromaDB 向量库 |
| LSP+AST 双引擎索引 | grep / read 工具 | 新增：tree-sitter + pygls 代码感知 |
| 分层 Token 压缩 + Loop | compaction | 新增：摘要/细节/归档三级 + 五段闭环 |
| MCP + Skill 接入 | extensions / skills | 升级：统一协议 + 结构化封装 |
| LangChain | pi-ai | 多提供商 LLM 抽象（对齐） |

---

## 技术栈

| 层面 | 技术 | 版本约束 |
|---|---|---|
| 语言 | Python | 3.11+ |
| 多 Agent 编排 | LangGraph | `==0.2.x`（锁定，详见 PRD §9.2） |
| LLM 多提供商抽象 | LangChain | `>=0.3` |
| 短期记忆 / 会话状态 | LangGraph Checkpointer + SQLite | 随 LangGraph |
| 长期记忆 / 知识积累 | ChromaDB（嵌入式向量库） | `>=0.5` |
| 结构化存储 | SQLite | 3.35+ |
| AST 语法索引 | tree-sitter | `>=0.22` |
| LSP 语义索引 | pygls + pyright | pygls `>=1.3` / pyright `>=1.1` |
| 统一工具协议 | MCP 官方 Python SDK | `>=1.0` |
| Skill 引擎 | 自研 Markdown 加载器 | — |
| 可视化仪表盘 | Streamlit | `>=1.30` |
| API / RPC | FastAPI | `>=0.110` |
| 配置 | pydantic + python-dotenv + pyyaml | pydantic v2 / dotenv `>=0.21` / pyyaml `>=6.0` |
| 测试 | pytest | `>=8.0` |

版本约束的最终一致口径以架构文档 §3 与开发文档 §2.2.3 为准。

---

## 交付里程碑

| 里程碑 | 时间区间 | 目标 | 验收条件 |
|---|---|---|---|
| **M1 — 基础骨架** | D1~D4 | 跑通 LangGraph 图 + 中间件 + MCP 最小链路 | 多 Agent 单图 + 1 个 MCP 工具 + 2 个钩子可运行 |
| **M2 — 记忆与代码索引** | D5~D8 | 跑通 Checkpointer+ChromaDB 双层记忆 + AST 索引 | 跨会话记忆召回 + 代码符号检索可用 |
| **M3 — 协作与循环** | D9~D12 | 跑通三 Agent Sequential + Token 压缩 + 测试 Loop | 端到端产出三阶段产物 + Loop 自愈 |
| **M4 — 集成验收** | D13~D14 | 跑通可视化 + LSP + 全流程 E2E + 文档收尾 | 全部验收标准通过 |

---

## 参考资料映射

6 份文档中频繁引用"大模型 N"作为外部参考索引，对应到本地 `参考资料/` 目录的文件路径如下：

| 引用名 | 主题 | 本地路径 |
|---|---|---|
| 大模型 18 | 多智能体（MAS） | `参考资料/大模型18-多智能体介绍.md` |
| 大模型 19 | 中间件（钩子） | `参考资料/大模型19-中间件介绍.md` |
| 大模型 20 | MCP 协议 | `参考资料/大模型20-MCP介绍及使用.md` |
| 大模型 21 | Skills 延迟加载 | `参考资料/大模型21-Skills介绍及使用.md` |
| 大模型 22 | Agent 记忆 | `参考资料/大模型22-Agent记忆介绍.md` |
| 大模型 23 | Harness Engineering | `参考资料/大模型23-Harness Engineering介绍.md` |
| 大模型 24 | Loop Engineering | `参考资料/大模型24-Loop Engineering介绍.md` |

引用映射以本表为准；如文件实际命名不一致，以本表路径作为修订依据。

---

## 文档约定

- 示例代码全部使用 Python，模块边界与包导入路径以开发文档 §3 的目录结构为权威方案
- 关键架构与流程使用 Mermaid 可视化
- 每份文档开头说明其在整套文档中的位置、前置依赖与适用范围
- 文档间交叉引用使用相对文件名（如 `02_系统架构文档.md`）