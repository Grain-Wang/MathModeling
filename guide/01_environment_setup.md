# 环境配置

## 标准环境

默认使用 Conda 环境：

```text
math_modeling
```

激活：

```bash
conda activate math_modeling
```

## 初次配置

优先根据仓库中的环境文件创建或更新：

```bash
conda env create -f environment/environment.yml
```

已有环境时，按环境说明补齐依赖。

## 依赖规则

1. 不把项目依赖安装到 `base`。
2. 新依赖必须安装到 `math_modeling`。
3. 安装前先确认现有环境是否已经包含。
4. 新增依赖后更新环境记录。
5. 正式比赛期间避免引入未经演练的高风险依赖。

## 快速检查

至少确认：

```bash
python --version
python -c "import numpy, pandas, scipy"
```

如项目使用 GPU，再检查：

```bash
nvidia-smi
```

## 环境异常处理

记录以下信息：

- 报错命令；
- Python 和包版本；
- 操作系统；
- 完整报错；
- 已尝试的修复。

> 后续可在此增加常用包清单和一键环境检查脚本。
