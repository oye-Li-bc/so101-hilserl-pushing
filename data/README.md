# 数据集说明

数据集托管在 HuggingFace，不进 GitHub：

| 数据集 | 用途 | 内容 |
|---|---|---|
| `oye-Li-bc/push_cube_v2` | 立方体任务示范 | 12 集 / 984 帧 |
| `oye-Li-bc/push_cylinder_v1` | 圆柱任务示范 | 12 集 / 2,087 帧 |
| `oye-Li-bc/push_cube_probe3` | 立方体探路（量裁剪框） | 1 集整图 |
| `oye-Li-bc/push_cylinder_probe1` | 圆柱探路（量裁剪框） | 1 集整图 |

下载：

```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset
ds = LeRobotDataset("oye-Li-bc/push_cylinder_v1")
```

> 国内建议设 `HF_ENDPOINT=https://hf-mirror.com`。
