#!/usr/bin/env python3
"""验证：两份新配置能不能被 draccus 按 learner/actor 的真实链路解析。

为什么必须这么验：draccus 的 ChoiceRegistry 靠【import 副作用】注册类型，
所以验证时必须 import 与入口完全一致的模块集合，否则会假报"未知类型"。
"""
import sys

sys.argv = [sys.argv[0]]  # 防 draccus 抢 argv

import logging

logging.disable(logging.CRITICAL)

from pathlib import Path

import draccus

CFG = Path("/home/lbc/Projects/AI-Study/hilserl/configs/official")
ok = True


def ck(name, cond, got=""):
    global ok
    ok &= bool(cond)
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  {got}" if got else ""))


# ── 与 learner.py / actor.py / gym_manipulator.py 一致的 import 集合 ──
from lerobot.cameras import opencv  # noqa: F401,E402
from lerobot.robots import so_follower  # noqa: F401,E402
from lerobot.teleoperators import gamepad, keyboard, so_leader  # noqa: F401,E402

print("=" * 74)
print("① 训练配置 train_push_cube.json（learner / actor 共用）")
print("=" * 74)
from lerobot.rl.train_rl import TrainRLServerPipelineConfig  # noqa: E402

p = CFG / "train_push_cube.json"
try:
    cfg = draccus.parse(config_class=TrainRLServerPipelineConfig, config_path=p)
    ck("draccus 解析成功", True, type(cfg).__name__)
    ck("algorithm.discount == 0.97", cfg.algorithm.discount == 0.97,
       f"实际 {cfg.algorithm.discount}")
    print(f"     algorithm.discount      = {cfg.algorithm.discount}")
    print(f"     algorithm.grad_clip_norm= {cfg.algorithm.grad_clip_norm}")
    print(f"     policy.latent_dim       = {cfg.policy.latent_dim}")
    print(f"     policy.storage_device   = {cfg.policy.storage_device}")
    print(f"     policy.online_steps     = {cfg.policy.online_steps}")
    print(f"     policy 动作维           = "
          f"{cfg.policy.output_features['action'].shape}")
    print(f"     env.robot.cameras       = {list(cfg.env.robot.cameras)}")
    print(f"     env.teleop.type         = {cfg.env.teleop.type}")
    print(f"     env.processor.reset     = "
          f"control_time_s={cfg.env.processor.reset.control_time_s}, "
          f"reset={cfg.env.processor.reset.fixed_reset_joint_positions}")
    ik = cfg.env.processor.inverse_kinematics
    print(f"     step_sizes              = {ik.end_effector_step_sizes}")
    print(f"     bounds                  = {ik.end_effector_bounds}")
    ck("相机只剩 front", list(cfg.env.robot.cameras) == ["front"])
    ck("动作维 = [3]", tuple(cfg.policy.output_features["action"].shape) == (3,))
    ck("teleop = keyboard_ee", cfg.env.teleop.type == "keyboard_ee")
    ck("reset 位置已写入", cfg.env.processor.reset.fixed_reset_joint_positions ==
       [-41.32, 43.34, -40.88, 90.64, -32.22, 0.79])
    ck("围栏 = 重测值（x,y 第3次；z 上界取第1次 0.0589 以包住起始姿势）", ik.end_effector_bounds ==
       {"min": [0.1076, -0.1023, -0.0294], "max": [0.2965, 0.2091, 0.0589]},
       f"实际 {ik.end_effector_bounds}")

    # ★ FK 自检：起始姿势必须落在围栏内。见过三次围栏没包住起始姿势（每集开局
    #   被 np.clip 硬钳 → IK 猛拉 → 手臂抖一下，且策略看到的状态/动作对不上）。
    try:
        import numpy as _np

        from lerobot.model import RobotKinematics as _RK

        _kin = _RK(
            urdf_path=ik.urdf_path,
            target_frame_name=ik.target_frame_name,
            joint_names=["shoulder_pan", "shoulder_lift", "elbow_flex",
                         "wrist_flex", "wrist_roll", "gripper"],
        )
        _ee = _np.asarray(_kin.forward_kinematics(_np.array(
            cfg.env.processor.reset.fixed_reset_joint_positions, dtype=float)))[:3, 3]
        _lo = _np.array(ik.end_effector_bounds["min"])
        _hi = _np.array(ik.end_effector_bounds["max"])
        _inside = bool(_np.all(_ee >= _lo) and _np.all(_ee <= _hi))
        _ax = ("x", "y", "z")
        _over = [
            f"{_ax[i]}: 起始 {_ee[i]:+.4f} vs 围栏 [{_lo[i]:+.4f},{_hi[i]:+.4f}]"
            f" 越 {(abs(_ee[i] - _lo[i]) if _ee[i] < _lo[i] else abs(_ee[i] - _hi[i])) * 100:.2f}cm"
            for i in range(3) if _ee[i] < _lo[i] or _ee[i] > _hi[i]
        ]
        ck("★ 起始姿势 EE 在围栏内（FK 自检）", _inside,
           "; ".join(_over) or f"EE={_np.round(_ee, 4).tolist()}")
    except Exception as _e:
        ck("★ 起始姿势 EE 在围栏内（FK 自检）", False, f"{type(_e).__name__}: {str(_e)[:110]}")
    ck("步长 = 用户原值 0.009/0.009/0.01",
       {k: float(v) for k, v in ik.end_effector_step_sizes.items()} ==
       {"x": 0.009, "y": 0.009, "z": 0.01},
       f"实际 {ik.end_effector_step_sizes}")
    ck("裁剪框 = 官方工具选出值",
       {k: list(v) for k, v in
        cfg.env.processor.image_preprocessing.crop_params_dict.items()} ==
       {"observation.images.front": [225, 679, 805, 966]},
       f"实际 {cfg.env.processor.image_preprocessing.crop_params_dict}")
    # dataset_stats：归一化的来源（actor.py:288 / learner.py:338 消费）
    ds = cfg.policy.dataset_stats
    ck("dataset_stats 三个键齐全",
       set(ds) == {"observation.images.front", "observation.state", "action"},
       f"实际 {sorted(ds)}")
    ck("state min/max 各 18 维（6关节+6速度+6电流）",
       len(ds["observation.state"]["min"]) == 18
       and len(ds["observation.state"]["max"]) == 18)
    ck("action min/max 各 3 维且为理论 ±1",
       ds["action"]["min"] == [-1.0, -1.0, -1.0]
       and ds["action"]["max"] == [1.0, 1.0, 1.0],
       f"{ds['action']}")
    ck("front mean/std 各 3 通道",
       len(ds["observation.images.front"]["mean"]) == 3
       and len(ds["observation.images.front"]["std"]) == 3)
    ck("图像统计不是 ImageNet 常数（未启用 imagenet stats）",
       abs(ds["observation.images.front"]["mean"][0] - 0.485) > 1e-3,
       f"mean[0]={ds['observation.images.front']['mean'][0]:.4f}")

    # ★ dataset_stats 必须【真的等于】当前数据集的 meta/stats.json。见过两次差点拿旧相机/
    #   旧数据集的统计值开训（归一化尺度不对 = 白训），所以做成硬断言，且数据集缺失也报红。
    try:
        import json as _json
        from pathlib import Path as _P

        def _flat(v):
            out = []
            for x in v:
                out.extend(_flat(x)) if isinstance(x, (list, tuple)) else out.append(float(x))
            return out

        def _close(a, b):
            a, b = _flat(a), _flat(b)
            return len(a) == len(b) and all(abs(x - y) < 1e-4 for x, y in zip(a, b))

        _f = _P.home() / ".cache/huggingface/lerobot" / cfg.dataset.repo_id / "meta" / "stats.json"
        if not _f.exists():
            ck("★ dataset_stats 与数据集一致（数据集须已录）", False, f"缺 {_f}")
        else:
            _st = _json.loads(_f.read_text())
            ck("★ 图像 stats 与数据集 stats.json 一致",
               _close(ds["observation.images.front"]["mean"], _st["observation.images.front"]["mean"])
               and _close(ds["observation.images.front"]["std"], _st["observation.images.front"]["std"]))
            ck("★ state stats 与数据集 stats.json 一致",
               _close(ds["observation.state"]["min"], _st["observation.state"]["min"])
               and _close(ds["observation.state"]["max"], _st["observation.state"]["max"]))
    except Exception as _e:
        ck("★ dataset_stats 与数据集一致", False, f"{type(_e).__name__}: {str(_e)[:110]}")
    ck("dataset.repo_id 指向录好的数据集",
       cfg.dataset.repo_id == "oye-Li-bc/push_cube_v2", cfg.dataset.repo_id)
except Exception as e:
    ck("draccus 解析成功", False, f"{type(e).__name__}: {str(e)[:300]}")

print()
print("=" * 74)
print("② 采数据配置 record_push_cube.json（gym_manipulator 入口的配置类）")
print("=" * 74)
# 注意：gym_manipulator.py 自己定义了一个 DatasetConfig（:87），与
# configs/default.py 里的同名类【不是同一个】。这里必须用它自己的。
try:
    from lerobot.rl.gym_manipulator import GymManipulatorConfig  # noqa: E402

    cfg2 = draccus.parse(config_class=GymManipulatorConfig,
                         config_path=CFG / "record_push_cube.json")
    ck("draccus 解析成功", True, type(cfg2).__name__)
    ck("mode == record", cfg2.mode == "record", f"实际 {cfg2.mode!r}")
    ck("相机只剩 front", list(cfg2.env.robot.cameras) == ["front"],
       f"实际 {list(cfg2.env.robot.cameras)}")
    ck("teleop = keyboard_ee", cfg2.env.teleop.type == "keyboard_ee")
    print(f"     dataset.repo_id          = {cfg2.dataset.repo_id}")
    print(f"     dataset.task             = {cfg2.dataset.task}")
    print(f"     dataset.num_episodes     = {cfg2.dataset.num_episodes_to_record}")
    print(f"     reset 位置               = "
          f"{cfg2.env.processor.reset.fixed_reset_joint_positions}")
    print(f"     control_time_s           = {cfg2.env.processor.reset.control_time_s}")
    print(f"     step_sizes               = "
          f"{cfg2.env.processor.inverse_kinematics.end_effector_step_sizes}")
    print(f"     crop                     = "
          f"{cfg2.env.processor.image_preprocessing.crop_params_dict}")
    ck("reset 位置已写入", cfg2.env.processor.reset.fixed_reset_joint_positions ==
       [-41.32, 43.34, -40.88, 90.64, -32.22, 0.79])
    ck("围栏 = 重测值（x,y 第3次；z 上界取第1次 0.0589 以包住起始姿势）",
       cfg2.env.processor.inverse_kinematics.end_effector_bounds ==
       {"min": [0.1076, -0.1023, -0.0294], "max": [0.2965, 0.2091, 0.0589]},
       f"实际 {cfg2.env.processor.inverse_kinematics.end_effector_bounds}")
    ck("步长 = 用户原值 0.009/0.009/0.01",
       {k: float(v) for k, v in
        cfg2.env.processor.inverse_kinematics.end_effector_step_sizes.items()} ==
       {"x": 0.009, "y": 0.009, "z": 0.01})
    ck("crop 只含 front", list(
        cfg2.env.processor.image_preprocessing.crop_params_dict) ==
        ["observation.images.front"])
    ck("裁剪框 = 官方工具选出值",
       {k: list(v) for k, v in
        cfg2.env.processor.image_preprocessing.crop_params_dict.items()} ==
       {"observation.images.front": [225, 679, 805, 966]},
       f"实际 {cfg2.env.processor.image_preprocessing.crop_params_dict}")
except Exception as e:
    ck("draccus 解析成功", False, f"{type(e).__name__}: {str(e)[:300]}")

print()
print("=" * 74)
print("③ 探路配置 record_push_cube_probe.json（存原图，供官方裁剪工具用）")
print("=" * 74)
try:
    from lerobot.rl.gym_manipulator import GymManipulatorConfig as _G  # noqa: E402

    cfg3 = draccus.parse(config_class=_G,
                         config_path=CFG / "record_push_cube_probe.json")
    ck("draccus 解析成功", True, type(cfg3).__name__)
    ip = cfg3.env.processor.image_preprocessing
    ck("crop_params_dict 为空（不裁）",
       not ip.crop_params_dict, f"实际 {ip.crop_params_dict}")
    ck("resize_size 为 None（存原图→工具显示 1920x1080）",
       ip.resize_size is None, f"实际 {ip.resize_size}")
    ck("repo_id 独立", cfg3.dataset.repo_id == "oye-Li-bc/push_cube_probe3",
       cfg3.dataset.repo_id)
    ck("集数 = 1", cfg3.dataset.num_episodes_to_record == 1)
    ck("reset / 围栏 / 步长 与正式配置一致",
       cfg3.env.processor.reset.fixed_reset_joint_positions ==
       [-41.32, 43.34, -40.88, 90.64, -32.22, 0.79]
       and cfg3.env.processor.inverse_kinematics.end_effector_bounds ==
       {"min": [0.1076, -0.1023, -0.0294], "max": [0.2965, 0.2091, 0.0589]}
       and {k: float(v) for k, v in
            cfg3.env.processor.inverse_kinematics.end_effector_step_sizes.items()} ==
       {"x": 0.009, "y": 0.009, "z": 0.01})
except Exception as e:
    ck("draccus 解析成功", False, f"{type(e).__name__}: {str(e)[:300]}")

print()
print("=" * 74)
print(f"结果：{'全部通过' if ok else '有失败'}")
print("=" * 74)
sys.exit(0 if ok else 1)
