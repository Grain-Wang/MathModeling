# `math_modeling` Conda 环境

本目录记录仓库默认 Python 环境。当前清单来自本机已存在且通过导入冒烟测试的 `math_modeling` 环境，而不是根据算法清单推测生成。

## 基准状态

- 采集日期：2026-09-04
- 操作系统：Windows
- Conda：25.5.1
- Python：3.11.11
- 环境名称：`math_modeling`
- 主环境文件：`environment/environment.yml`
- pip 兼容清单：`environment/requirements.txt`

`environment.yml` 固定直接依赖版本，但不包含机器专属 `prefix` 或 Conda 构建号。它用于跨机器重建功能等价环境，不保证所有底层二进制逐字节相同；若正式比赛需要完全锁定，应在目标平台生成并测试 `conda-lock` 文件。

## 创建环境

在仓库根目录执行：

```powershell
conda env create --file environment/environment.yml
conda activate math_modeling
```

如果同名环境已经存在，先检查差异，再按需更新：

```powershell
conda env update --name math_modeling --file environment/environment.yml
```

`--prune` 会移除清单外依赖，不应在未检查现有项目依赖时直接使用。

## 当前核心能力

| 用途 | 包 |
|---|---|
| 数值与数据 | NumPy、pandas、SciPy |
| 机器学习 | scikit-learn |
| 基础绘图 | matplotlib |
| Excel | openpyxl、xlrd |
| PDF / DOCX | PyMuPDF、python-docx |
| 图像读取 | OpenCV（pip 安装） |
| 配置与资料 | PyYAML、python-dotenv、requests、jsonschema、bibtexparser |
| Notebook / 锁定工具 | ipykernel、conda-lock |

## 已验证的冒烟测试

以下命令使用指定环境，不依赖当前 shell 是否已经激活：

```powershell
conda run -n math_modeling python -c "import numpy, pandas, scipy, sklearn, matplotlib, openpyxl, xlrd, fitz, docx, cv2, bibtexparser, jsonschema, yaml, dotenv, requests, conda_lock; print('smoke=PASS')"
```

2026-09-04 的实际结果为 `smoke=PASS`。核心版本为：NumPy 2.4.4、pandas 3.0.2、SciPy 1.17.1、scikit-learn 1.7.1、matplotlib 3.11.0、openpyxl 3.1.5、PyMuPDF 1.28.0、python-docx 1.2.0、OpenCV 4.13.0。

## 当前未包含的可选依赖

下列包在采集时不属于当前环境，不应假装可用：

- statsmodels、seaborn；
- XGBoost、LightGBM；
- CVXPY、OR-Tools；
- SymPy、PyTorch。

只有在赛题路线确实需要时才添加。新增依赖后必须：

1. 安装到 `math_modeling`，不得安装到 `base`；
2. 更新 `environment.yml` 和本 README；
3. 重新执行冒烟测试；
4. 在当前项目日志中记录用途、版本和验证结果。

## `requirements.txt` 的定位

`requirements.txt` 是无 Conda 条件下的 pip 兼容参考，不是仓库的首选恢复方式。由于部分科学计算包在不同平台上的二进制分发不同，正式演练优先使用 Conda 清单。

## 已知待办

仓库级 `scripts/verify_environment.py` 当前仍为空；在它实现前，以本 README 的 `conda run` 命令作为人工验证入口。完成脚本后，应让其输出 Python/依赖版本、核心导入结果和可选能力，不得自动安装或修改环境。
