#!/bin/bash
# 跑真机之前先过一遍配置自检（围栏/步长/起始姿势/裁剪框/dataset_stats 一致性）
set -e
cd "$(dirname "$0")/.."

PY=~/miniconda3/envs/lerobot/bin/python
"$PY" verify/verify_push_configs.py
