#!/bin/bash
# 录制演示数据（12 条）。跑之前务必确认三件套已经量准：docs/02-数据采集.md
set -e
cd "$(dirname "$0")/.."

PY=~/miniconda3/envs/lerobot/bin/python

"$PY" -m lerobot.rl.gym_manipulator \
    --config_path configs/record_push_cylinder.json

# 键位：空格=接管/交还  w/s前后  a/d左右  r/f升降  o/c夹爪  y=成功存盘  u=重录
# ⚠️ 推到位后停约半秒再按 y；千万别让它跑满 20 秒时限（跑满 = 没有成功标记 = 白录）
