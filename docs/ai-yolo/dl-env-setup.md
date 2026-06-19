# 如何搭建自己的深度学习开发环境

## 硬件选型：NVIDIA vs Apple Mac Studio

对于个人深度学习开发，目前主流的本地方案是 **NVIDIA 独立显卡（Windows/Linux）** 和 **Apple Silicon Mac Studio**，两者思路完全不同。

---

### NVIDIA 方案

NVIDIA 的优势在于 **CUDA 生态**——几乎所有深度学习框架、论文代码都以 CUDA 为第一目标，遇到问题社区资料最多。

| 型号 | 架构 | 显存 | 参考价（CAD） | 适合场景 |
|------|------|------|-------------|----------|
| RTX 4090 | Ada Lovelace | 24 GB GDDR6X | CA$1,899–$2,299 | 主力训练，大多数 YOLO 任务 |
| RTX 5090 | Blackwell | 32 GB GDDR7 | CA$2,799–$4,500+ | 旗舰训练，速度约为 4090 的 1.5–2 倍 |

**核心优势**
- CUDA 生态覆盖率 100%，pip install 直接能跑
- 训练速度（TFLOPS）目前仍领先 Apple Silicon
- 显存与系统内存独立，显存满了报错清晰
- 多 GPU 扩展方便

**主要短板**
- 需要搭配 Windows 或 Linux 主机，整机成本高
- 功耗大（RTX 4090 满载 ~450W），发热噪音明显
- 不适合移动办公

---

### Apple Mac Studio 方案

Mac Studio 的核心是**统一内存架构（Unified Memory）**：CPU、GPU、Neural Engine 共享同一块内存，没有传统意义上的"显存上限"问题——128 GB 内存就是 128 GB 可用于模型的内存。

| 配置 | 芯片 | 内存 | GPU 核心数 | 参考价（CAD） |
|------|------|------|-----------|-------------|
| 基础款 | M4 Max | 36 GB | 32 核 GPU | CA$2,499 |
| 旗舰款 | M3 Ultra | 96 GB | 60 核 GPU | CA$5,999+ |

**核心优势**
- 统一内存：可以把 96 GB、128 GB 全部给模型用，跑大模型不 OOM
- 功耗极低（整机满载 ~100W），静音，随时开关
- macOS 开发体验流畅，适合兼顾编程与其他工作
- PyTorch 已支持 MPS（Metal Performance Shaders）后端

**主要短板**
- 不是 CUDA，部分库需要额外适配（`device="mps"` 而非 `"cuda"`）
- 训练速度：同等价位下比 RTX 4090 慢约 2–4 倍（取决于任务）
- 内存虽大，但带宽仍低于高端 NVIDIA 卡
- 遇到报错，社区资料比 CUDA 少

---

### 横向对比

| 维度 | RTX 4090 | RTX 5090 | Mac Studio M4 Max (36GB) |
|------|----------|----------|--------------------------|
| 参考总成本 | CA$1,899–$2,299（卡）+ 主机 | CA$2,799–$4,500+（卡）+ 主机 | CA$2,499（一体） |
| 训练速度 | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| 可用内存上限 | 24 GB | 32 GB | 36 GB 统一内存 |
| 生态兼容性 | ★★★★★（CUDA） | ★★★★★（CUDA） | ★★★☆☆（MPS） |
| 功耗 / 噪音 | 高（~450W） | 极高（~575W） | 极低（~100W） |
| 推理部署 | ★★★★★ | ★★★★★ | ★★★★☆ |
| 便携 / 办公 | ✗ | ✗ | ✓ |

---

### 怎么选？

- **以训练为主、追求速度** → NVIDIA RTX 4090（或云 GPU 按需租用）
- **内存吃紧（跑大模型/大图）、注重体验** → Mac Studio M4 Max 36GB 或 M3 Ultra 96GB
- **两全其美** → Mac Studio 做日常开发 + 云 GPU（AutoDL / Vast.ai）做大规模训练

> 没有本地 GPU？可先用 [Google Colab](https://colab.research.google.com) 或 [AutoDL](https://www.autodl.com) 租用云 GPU 起步。

---

## CPU 选型

CPU 在深度学习中的角色和 GPU 不同——它不做模型训练的矩阵运算，但负责**数据预处理、DataLoader 多进程加载、推理前后处理**。CPU 瓶颈会让 GPU 等待，拖慢整体训练效率。

---

### NVIDIA 主机方案：Intel vs AMD

搭配 NVIDIA 显卡自建主机时，CPU 主要看**核心数**（多进程数据加载）和**PCIe 通道数**（GPU 带宽）。

| 型号 | 核心/线程 | 基础/加速频率 | PCIe 通道 | 参考价（CAD） |
|------|----------|------------|----------|-------------|
| Intel Core i9-14900K | 24C / 32T | 3.2 / 6.0 GHz | PCIe 5.0 x16 | CA$499–$599 |
| AMD Ryzen 9 7950X | 16C / 32T | 4.5 / 5.7 GHz | PCIe 5.0 x16 | CA$549–$649 |
| AMD Ryzen 9 9950X | 16C / 32T | 4.3 / 5.7 GHz | PCIe 5.0 x16 | CA$699–$799 |

**深度学习场景下的建议：**
- 核心数 ≥ 12 核即可满足多进程 DataLoader（`num_workers=8`）
- AMD 平台在多核性能和功耗比上略占优
- Intel i9-14900K 性能接近但功耗更高（最高 ~250W）
- **不需要买最顶级的 CPU**，GPU 才是训练瓶颈

---

### Apple Mac Studio 方案：CPU 已内置

Mac Studio 的 CPU 与 GPU 集成在同一颗芯片上，无需单独选购。

| 芯片 | CPU 核心 | 单核性能 | 多核性能 |
|------|---------|---------|---------|
| M4 Max | 14 核（10 性能 + 4 能效） | ★★★★★ | ★★★★☆ |
| M3 Ultra | 28 核（20 性能 + 8 能效） | ★★★★☆ | ★★★★★ |

Apple Silicon 的单核性能目前是消费级处理器里最强的，日常编码、数据处理体验极快。M3 Ultra 的多核性能可以媲美高端桌面 CPU，同时整机功耗仍在 ~100W。

---

### CPU 横向对比

| 维度 | i9-14900K | Ryzen 9 9950X | M4 Max（内置） |
|------|-----------|--------------|--------------|
| 参考价（CAD） | CA$499–$599 | CA$699–$799 | 含在 Mac Studio 内 |
| 核心数 | 24C / 32T | 16C / 32T | 14C |
| 单核性能 | ★★★★☆ | ★★★★☆ | ★★★★★ |
| 多核性能 | ★★★★★ | ★★★★☆ | ★★★★☆ |
| 功耗 | 高（~125–250W） | 中（~170W） | 极低（整机 ~100W） |
| DataLoader 效率 | ★★★★★ | ★★★★★ | ★★★★☆ |
| 平台 | Windows / Linux | Windows / Linux | macOS 专属 |

---

### 怎么选？

- **自建 NVIDIA 主机**：Ryzen 9 7950X / 9950X 是性价比首选；预算有限选 i9-14900K
- **Mac Studio 用户**：CPU 已经够用，无需纠结，专注选内存容量即可

---

## 主板选型

主板负责把 CPU、GPU、内存、存储连接在一起。对深度学习来说，主板选型主要看三点：**CPU 插槽兼容性、PCIe 5.0 x16 插槽数量、供电规格**。

> Mac Studio 无需主板，跳过此节。

---

### 芯片组与插槽对应关系

| CPU | 插槽 | 推荐芯片组 |
|-----|------|----------|
| Intel i9-14900K | LGA1700 | Z790 |
| AMD Ryzen 9 7950X | AM5 | X670E |
| AMD Ryzen 9 9950X | AM5 | X670E / X870E |

> AMD AM5 平台向前兼容：X670E 主板可以跑 Ryzen 9000 系列，但建议搭配 X870E 以获得完整 PCIe 5.0 支持。

---

### Intel Z790 主板推荐

| 型号 | 特点 | 参考价（CAD） |
|------|------|-------------|
| MSI MAG Z790 Tomahawk WiFi | 扎实供电，性价比高，适合 i9-14900K | CA$299–$349 |
| ASUS ProArt Z790-Creator WiFi | 创作者定位，供电强，接口丰富 | CA$449–$499 |
| ASUS ROG Maximus Z790 Hero | 旗舰供电，超频潜力大，适合长期使用 | CA$699–$799 |

---

### AMD X670E / X870E 主板推荐

| 型号 | 芯片组 | 特点 | 参考价（CAD） |
|------|--------|------|-------------|
| MSI MAG X670E Tomahawk WiFi | X670E | 供电稳，兼容性好，入门首选 | CA$299–$349 |
| ASUS ROG Strix X670E-F Gaming | X670E | 全面 PCIe 5.0，M.2 插槽多 | CA$449–$499 |
| ASUS ROG Crosshair X870E Hero | X870E | 旗舰供电，适合 Ryzen 9950X | CA$599–$699 |

---

### 深度学习场景下的选板要点

| 要点 | 说明 |
|------|------|
| PCIe 5.0 x16 插槽 | 确保有至少一条，给 RTX 4090 / 5090 满速运行 |
| 供电相数 | ≥ 16+2 相，i9-14900K / Ryzen 9950X 满载功耗高，供电不足会降频 |
| DDR5 内存插槽 | 4 条槽，最大支持容量 ≥ 128 GB |
| M.2 插槽数量 | ≥ 2 条，训练数据集读写速度影响 DataLoader 效率 |
| WiFi / 2.5G 网口 | 下载数据集、远程连接服务器时用得上 |

---

### 主板横向对比

| 维度 | MSI MAG Tomahawk（入门） | ASUS ROG Hero（旗舰） | Mac Studio |
|------|------------------------|---------------------|-----------|
| 参考价（CAD） | CA$299–$349 | CA$699–$799 | 含在整机内 |
| PCIe 5.0 x16 | ✓ | ✓ | 不适用 |
| 供电规格 | 16+2 相 | 20+2 相 | 不适用 |
| DDR5 最大容量 | 128 GB | 192 GB | 不适用 |
| M.2 插槽数 | 4 | 6 | 不适用 |
| 适合场景 | 预算有限，单 GPU 训练 | 长期主力机，扩展需求高 | 一体机无需选配 |

---

### 怎么选？

- **预算优先**：MSI MAG Tomahawk 系列（Intel Z790 或 AMD X670E）性价比最高，供电够用，稳定可靠
- **长期投资**：ASUS ROG Hero / Crosshair 系列，供电更强，PCIe / M.2 扩展槽更多，未来升级空间大
- **不要在主板上过度投入**：主板不影响训练速度，把预算留给 GPU 和内存

---

## 内存选型

系统内存（RAM）在深度学习中的角色：**不参与模型训练**（那是 GPU 显存的工作），但负责在训练过程中临时存放原始数据集、数据增强 pipeline 的中间结果，以及多进程 DataLoader 的共享缓冲区。RAM 不够会导致频繁读磁盘，成为训练瓶颈。

---

### NVIDIA 主机方案：DDR5

现代 Z790 / X670E / X870E 平台均使用 **DDR5**。深度学习场景下的容量经验法则：

> **系统 RAM ≥ GPU 显存的 2–4 倍**
> - RTX 4090（24 GB 显存）→ 建议至少 64 GB RAM
> - RTX 5090（32 GB 显存）→ 建议至少 64–128 GB RAM

#### 容量推荐

| 容量 | 适合场景 |
|------|---------|
| 32 GB（2×16 GB） | 入门可用，数据集较小时够用 |
| 64 GB（2×32 GB） | 主流推荐，日常训练无压力 |
| 128 GB（4×32 GB） | 大数据集、多任务并行处理 |

#### 频率选择

DDR5 频率越高，CPU 与内存之间的数据传输越快，但超过一定阈值收益递减。

| 平台 | 推荐频率 | 原因 |
|------|---------|------|
| AMD AM5（Ryzen 7000/9000） | DDR5-6000 | AM5 的内存控制器甜点，延迟和带宽最优 |
| Intel LGA1700（i9-14900K） | DDR5-5600–6400 | Z790 平台支持范围广，6000 性价比最高 |

#### 品牌推荐

| 型号 | 规格 | 参考价（CAD） |
|------|------|-------------|
| G.Skill Trident Z5 RGB | 64 GB DDR5-6000 CL30 | CA$179–$219 |
| Corsair Vengeance DDR5 | 64 GB DDR5-6000 CL30 | CA$169–$199 |
| Kingston Fury Beast | 64 GB DDR5-6000 CL30 | CA$159–$189 |

> CL（CAS Latency）越低越好，CL30 是目前 DDR5-6000 的主流水准。

---

### Apple Mac Studio 方案：统一内存

Mac Studio 的内存在购买时就已确定，无法事后升级，**选机时一定要选够**。

| 内存容量 | 适合场景 |
|---------|---------|
| 36 GB（M4 Max 基础款） | 日常开发、中小型 YOLO 模型训练 |
| 96 GB（M3 Ultra 基础款） | 大模型、大图像分辨率目标检测 |

统一内存的特殊性：这块内存同时被 CPU、GPU、Neural Engine 共享，**可以把全部 36 GB / 96 GB 都给模型用**，不存在传统 PC 中"显存用完但系统 RAM 剩很多"的割裂问题。

---

### 内存横向对比

| 维度 | NVIDIA 主机（64 GB DDR5） | Mac Studio M4 Max（36 GB） | Mac Studio M3 Ultra（96 GB） |
|------|--------------------------|--------------------------|---------------------------|
| 参考价（CAD） | CA$159–$219 | 含在整机内 | 含在整机内 |
| 可用于模型的内存 | 受限于 GPU 显存（24–32 GB） | 36 GB 全部可用 | 96 GB 全部可用 |
| 带宽 | DDR5 ~96 GB/s | ~546 GB/s | ~800 GB/s |
| 事后升级 | ✓（插槽可加） | ✗（不可升级） |✗（不可升级） |
| 上限 | 128–192 GB | 36 GB（M4 Max） | 96 GB（M3 Ultra） |

---

### 怎么选？

- **自建 NVIDIA 主机**：64 GB DDR5-6000 是最佳起点，品牌差异不大，选 Kingston / Corsair 即可
- **Mac Studio**：内存不够将来无法补救——如果预算允许，M4 Max 直接选 96 GB 升级选项（如有），或考虑 M3 Ultra

---

## 存储选型

存储速度直接影响 DataLoader 的效率——训练时每个 epoch 都要从磁盘把图片读进内存，如果磁盘慢，GPU 会空转等待数据。容量则决定你能在本地放多大的数据集。

---

### NVIDIA 主机方案：NVMe SSD

深度学习主机推荐 **M.2 NVMe SSD**（不要用机械硬盘做训练数据盘）。PCIe 4.0 是目前性价比最高的选择，PCIe 5.0 速度更快但价格贵一倍且发热高，对大多数 YOLO 任务提升有限。

#### 推荐配置：系统盘 + 数据盘分开

| 用途 | 容量建议 | 原因 |
|------|---------|------|
| 系统盘（装 OS + 环境） | 1 TB | 系统、CUDA、conda 环境、代码 |
| 数据盘（存数据集） | 2–4 TB | COCO ~20 GB，自定义数据集可达数百 GB |

#### 产品推荐

| 型号 | 接口 | 顺序读速 | 容量 | 参考价（CAD） |
|------|------|---------|------|-------------|
| Samsung 990 Pro | PCIe 4.0 | 7,450 MB/s | 2 TB | CA$149–$179 |
| WD Black SN850X | PCIe 4.0 | 7,300 MB/s | 2 TB | CA$139–$169 |
| Crucial T705 | PCIe 5.0 | 14,500 MB/s | 2 TB | CA$249–$299 |
| Samsung 9100 Pro | PCIe 5.0 | 15,000 MB/s | 2 TB | CA$269–$319 |

> 对 YOLO 训练来说，PCIe 4.0（~7 GB/s）已经足够，PCIe 5.0 的速度优势在数据加载上体现不明显，不建议为此额外花钱。

---

### Apple Mac Studio 方案：内置 SSD + 外置扩展

Mac Studio 的内置 SSD **焊死在主板上，不可更换**，购买时需选好容量。内置 SSD 速度极快（~7.5 GB/s），但选项少、升级价格贵。

#### 内置 SSD 选项（M4 Max 为例）

| 容量 | 参考价（CAD） | 建议 |
|------|-------------|------|
| 512 GB | 含在基础款 CA$2,499 内 | 不够用，至少升级到 1 TB |
| 1 TB | +CA$230 | 够放系统和常用数据集 |
| 2 TB | +CA$460 | 推荐，留足余量 |
| 4 TB | +CA$920 | 数据集极大时选 |

#### 外置扩展：Thunderbolt SSD

Mac Studio 有 Thunderbolt 4 接口，可接外置高速 SSD 存放大数据集，读写速度可达 2–3 GB/s，完全满足训练需求。

| 型号 | 接口 | 顺序读速 | 容量 | 参考价（CAD） |
|------|------|---------|------|-------------|
| Samsung T9 | USB 3.2 Gen 2×2 | 2,000 MB/s | 2 TB | CA$149–$179 |
| SanDisk Desk Drive | USB 3.2 | 1,000 MB/s | 4 TB | CA$139–$159 |
| OWC Envoy Pro FX | Thunderbolt 3 | 2,800 MB/s | 2 TB | CA$299–$349 |

---

### 存储横向对比

| 维度 | NVIDIA 主机 | Mac Studio |
|------|------------|-----------|
| 内置 SSD 速度 | ~7 GB/s（PCIe 4.0） | ~7.5 GB/s（内置） |
| 可扩展性 | ✓ 多条 M.2 插槽，随时加盘 | ✗ 内置不可换，靠外置扩展 |
| 大容量成本 | 低（4 TB NVMe ~CA$300） | 高（官方 4 TB 升级 +CA$920） |
| 外置方案 | USB / Thunderbolt 均可 | Thunderbolt 4（速度更快） |

---

### 怎么选？

- **NVIDIA 主机**：系统盘 1 TB + 数据盘 2 TB，都选 PCIe 4.0，Samsung 990 Pro 或 WD SN850X 可靠性好
- **Mac Studio**：内置至少选 1 TB，数据集用 Samsung T9 外置扩展，性价比最高
- **通用建议**：数据集单独放一块盘，避免和系统盘抢 I/O

---

## 机箱与散热

> Mac Studio 无需机箱和额外散热，跳过此节。

深度学习训练动辄跑几小时满负荷，CPU + GPU 合计功耗轻松超过 800W，**散热和机箱风道是长期稳定运行的关键**，比日常游戏 PC 要求严苛得多。

---

### 机箱选型

RTX 4090 / 5090 的卡长普遍在 320–380 mm，必须选 **ATX 全塔或中塔**，同时优先考虑风道设计而非外观。

| 型号 | 类型 | 特点 | 参考价（CAD） |
|------|------|------|-------------|
| Fractal Design Torrent | 中塔 ATX | 底部大风扇直吹 GPU，风道业界顶级 | CA$189–$229 |
| Lian Li O11 Dynamic EVO | 中塔 ATX | 三面进风，搭配水冷效果极佳 | CA$189–$219 |
| be quiet! Silent Base 802 | 中塔 ATX | 隔音出色，风道合理，安静优先 | CA$179–$209 |
| Fractal Design North | 中塔 ATX | 木纹面板，桌面美观，风道良好 | CA$169–$199 |

**选机箱的核心原则：**
- GPU 限长 ≥ 380 mm（RTX 5090 部分公版卡更长）
- 前后至少各 2 个 120/140 mm 风扇位
- 优先选底部或前部大面积进风的设计，让 GPU 直接吸到冷风

---

### CPU 散热：风冷 vs 水冷

#### 风冷

优点：结构简单、可靠性高、无漏液风险、长期免维护。

| 型号 | 规格 | 参考价（CAD） |
|------|------|-------------|
| Noctua NH-D15 | 双塔双风扇 | CA$109–$129 |
| be quiet! Dark Rock Pro 5 | 双塔双风扇 | CA$99–$119 |

Noctua NH-D15 是公认的顶级风冷，压制 i9-14900K / Ryzen 9950X 满载完全没有问题，安静且免维护，**对大多数人来说是最佳选择**。

#### AIO 一体式水冷（All-in-One）

优点：温度更低、机箱内视觉整洁；缺点：有水泵寿命（一般 5–7 年），需要额外安装空间。

| 型号 | 冷排尺寸 | 参考价（CAD） |
|------|---------|-------------|
| Corsair iCUE H150i Elite | 360 mm | CA$179–$219 |
| NZXT Kraken 360 | 360 mm | CA$179–$209 |
| Arctic Liquid Freezer III 360 | 360 mm | CA$99–$129 |

> 搭配 i9-14900K 或 Ryzen 9950X 做长时间训练，推荐 **360 mm 冷排**，240 mm 在持续满载下压制能力有限。

#### 要不要上自定义水冷？

**不需要。** 自定义水冷（DIY 水冷）成本高（CA$500+）、安装复杂、维护麻烦，对训练速度没有任何提升。顶级风冷或 AIO 完全够用。

---

### GPU 散热

GPU 使用自带散热器，无需额外购买。但有两点需要注意：

- **机箱风道**要给 GPU 提供足够的冷风供给（这是选 Fractal Torrent 这类机箱的原因）
- 长时间训练建议在系统中监控 GPU 温度，保持在 **83°C 以下**为佳

```bash
# 实时监控 GPU 温度
watch -n 1 nvidia-smi
```

---

### 散热方案横向对比

| 方案 | 压制能力 | 噪音 | 可靠性 | 价格（CAD） | 推荐度 |
|------|---------|------|--------|-----------|--------|
| Noctua NH-D15（风冷） | ★★★★☆ | 极低 | ★★★★★ | CA$109–$129 | ✅ 首选 |
| AIO 360mm 水冷 | ★★★★★ | 低 | ★★★★☆ | CA$99–$219 | ✅ 追求低温 |
| AIO 240mm 水冷 | ★★★☆☆ | 低 | ★★★★☆ | CA$79–$149 | ⚠️ 持续满载勉强 |
| 自定义水冷 | ★★★★★ | 极低 | ★★★☆☆ | CA$500+ | ❌ 不必要 |

---

### 怎么选？

- **追求省心**：Fractal Design Torrent 机箱 + Noctua NH-D15 风冷，稳定可靠，长期免维护
- **追求低温安静**：Lian Li O11 Dynamic EVO 机箱 + Arctic Liquid Freezer III 360，性价比最高的水冷方案
- **不需要自定义水冷**：对训练速度没有帮助，维护成本高

## 软件选择

在搭建深度学习环境之前，先理解各平台的软件栈层次——这是避免版本冲突、快速排查问题的基础。

---

### Nvidia 方案（Windows / Linux）

#### 软件栈层次

![Nvidia 驱动与 CUDA 的关系](/images/nvidia-cuda-layers.png)

整个软件栈从下到上分为四层：

| 层级 | 名称 | 作用 |
|------|------|------|
| **硬件** | GPU | 物理计算单元 |
| **Driver** | Nvidia 驱动 | 让操作系统识别并控制 GPU |
| **CUDA** | Compute Unified Device Architecture | GPU 并行计算平台，提供编程接口 |
| **框架** | PyTorch / TensorFlow 等 | 你实际写代码的层，底层调用 CUDA |

图中各层的**宽度**有意义：CUDA 比 PyTorch 宽，代表 CUDA 同时支撑多个框架；Driver 和 OS 最宽，是整个系统的地基。

#### 版本对应关系（关键）

三层版本必须**严格匹配**，否则运行时报错：

```
Driver 版本 ≥ CUDA 所需最低驱动版本
CUDA 版本  ↔  cuDNN 版本
cuDNN 版本 ↔  PyTorch / TensorFlow 版本
```

例如 PyTorch 2.1 需要 CUDA 11.8 或 12.1，对应特定 cuDNN，Driver 需满足该 CUDA 版本的最低要求。

#### 安装方式推荐

| 方式 | 推荐度 | 说明 |
|------|--------|------|
| **Docker 容器** | ⭐⭐⭐ | Nvidia 官方镜像版本已对齐，最省心 |
| **Conda + pip** | ⭐⭐ | `conda install pytorch -c pytorch -c nvidia` 自动拉对应 CUDA |
| **手动安装** | ⭐ | 自行匹配版本，最容易出冲突 |

---

### Mac 方案（Apple Silicon）

#### 软件栈层次

```
PyTorch（device="mps"）
        ↓
MPS（Metal Performance Shaders）  ← 相当于 CUDA
        ↓
Metal                              ← Apple 的 GPU 编程框架
        ↓
macOS（驱动已内置，无需单独安装）
        ↓
Apple Silicon 硬件
```

**与 Nvidia 方案最大的区别**：Driver + CUDA + cuDNN 这三层全部省掉，Metal/MPS 内置在 macOS 里，系统更新自动升级，无需手动管理版本。

#### 安装（只需两步）

```bash
# 1. 创建 conda 环境
conda create -n yolo python=3.10 -y
conda activate yolo

# 2. 安装 PyTorch（自动支持 MPS，无需指定 CUDA 版本）
pip install torch torchvision torchaudio
```

#### 验证 GPU 可用

```python
import torch
print(torch.backends.mps.is_available())  # True
print(torch.backends.mps.is_built())      # True
```

#### 使用时指定设备

```python
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = model.to(device)
```

---

### 两种方案对比

| 维度 | Nvidia（CUDA） | Mac（MPS） |
|------|--------------|-----------|
| GPU 编程框架 | CUDA + cuDNN | Metal + MPS |
| 驱动安装 | 需手动安装 | 内置于 macOS |
| 版本管理复杂度 | 高（三层需匹配） | 低（随系统自动更新） |
| PyTorch 设备参数 | `device="cuda"` | `device="mps"` |
| 生态兼容性 | ★★★★★ | ★★★☆☆ |
| 安装难度 | ★★★☆☆ | ★☆☆☆☆ |

---

## 软件环境

### 1. 安装 NVIDIA 驱动

前往 [NVIDIA 官网](https://www.nvidia.com/drivers) 下载对应显卡驱动并安装。

验证安装：

```bash
nvidia-smi
```

### 2. 安装 Miniconda

推荐用 Conda 管理 Python 环境，避免依赖冲突。

```bash
# Linux / macOS
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### 3. 创建独立 Python 环境

```bash
conda create -n yolo python=3.10 -y
conda activate yolo
```

### 4. 安装 PyTorch（含 CUDA）

前往 [pytorch.org](https://pytorch.org/get-started/locally/) 选择对应 CUDA 版本，例如 CUDA 12.1：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

验证 GPU 可用：

```python
import torch
print(torch.cuda.is_available())   # True
print(torch.cuda.get_device_name(0))
```

### 5. 安装 Ultralytics（YOLOv8/v11）

```bash
pip install ultralytics
```

验证安装：

```bash
yolo checks
```

---

## 用 Docker + VS Code 做本地开发

相比直接在宿主机上安装 CUDA / conda 环境，**Docker 容器**能让你把整个开发环境打包成一个镜像，彻底告别"在我机器上能跑"的问题——团队协作、换机迁移、多项目隔离都变得轻松。结合 **VS Code Dev Containers**，你可以在容器内获得和本地开发几乎一模一样的体验：代码补全、调试器、终端全部正常工作。

---

### 为什么选 Docker

| 问题 | 不用 Docker | 用 Docker |
|------|------------|----------|
| 多项目 CUDA 版本冲突 | 手动切 conda 环境，容易出错 | 每个项目一个镜像，互不干扰 |
| 换机迁移 | 重新装驱动 + 环境，耗时数小时 | `docker pull` + `docker run`，几分钟搞定 |
| 团队协作 | "你那边能跑但我这里报错" | 镜像一致，环境完全相同 |
| 生产部署 | 本地和服务器环境不一致 | 开发镜像即部署镜像 |

---

### 前置条件

#### NVIDIA 主机（Windows / Linux）

```bash
# 1. 安装 Docker Engine（Linux）
curl -fsSL https://get.docker.com | sh

# 2. 安装 NVIDIA Container Toolkit（让容器内能访问 GPU）
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

# 3. 重启 Docker 使 GPU 支持生效
sudo systemctl restart docker

# 验证 GPU 在容器内可访问
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

Windows 用户推荐使用 **Docker Desktop**（内置 WSL2），安装 NVIDIA Container Toolkit 的 WSL2 版本后同样支持 GPU 直通。

#### Mac（Apple Silicon）

Mac 上的 Docker Desktop 目前**不支持 MPS 直通**（Metal 不能透传到容器），容器内只能跑 CPU。

如果你的主力工作是本地训练，Mac 用户建议：
- **日常代码开发**：用 Docker 容器（CPU），验证代码逻辑
- **实际训练**：直接在宿主机 conda 环境（`device="mps"`）跑

---

### 选择基础镜像

NVIDIA 官方提供的 NGC 镜像已经预装好 CUDA + cuDNN + PyTorch，是最省心的选择：

| 镜像 | 适合场景 | 示例 tag |
|------|---------|---------|
| `pytorch/pytorch` | 直接用 PyTorch，轻量 | `pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime` |
| `nvcr.io/nvidia/pytorch` | NGC 官方，预装更多工具 | `nvcr.io/nvidia/pytorch:24.05-py3` |
| `ultralytics/ultralytics` | 直接用 YOLO，开箱即用 | `ultralytics/ultralytics:latest` |

> 建议从 `ultralytics/ultralytics` 开始，它已经包含了 CUDA、PyTorch、Ultralytics，不用写 Dockerfile。

---

### 项目文件结构

```
project/
├── .devcontainer/
│   └── devcontainer.json   # VS Code Dev Container 配置
├── docker-compose.yml       # 容器启动配置
├── data/
├── weights/
└── train.py
```

---

### docker-compose.yml

```yaml
services:
  yolo-dev:
    image: ultralytics/ultralytics:latest
    container_name: yolo-dev
    runtime: nvidia          # 启用 GPU（Mac 上去掉这行）
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - .:/workspace         # 把项目目录挂载进容器
      - ~/.ssh:/root/.ssh:ro # 可选：挂载 SSH key，方便 git 操作
    working_dir: /workspace
    stdin_open: true
    tty: true
    ports:
      - "8888:8888"          # Jupyter Lab
      - "6006:6006"          # TensorBoard
    shm_size: "8gb"          # 增大共享内存，DataLoader 多进程必需
```

启动容器：

```bash
docker compose up -d
```

---

### VS Code Dev Container 配置

在项目根目录创建 `.devcontainer/devcontainer.json`：

```json
{
  "name": "YOLO Dev",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "yolo-dev",
  "workspaceFolder": "/workspace",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.pylance",
        "ms-toolsai.jupyter",
        "njpwerner.autodocstring",
        "eamodio.gitlens"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/bin/python3",
        "editor.formatOnSave": true
      }
    }
  },
  "remoteUser": "root",
  "postCreateCommand": "pip install -e . 2>/dev/null || true"
}
```

---

### 用 VS Code 打开容器

1. 安装 VS Code 插件：**Dev Containers**（`ms-vscode-remote.remote-containers`）
2. 在项目目录下，按 `Cmd+Shift+P`（Mac）或 `Ctrl+Shift+P`（Windows/Linux）
3. 选择 **"Dev Containers: Open Folder in Container"**
4. VS Code 会自动拉取镜像、启动容器，并把整个编辑器接入容器内部

此后，VS Code 左下角会显示 `Dev Container: YOLO Dev`，终端直接就是容器内的 shell。

---

### 验证 GPU 可用

打开 VS Code 内置终端，运行：

```bash
# 方式一：nvidia-smi
nvidia-smi

# 方式二：Python 验证
python - <<'EOF'
import torch
print("CUDA available:", torch.cuda.is_available())
print("Device:", torch.cuda.get_device_name(0))
print("YOLO version:", __import__('ultralytics').__version__)
EOF
```

---

### 常用操作速查

```bash
# 启动容器（后台运行）
docker compose up -d

# 进入已运行的容器（不用 VS Code 时）
docker exec -it yolo-dev bash

# 查看容器日志
docker compose logs -f

# 停止容器
docker compose down

# 重新构建镜像（更新了 Dockerfile 后）
docker compose build --no-cache
```

---

### 自定义 Dockerfile（可选）

如果需要安装额外依赖或固定版本，可以自己写 Dockerfile：

```dockerfile
FROM ultralytics/ultralytics:latest

# 安装项目额外依赖
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
```

对应修改 `docker-compose.yml`，把 `image:` 改为 `build:`：

```yaml
services:
  yolo-dev:
    build:
      context: .
      dockerfile: Dockerfile
    # ... 其余配置不变
```

---

### 小结

| 步骤 | 操作 |
|------|------|
| 1 | 安装 Docker + NVIDIA Container Toolkit |
| 2 | 创建 `docker-compose.yml`，选好基础镜像 |
| 3 | 创建 `.devcontainer/devcontainer.json` |
| 4 | VS Code 安装 Dev Containers 插件，打开容器 |
| 5 | 验证 `nvidia-smi` 和 `torch.cuda.is_available()` |

> Mac 用户如果只是想隔离依赖环境（不需要 GPU 直通），Docker + Dev Containers 同样适用，只需去掉 `runtime: nvidia` 相关配置，在宿主机训练、容器内开发。

---

## 推荐工具

| 工具 | 用途 |
|------|------|
| VS Code + Python 插件 | 代码编写 |
| Jupyter Lab | 实验与可视化 |
| TensorBoard / W&B | 训练过程监控 |
| LabelImg / Label Studio | 数据标注 |

---

## 目录结构建议

```
project/
├── data/
│   ├── images/
│   └── labels/
├── runs/          # 训练输出（自动生成）
├── weights/       # 预训练权重
└── train.py
```

---

持续更新中...

---

## 词条解释

### TFLOPS

**TFLOPS**（Tera Floating Point Operations Per Second）= 每秒万亿次浮点运算。

深度学习的本质是大量矩阵乘法，每一次乘加运算都是一次浮点运算。TFLOPS 就是衡量 GPU 每秒能完成多少次这样的运算——数字越大，训练速度越快。

| GPU | FP32 TFLOPS |
|-----|------------|
| RTX 4090 | ~82 |
| RTX 5090 | ~209 |
| Mac Studio M4 Max (40 核 GPU) | ~21 |

> 实际训练速度还受显存带宽、软件优化等影响，TFLOPS 只是理论峰值参考。

### PCIe

**PCIe**（Peripheral Component Interconnect Express）是主板上连接 GPU、SSD 等高速设备的**数据通道标准**，可以理解为 CPU 和 GPU 之间的"高速公路"——训练时数据从内存传给 GPU、梯度再传回来，都走这条路。

- **x16 / x8 / x4**：后面的数字是"车道数"，越大带宽越高
- **PCIe 5.0 x16**：目前主流旗舰标准，带宽约 128 GB/s，足够撑住 RTX 4090 / 5090

对深度学习来说 PCIe 本身不是瓶颈（GPU 显存带宽才是），但要确认主板和 CPU 支持对应版本，否则会降速运行。
