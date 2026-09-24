#!/bin/bash
# 启动 learner（策略服务器 + 训练）。在【终端 1】跑这个，然后去【终端 2】跑 deploy.sh 起 actor。
#
# ★ 跑之前必须确认：
#   1) wandb 已登录（wandb login），配置里 wandb.enable=true
#      —— 指标只进 wandb，漏开就永远补不上（docs/03 第 2 节）
#   2) output_dir 是干净的
set -e
cd "$(dirname "$0")/.."

# ⚠️ 必须清掉 PYTHONPATH：环境里若有一个指向别的 Python 版本的路径，
#    会串来不兼容的 numpy（表现为 "Importing the numpy C-extensions failed"）
unset PYTHONPATH

PY=~/miniconda3/envs/lerobot/bin/python

# 从零开始
"$PY" -m lerobot.rl.learner \
    --config_path configs/train_push_cylinder.json

# 续训（换成这两行；--resume 必须配 config_path，且命令行覆盖想改的项）
# "$PY" -m lerobot.rl.learner \
#     --config_path=/home/lbc/output_lerobot_train/push_cylinder/sac_v1/checkpoints/last/pretrained_model/train_config.json \
#     --resume=true
