# 数据恢复说明（重要）

## 事故说明

清场时误将**运行必需数据**与**中间产物**一并删除，且**未先上传**到 GitHub Releases / 对象存储：

| 已删除（本机不可恢复） | 约大小 | 性质 |
|------------------------|--------|------|
| `MAFS5140.../mini1/train.parquet` | ~501MB | **必需** — 因子计算唯一输入 |
| `mini1/validation.parquet` | ~7MB | 可选 |
| `QuantaAlpha/data/qlib/mini1_us_5min/` | ~4.2GB | **必需** — Qlib 回测 |
| `rdagent_workspace` / `quanta_results` | ~109GB | 中间产物（可不要） |

GitHub `mini1-migration` 上**仅有**：代码补丁、因子表达式、假设、`dump_bin.py` 等脚本；**不含**上述 parquet/Qlib 二进制。

## 请从以下来源找回 `train.parquet`

1. **本机/笔记本**是否曾 `scp` 或下载过 `mini1/`
2. 同目录是否还有 **`train0.parquet` / `validation0.parquet`**（课程原版，可替代重建）
3. 课程方 / 同学 / NAS / 云盘作业包
4. **云厂商磁盘快照**（若 VPS 有自动备份，联系管理员按时间点恢复 `chenyuanhengWorkspace`）

## 找回 parquet 后重建 Qlib（无需旧 4GB 目录）

```bash
# 假设已 clone mini1-migration 且 MAFS 项目在 $CHY_WS
pip install pandas pyarrow  # 在 quantsociety_backend 中

python $CHY_WS/MAFS5140-Spring2026-Project/scripts/build_mini1_qlib_5min.py \
  --proj $CHY_WS/MAFS5140-Spring2026-Project \
  --qlib-dir $CHY_WS/QuantaAlpha/data/qlib/mini1_us_5min
```

脚本会从 `mini1/train.parquet` + `validation.parquet` 生成完整 `mini1_us_5min`。

## 上传到 GitHub（今后）

大文件请用 **GitHub Release** 或网盘链接写在 `README_MIGRATION.md`，**删除磁盘前必须先确认 off-site 有一份**。
