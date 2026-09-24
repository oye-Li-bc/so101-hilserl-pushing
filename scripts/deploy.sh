#!/bin/bash
# 起 actor：真机执行策略 + 采集数据。在【终端 2】跑。
# 看策略表现就是看这里 —— lerobot-rollout 接不上 HIL-SERL 策略，原因见 docs/04。
set -e
cd "$(dirname "$0")/.."

PY=~/miniconda3/envs/lerobot/bin/python

"$PY" -m lerobot.rl.actor \
    --config_path configs/train_push_cylinder.json \
    --output_dir=/home/lbc/output_lerobot_train/push_cylinder/actor_logs

# ⚠️ output_dir 必须给，否则有检查点后会撞 FileExistsError（actor 不存检查点，只写日志）
# 停的时候顺序反过来：先停 actor，再停 learner
