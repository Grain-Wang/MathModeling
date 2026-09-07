# S3 baseline experiments

本目录保存 G2 已批准的 8 个 S3 实验描述。描述文件是可追溯配置入口；所有模型参数仍以 `../s2_frozen_config.json` 为唯一冻结来源。

统一运行命令：

```powershell
conda run -n math_modeling python src/run_s3_baselines.py --config experiments/s2_frozen_config.json --verify-data-rebuild
```

运行产物只写入 `results/raw/`，不得在 G3 通过前写入 `results/verified/`。
