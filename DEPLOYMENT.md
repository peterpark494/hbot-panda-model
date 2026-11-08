# 本地部署说明

本仓库用于分享已经完成 20000 次优化器更新的 Panda 六任务模型。
GitHub 只提供文件下载；运行模型、渲染仿真需要你自己的 GPU 主机。

## 获取并还原模型

在本仓库的 Releases 页面选择 `panda-20k-v1`，将四个 `.part001` 至 `.part004`、
`manifest.json` 和 `merge_model_parts.py` 下载到同一目录。分卷不能单独解压。

```bash
python merge_model_parts.py
tar -xf panda_six_tasks_b32_a4_20k_inference.tar
```

脚本会校验每个分卷及合并后的完整 SHA-256；任何校验失败都不能用于部署。
原始 tar 共 6,982,860,800 字节；下载、合并、解压同时保留时请预留约 22GB 空间。
这还不包含 Docker 镜像、环境依赖和场景资产占用。

完整 SHA-256：

```text
6aa6e09511a376d3c7e74f4b3423ca642e7163d4cf68b88c0846486b06052993
```

## 文件包含什么

- 最终模型权重、Panda 推理配置与处理器、URDF。
- Qwen3.5-2B 本地资源；无需从训练服务器复制符号链接目标。
- 打包时的 RoboOrchardLab 和模型 Server 源码。
- 训练配置、完成记录、环境版本信息和 `server.yaml`。

不包含训练数据、优化器检查点、Docker 镜像和仿真场景资产。
本包用于推理，不是完整的断点续训检查点。

## 仿真客户端

优先使用可以直接访问 NVIDIA RTX GPU 的原生 Linux 系统。
RTX 5070 Ti 16GB 是待验证候选硬件，不能保证所有场景都能运行；先做短测。
普通 VMware Workstation 的虚拟显卡不能替代所需的 NVIDIA CUDA/RTX 设备访问。

宿主机先准备兼容 Isaac Sim 5.1 的 NVIDIA 驱动、Docker 和 NVIDIA Container Toolkit。
镜像不能替换宿主驱动。固定镜像为：

```bash
docker pull horizonrobotics/robo_orchard_sim:ubuntu22.04-py3.11-cuda12.8-isaacsim5.1-isaac_lab-v2.3.2-v0.1
```

该镜像包括 Ubuntu 22.04、Python 3.11、CUDA 12.8、Torch 2.7.0、Isaac Sim 5.1、
Isaac Lab 2.3.2 和 cuRobo。项目源码和仿真资产需另外准备。
按主办方启动脚本配置 Vulkan、GPU 和资产挂载，不要只用普通 `docker run` 替代。

- 官方镜像指南：https://github.com/HorizonRobotics/RoboOrchardSim/blob/master/docker/README.md
- 仿真项目及资产指南：https://github.com/HorizonRobotics/RoboOrchardSim
- Isaac Sim 要求：https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html

## 模型服务

模型端与仿真端使用独立 Python 环境。不要为了安装模型依赖覆盖仿真端的 Torch。
训练时模型环境版本见包内 `bundle_metadata.json`，主要是 Python 3.11、Torch 2.8.0+cu128、
Transformers 5.10.2、PyTorch3D 0.7.8、FlashAttention 2.8.3、NumPy 1.26.4，
以及 RoboOrchardCore 0.8.0.dev0。Torch 及 CUDA 扩展还必须支持实际使用的 GPU 架构。

安装包内对应模型及 Server 源码和依赖后，在模型环境执行：

```bash
# 将路径换成你自己的解压位置；路径建议不含空格。
export MODEL_DIR=/absolute/path/to/panda_six_tasks_b32_a4_20k
cd "$MODEL_DIR/code/RoboOrchardLab-master"
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
python -m robo_orchard_server.policy.holobrain.main \
  --model-yaml "$MODEL_DIR/server.yaml" \
  --model-dir "$MODEL_DIR" \
  --device cuda:0 --host 127.0.0.1 --port 18765
```

推理前缀为 `panda_droid_inference`。客户端连接同机 `127.0.0.1:18765`。
模型与仿真分机部署时还需要另行配置安全的网络连接，不能直接使用回环地址。

## 已验证的范围

2026-11-08，在 A10 24GB、Linux 驱动 580.126.09 上，真实模型与官方仿真环境完成过
10 步通信短测及一个叠方块案例（seed 100000，最多 900 步）。
完整案例程序正常退出，任务未完成、得分为 0；不能将程序运行成功理解为任务成功。
尚无完整六任务成功率。本仓库不声称模型已经达到比赛评测要求。

第三方代码和基础模型资源继续遵循各自的上游许可；本说明不为它们重新指定许可。
