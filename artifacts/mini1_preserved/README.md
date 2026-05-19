# mini1 保留产物（迁移后中间数据已删）

本目录在旧 Ubuntu 服务器清场前从 workspace / shared 盘导出，**可安全进 Git**（仅文本，无 `result.h5` / parquet）。

| 路径 | 内容 |
|------|------|
| `pool/factor_zoo_pool.csv` | 历史因子池表达式（~220 条） |
| `pool/merged_pool.jsonl` | 假设（hypothesis）与相关条目 |
| `pool/merged_pool_context.md` | 假设/表达式摘要（供 planning 参考） |
| `pool/five_factors_v4pro.csv` | 精选因子子集 |
| `all_factors_library.json` | 带假设、回测指标、元数据的因子库（最新 12 条详表） |
| `workspace_factors_extracted.csv` | 从 `rdagent_workspace` 各目录 `factor.py` 解析的表达式 |
| `mafs_scripts/` | MAFS5140 启停、`env.sh`、监控脚本副本 |

新机恢复：复制 `mafs_scripts` 回 `MAFS5140-Spring2026-Project/scripts/`，数据仍须单独 `rsync` `train.parquet` 与 Qlib（见仓库根 `README_MIGRATION.md`）。
