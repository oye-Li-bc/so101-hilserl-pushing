#!/bin/bash
# 跑真机之前先过一遍配置自检（围栏/步长/起始姿势/裁剪框/dataset_stats 一致性）
set -e
cd "$(dirname "$0")/.."

# ⚠️ 必须清掉 PYTHONPATH：环境里若有一个指向别的 Python 版本的路径，
#    会串来不兼容的 numpy（表现为 "Importing the numpy C-extensions failed"）
unset PYTHONPATH

PY=~/miniconda3/envs/lerobot/bin/python
"$PY" verify/verify_push_configs.py
