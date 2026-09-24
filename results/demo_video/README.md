# 演示视频

完整版视频体积大、不进仓库，放 B 站 / 网盘，README 里放外链。

## 各种形式怎么选

| 形式 | 优点 | 缺点 | 用在哪 |
|---|---|---|---|
| **动画 WebP** | 体积只有 GIF 的 1/5，颜色好 | 极老客户端不认 | ✅ README 内嵌首选（本仓库 `assets/demo.webp` 2.5 MB）|
| GIF | 到处都能自动播放 | 又大又糊（256 色）| 兼容性兜底（本仓库 `assets/demo.gif` 6.9 MB）|
| MP4 放仓库 | 清晰、有声音 | 不会自动播放，点进去才播 | 想连原始文件一起给 |
| MP4 外链（B站/网盘）| 清晰、不占仓库 | 要跳出去看 | ✅ 完整版演示 |
| 多帧拼图 | 一张图看完整过程 | 不是视频 | 补一张"过程总览" |

## 本项目的文件

| 文件 | 内容 |
|---|---|
| `policy_21000_full.mp4` | ✅ **完整原视频**（67 秒 / 13.3 MB，6 次测试全程无剪辑）|
| `assets/demo.webp` | 前 10 秒原速动图（README 内嵌用，1.8 MB）|
| `results/training_curves/loss_actor.png` | Actor 损失曲线（导出自 wandb）|
| `results/training_curves/loss_critic.png` | Critic 损失曲线（导出自 wandb）|

原始素材在本机：`~/Projects/AI-Study/hilserl/demo_videos/`
