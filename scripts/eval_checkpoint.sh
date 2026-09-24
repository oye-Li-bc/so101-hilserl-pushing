#!/bin/bash
# 冻结某个检查点做评估：learner 只放一次权重、之后不学习也不推新参数。
# 原理：learner.py:342 循环前推一次；:412-414 池子不够就 continue
# 用法：bash scripts/eval_checkpoint.sh 0021000
set -e
cd "$(dirname "$0")/.."

STEP=${1:?用法: bash scripts/eval_checkpoint.sh <步数，如 0021000>}
CKPT=/home/lbc/output_lerobot_train/push_cylinder/sac_v1/checkpoints/$STEP/pretrained_model
PY=~/miniconda3/envs/lerobot/bin/python

[ -d "$CKPT" ] || { echo "找不到检查点: $CKPT"; exit 1; }

echo "冻结在 $STEP 步，评估期间请【不要碰键盘】"
"$PY" -m lerobot.rl.learner \
    --config_path configs/train_push_cylinder.json \
    --policy.pretrained_path="$CKPT" \
    --policy.online_step_before_learning=1000000000 \
    --output_dir=/home/lbc/output_lerobot_train/push_cylinder/eval_$STEP \
    --job_name=eval_$STEP \
    --wandb.enable=false
