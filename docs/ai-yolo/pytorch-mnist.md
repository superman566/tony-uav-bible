# PyTorch 手写数字识别实战

> 这篇笔记按"由浅入深"排列：Part 1、Part 2 是背景知识（PyTorch 是什么、MNIST 数据集是什么），不涉及代码，读起来很快；Part 3 才是真正的实战——逐行讲解一份真实跑通的训练代码（对应 `docs/ai-yolo/reg_pt.ipynb`），从加载数据一路讲到训练出模型、把它存下来。已经熟悉 PyTorch/MNIST 的话，可以直接用右侧「本页目录」跳到 Part 3。

## Part 1：认识 PyTorch（背景知识）

### PyTorch 是什么

**一句话理解**：PyTorch 是一个开源的深度学习框架，帮你把"定义神经网络、算梯度、更新权重"这些数学操作，变成几行 Python 代码就能调用的现成工具，不用自己手写矩阵求导。[深度学习基础](/ai-yolo/dl-basics) 里手算的那些"梯度下降更新 w、b"的过程，PyTorch 一行 `loss.backward()` 就自动算完了。

### 官网

https://pytorch.org/

### 历史

- **2002 年，Torch**：最早的 Torch 是用 Lua 语言写的科学计算框架，主要在学术圈小范围使用。
- **2016 年 10 月，PyTorch 发布**：Facebook（现 Meta）的 AI Research 团队（FAIR）用 Python 重写，核心卖点是"动态计算图"（define-by-run）——网络结构在运行时才确定，写起来和调试都比早期"先搭图纸再运行"的框架（比如当时的 TensorFlow 1.x）更符合直觉、更容易 debug。
- **2018 年，1.0 版本**：合并了 Facebook 内部用于生产部署的 Caffe2，从"研究友好"补齐了"能上生产"的能力。
- **2022 年，交给 PyTorch Foundation**：治理权移交给 Linux Foundation 旗下新成立的 PyTorch Foundation，不再是 Meta 一家公司的项目，微软、AMD、Google、AWS 等也作为成员参与共建。
- 目前是学术界和大模型训练领域的事实标准框架（Hugging Face、Stable Diffusion、LLaMA 等主流模型的训练代码基本都基于它）。

### 市场占比

- **学术界**：占绝对主导。近几年顶会论文里用 PyTorch 实现的比例常年在 70%~90% 区间，明显超过 TensorFlow。
- **工业界**：早期 TensorFlow 靠 TF Serving、TFLite 在生产部署上更有优势；这几年 PyTorch 通过 TorchServe、ONNX 导出、`torch.compile` 等逐步补齐，加上几乎所有主流大模型都用它训练，目前综合来看 PyTorch 已经是行业首选，TensorFlow 份额持续下滑。

![PyTorch 与 TensorFlow 占比对比](/images/PytorchvsTensorflow.png)

> 以上是行业里公认的大致趋势，不是精确统计数字——如果要在正式材料里引用具体百分比，建议查最新的 Papers with Code / State of AI 报告等来源核实。

### 支持哪些平台

| 类别 | 支持情况 |
|-|-|
| 操作系统 | Linux、macOS、Windows |
| GPU 加速 | NVIDIA GPU（CUDA）、Apple Silicon（MPS 后端）、AMD GPU（ROCm） |
| 纯 CPU | 支持，只是训练速度慢很多 |
| 移动端/边缘设备 | PyTorch Mobile / ExecuTorch，支持 iOS、Android |
| 语言接口 | 主力是 Python；生产部署也提供 C++ 接口（LibTorch），不依赖 Python 运行时 |

具体到你自己机器上怎么装（conda 环境、CUDA 还是 MPS、Docker 方案怎么选），[搭建深度学习开发环境](/ai-yolo/dl-env-setup) 里已经写得很详细了，这里不重复。

### 一般怎么用

安装：

```bash
pip install torch torchvision
```

核心工作流程就 4 步，写代码时基本都是照着这个顺序来：

```
1. 数据 → Tensor（张量，见「图像识别的数学基础」）
2. 定义模型（继承 nn.Module，描述网络有哪些层）
3. 前向传播算 loss，loss.backward() 自动算出每个参数的梯度
4. optimizer.step() 用梯度更新一次权重，重复很多轮
```

#### PyTorch 生态里的几个主要库

**一句话理解**：`pip install torch torchvision` 这一行，装的其实是一个核心库 + 一个"领域专用工具箱"——核心库不关心你处理的是图片、声音还是文本，工具箱负责各自领域的数据集、预处理和现成模型。

| 库 | 定位 | 提供什么 |
|-|-|-|
| **torch** | 核心库（Core Library） | 最基础的能力：Tensor（张量）运算、自动求导（Autograd）、`nn.Module` 搭网络结构、`optim` 优化器——不管数据是图片、声音还是文本，都要靠它 |
| **torchvision** | 计算机视觉扩展（Computer Vision） | 图像专用：现成数据集（MNIST、CIFAR、ImageNet…）、图像预处理（`transforms.ToTensor`、`Normalize`…）、经典预训练模型（ResNet 等） |

对应到本篇要做的事：`torch` 是必需的地基，`torchvision` 是主力（加载 MNIST、做图像预处理，后面 YOLO 系列也一直靠它）。

## Part 2：认识数据集——MNIST（背景知识）

**一句话理解**：MNIST（Modified National Institute of Standards and Technology database）是机器学习界最经典的"入门数据集"——7 万张已经标好正确答案的手写数字图片，规模小、格式统一，几乎是每个人学图像分类（Image Classification）时第一个跑通的数据集。

### 从哪来

- 最早的数据来自美国国家标准与技术研究院（NIST）收集的两批手写样本：一批是人口普查局员工写的数字（字迹工整），另一批是高中生写的数字（字迹更随意）。NIST 原始数据里这两批人分别被整批放进了训练集和测试集，导致两边"手写风格"不一致，直接拿来训练效果很差。
- 1998 年，Yann LeCun（卷积神经网络的奠基人之一）和合作者 Corinna Cortes、Christopher Burges 把这批数据重新整理：统一缩放、居中、灰度化，并把两批人的样本重新打散、混合分配进训练集和测试集——这个"重新处理过"（Modified）的过程，就是 MNIST 名字里 "M" 的来历。
- LeCun 用这批数据训练了他设计的卷积神经网络 LeNet-5，最早被实际用在银行支票、邮政编码的自动识别上——这也是 CNN（卷积神经网络）最早落地的应用场景之一。

### 具体规格

| 项目 | 数值 |
|-|-|
| 总样本数 | 70,000 张 |
| 训练集 | 60,000 张 |
| 测试集 | 10,000 张 |
| 图片尺寸 | 28×28 像素 |
| 通道数 | 1（灰度图，不是彩色） |
| 像素值范围 | 0～255（0 = 纯黑背景，255 = 纯白笔画） |
| 类别数 | 10（数字 0～9） |
| 单张图拉平成向量后的维度 | 28×28 = 784 |

### 长什么样：具体看一眼数据

一张图片本质就是一个数字矩阵，如果把一张写着"7"的图简化成个位数示意（0 是背景，数字越大代表笔画越亮）：

```
0 0 0 0 0 0 0 0
0 0 0 0 0 0 9 0
0 0 0 0 0 9 0 0
0 0 0 0 9 0 0 0
0 0 0 9 0 0 0 0
0 0 9 9 9 9 9 9
0 0 0 0 0 0 0 0
```

真实的 MNIST 图片是完整的 28×28、像素值 0～255 连续渐变的灰度图，这里只是把"一张图片其实就是一个数字矩阵"这件事具体画出来，方便直观感受。

### 为什么是入门首选

数据量小（几十 MB，几秒钟下载完）、格式统一（不用自己做复杂的数据清洗）、`torchvision.datasets.MNIST` 一行代码直接能用——非常适合用来验证"数据处理 → 模型 → 训练循环"这一整套流程写得对不对，而不用先在数据准备上耗费太多精力。

### 局限性与替代数据集

这几年 MNIST 被认为"太简单"了——随便一个简单的全连接网络就能跑到 97%+ 准确率，已经不太能区分不同模型/方法的真实差距，业内更多把它当"验证流程能不能跑通"的第一步，而不是拿来正式对比模型好坏的基准。因此社区做了几个和 MNIST **格式完全兼容、但更难**的替代数据集：

| 数据集 | 特点 |
|-|-|
| Fashion-MNIST | Zalando 出品，图片规格和 MNIST 完全一样（28×28 灰度、10 类），内容换成了 T恤、鞋子等 10 类服饰图片，比手写数字更难分辨 |
| EMNIST | NIST 原始数据的扩展版，除了数字还包含英文字母 |
| KMNIST | 日语平假名字符，格式同样兼容 MNIST |

这几个数据集都可以直接把代码里的 `datasets.MNIST` 换成对应的类名就能跑，不用改其他任何代码——这正是"格式统一"带来的好处。下面 Part 3 里真实跑的训练结果（准确率能到 98%+），也印证了前面说的"MNIST 对现在的模型来说已经不难"。

## Part 3：动手实现——逐行讲解训练代码（正式开始写代码）

这一部分对应 `docs/ai-yolo/reg_pt.ipynb` 里真实跑通、训练出 98%+ 准确率的代码，按"准备数据 → 搭模型 → 写训练/评估函数 → 开始训练 → 保存模型"的顺序讲，代码复杂度也是一路往上走的——数据加载最简单，模型定义开始涉及新概念，训练/评估函数最复杂。每一步都配着 Part 1、Part 2 的背景知识一起看。

### 第一步：导入要用的工具

```python
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor
```

- `torch`：核心库，张量运算、自动求导都靠它
- `nn`：`torch.nn`，搭神经网络用的模块（`nn.Linear`、`nn.ReLU` 这些都在这里面）
- `DataLoader`：把数据集自动切成一批批（batch）喂给模型的工具
- `datasets`：`torchvision.datasets`，装了常见数据集的加载接口，MNIST 就在里面
- `ToTensor`：把图片转成 PyTorch 能处理的张量格式的预处理工具

### 第二步：加载 MNIST 数据集

```python
training_data = datasets.MNIST(
    "data",
    train=True,
    download=True,
    transform=ToTensor()
)

test_data = datasets.MNIST(
    "data",
    train=False,
    download=True,
    transform=ToTensor()
)
# print(test_data)
```

`datasets.MNIST()` 的四个参数：`"data"` 是数据存放的文件夹（`root`）；`train=True/False` 决定拿训练集（6 万张）还是测试集（1 万张）；`download=True` 表示本地没有就自动下载；`transform=ToTensor()` 让每张图读出来时自动转成张量、像素值从 0~255 缩放到 0~1。

`# print(test_data)` 这一行被注释掉了——大概率是写代码时用来确认"数据加载对不对"的调试语句，确认没问题之后就注释掉，不影响后面运行，这是很常见的写代码习惯，不是 bug。

### 第三步：切成 batch，看一眼数据长什么样

```python
BATCH_SIZE = 128

train_dataloader = DataLoader(
    training_data,
    batch_size=BATCH_SIZE,
    shuffle=True
)

test_dataloader = DataLoader(
    test_data,
    batch_size=BATCH_SIZE
)

for x, y in train_dataloader:
    print(f"shape of x[N, C, W, H]:{x.shape}")
    print(f"share of y: {y.shape}, {y.dtype}")
    print(f"lable of y: {y[0].item()}")
    break
```

**这里的 `BATCH_SIZE=128`**：训练集 60000 张，128 张一批，60000÷128=468.75，也就是一个 epoch 会被切成 469 个 batch（468 个满 128 张，最后 1 个只有 96 张）。

**`shuffle=True` 只加在训练集上**：每个 epoch 开始前把训练数据顺序打乱，避免模型学到"数据排列顺序"这种和任务无关的规律；测试集不需要打乱，因为只是用来打分，顺序不影响结果。

**`for x, y in train_dataloader: ... break`**：这是常见的调试写法——只取第一个 batch，打印出形状确认没问题，就直接 `break` 跳出循环，不是真的要遍历所有数据。

真实跑出来的结果：

```
shape of x[N, C, W, H]:torch.Size([128, 1, 28, 28])
share of y: torch.Size([128]), torch.int64
lable of y: 2
```

`x.shape = [128, 1, 28, 28]`：`N=128` 是这一批的图片数量，`C=1` 是灰度图的通道数，`H=28`、`W=28` 是每张图的高和宽。`y.shape = [128]`：128 张图对应的 128 个标签，`torch.int64` 说明标签是整数类型（`nn.CrossEntropyLoss` 要求标签必须是整数）。`y[0].item()` 把第 1 个标签从张量转成普通 Python 数字，这一批第一张图的标签是 `2`。

### 第四步：搭建神经网络

```python
class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.nmodel = nn.Sequential(
            nn.Linear(28*28, 256),
            nn.BatchNorm1d(256), # 后加优化用
            nn.ReLU(),
            nn.Dropout(0.5), # 后加优化用
            nn.Linear(256, 128),
            nn.BatchNorm1d(128), # 后加优化用
            nn.ReLU(),
            nn.Dropout(0.2), # 后加优化用
            nn.Linear(128, 10)
        )
    def forward(self, x):
      x = nn.Flatten()(x)
      output = self.nmodel(x)
      return output

device = ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
print(f"GPU->{device}")

model = NeuralNetwork().to(device)
```

**网络结构**：还是全连接网络（MLP）的思路——`Linear(784, 256)` 把拉平后的图片压到 256 维，`Linear(256, 128)` 再压到 128 维，最后 `Linear(128, 10)` 压到 10 维（对应 0~9）。比最简单的版本多了两样东西，代码里用注释标了"后加优化用"，说明是先写出能跑的版本，再加上去提升效果的：

- **`nn.BatchNorm1d`（批归一化，Batch Normalization）**：对每一层的输出，在当前这个 batch 内部做一次"重新校准"（减均值、除标准差），让传到下一层的数值范围更稳定。效果类似 [数据归一化](/ai-yolo/nn-training-optimization) 那一节讲的"输入归一化"，只是这里不是只做在最开始的输入上，而是每经过一个 `Linear` 层就重新做一次，能让更深的网络训练得更快、更稳。
- **`nn.Dropout(0.5)` / `nn.Dropout(0.2)`（随机丢弃）**：训练时随机把这一层一部分神经元的输出临时"关掉"（设成 0）——`Dropout(0.5)` 是关掉 50%，`Dropout(0.2)` 是关掉 20%。这么做是为了防止过拟合（[过拟合](/ai-yolo/dl-basics) 那一节讲过的"死记硬背"），强迫网络不能依赖某几个神经元，得学得更"鲁棒"。前一层用 0.5 这么高的比例，后一层用更保守的 0.2，是因为网络越靠近输出层，通常越不希望丢太多信息。

`forward` 里 `x = nn.Flatten()(x)` 还是那句话：把 `(N,1,28,28)` 的图片拉平成 `(N,784)`，再交给 `self.nmodel` 一路算到底。

**选设备**：`device` 那一行做的是"有 NVIDIA GPU 就用 CUDA，没有但是 Mac 就用 MPS，都没有就退回 CPU"的三选一。这次实际输出是 `GPU->cuda`，说明这份代码是在一台带 NVIDIA GPU 的机器上跑的（很可能是 Google Colab，默认会分配一块 GPU）。`model.to(device)` 把模型的所有参数搬到这块 GPU 上，后面训练数据也要搬到同一个设备，两者才能一起计算。

### 第五步：定义损失函数、优化器，写训练和评估函数

```python
loss_fn = nn.CrossEntropyLoss()
learning_rate = 1e-3
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    model.train()
    for batch, (x, y) in enumerate(dataloader):
        x, y = x.to(device), y.to(device)
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(x)
            print(f"loss: {loss:>7f} [{current:>5d}/{size:5d}]")
```

- `loss_fn = nn.CrossEntropyLoss()`：交叉熵损失，多分类问题的标准选择，内部已经包含 Softmax，模型直接输出原始分数（logits）就行。
- `learning_rate = 1e-3`：学习率 0.001，[梯度下降](/ai-yolo/dl-basics) 里讲过的那个"步子迈多大"的系数。
- `optimizer = torch.optim.Adam(...)`：用 [Adam](/ai-yolo/nn-training-optimization) 优化器，把模型所有可训练参数（`model.parameters()`）和学习率一起传进去，它会自适应地调整每个参数的更新步子。

`train()` 函数把"训练一整轮（一个 epoch）"封装成一个可以反复调用的函数：

- `size = len(dataloader.dataset)`：训练集总图片数（60000），后面打印进度用。
- `model.train()`：切换到训练模式——因为这次模型里真的用上了 `BatchNorm1d` 和 `Dropout`，这一步不再只是"养成习惯"，而是有实际效果：训练模式下 `Dropout` 会真的随机丢弃神经元，`BatchNorm1d` 会用当前这个 batch 的统计量做归一化。
- `for batch, (x, y) in enumerate(dataloader)`：遍历每一个 batch，`enumerate` 顺便给出这是第几个 batch（从 0 开始）。
- `x, y = x.to(device), y.to(device)`：把这批数据搬到和模型同一个设备上。
- `pred = model(x)`：前向传播，得到形状 `(128, 10)` 的预测分数。
- `loss = loss_fn(pred, y)`：算这一批的损失值。
- `loss.backward()`：反向传播，自动算出每个参数的梯度。
- `optimizer.step()`：用算出来的梯度更新一次权重。
- `optimizer.zero_grad()`：清空这次的梯度，给下一个 batch 做准备——写在 `step()` 之后也没问题，只要保证下一次 `backward()` 之前梯度已经清零就行。
- `if batch % 100 == 0`：不是每个 batch 都打印（469 个 batch 全打印会刷屏），每 100 个 batch 打印一次当前 loss 和大致处理进度，`current = batch * len(x)` 约等于"目前处理过多少张图片"。

```python
def test(dataloader, model, loss_fn):
    num_batches = len(dataloader)
    size = len(dataloader.dataset)
    test_loss, correct = 0, 0
    model.eval()
    with torch.no_grad():
        for batch, (x, y) in enumerate(dataloader):
            x, y = x.to(device), y.to(device)
            pred = model(x)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        test_loss /= num_batches
        correct /= size

    print(f"test Error: \n Accuracy: {(100*correct):>0.1f}%, avg loss: {test_loss: > 8f}")
```

`test()` 用来在测试集上打分，逻辑和 `train()` 很像，关键差别都是为了"只评估、不训练"：

- `model.eval()`：切换到评估模式——`Dropout` 不再随机丢弃（全部神经元都参与），`BatchNorm1d` 改用训练过程中累积下来的统计量，而不是当前这一批的统计量，这样同一张图不管在哪个 batch 里，预测结果都是确定、可复现的。
- `with torch.no_grad()`：评估不需要反向传播，不用算梯度，省显存、算得更快。
- `correct += (pred.argmax(1) == y).type(torch.float).sum().item()`：这一行是算"猜对了几张"的核心逻辑，拆开看——`pred.argmax(1)` 在每张图的 10 个分数里取最大值所在的位置（模型认为最可能的数字）；`== y` 和真实标签逐个比较，得到一串 `True`/`False`；`.type(torch.float)` 把它们转成 `1.0`/`0.0`；`.sum()` 加起来就是这一批猜对的张数；`.item()` 转成普通数字，累加进 `correct`。
- 最后 `test_loss /= num_batches` 算出平均每批的损失，`correct /= size` 算出总的准确率（猜对张数 ÷ 总张数）。

### 第六步：真正开始训练——跑 20 轮

```python
epochs = 20

for epoch in range(epochs):
    print(f"{epoch+1}/{epochs}")
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)

print("Finished traning!")
```

逻辑很直接：把前面写好的 `train()` 和 `test()` 各调用 20 次，每轮先在训练集上更新一遍权重,再在测试集上打一次分。真实跑出来的部分结果：

| Epoch | 测试集准确率 | 平均 loss |
|-|-|-|
| 1 | 98.2% | 0.0582 |
| 5 | 98.3% | 0.0544 |
| 10 | 98.3% | 0.0552 |
| 15 | 98.4% | 0.0532 |
| 20 | 98.4% | 0.0531 |

**两个值得注意的细节**：

- **第 1 轮结束就已经 98.2% 了**，后面 19 轮只把准确率往上磨了 0.2 个百分点（98.2% → 98.4%），loss 也一直在 0.05~0.06 之间小幅波动，没有再明显下降——这说明这个模型在 MNIST 这个任务上很快就"学到头"了，也印证了 Part 2 里说的"MNIST 对现在的模型来说已经不难"。真要看模型能力的差距，得换更难的数据集（比如 Fashion-MNIST）才看得出来。
- **训练过程中打印的单个 batch loss 不是一路下降的**（比如某一轮里 0.105 → 0.087 → 0.111 → 0.078，中间还会往上跳）——这是正常的，因为每次打印的是"这一个 batch"的损失，batch 和 batch 之间数据不同、难度不同，本身就会有噪声。想看训练是否真的在变好，应该看 `test()` 打印出来的整体准确率趋势，而不是紧盯单个 batch 的 loss 有没有下降。

### 第七步：保存训练好的模型

```python
torch.save(model.state_dict(), "model_weights.pth")
print("saved pytorch model")
```

`model.state_dict()` 是模型里所有权重、偏置的一份快照，`torch.save()` 把它存成一个文件。这里存成了 `model_weights.pth`——`.pth`（PyTorch 的缩写）和前面提到过的 `.pt` 是同一回事,都只是约定俗成的文件扩展名,没有格式上的区别,存的都是 `state_dict` 这份参数快照。之后要用这个模型，需要先照着同样的 `NeuralNetwork` 类建好网络骨架，再用 `load_state_dict()` 把这些数字加载回去。

## 术语表

### Batch Normalization（批归一化） {.ignore-header}

在网络的每一层输出上，用当前这批（batch）数据算出的均值和标准差做一次归一化，让传给下一层的数值范围更稳定，训练更快更稳。评估模式（`model.eval()`）下会改用训练过程中累积的统计量，而不是当前批次的。

### Dropout（随机丢弃） {.ignore-header}

训练时按一定比例（比如 0.5 = 50%）随机把某些神经元的输出临时设成 0，防止网络过度依赖某几个神经元、死记硬背训练数据。只在训练模式下生效，评估模式下所有神经元都正常参与。

### argmax {.ignore-header}

从一组数字里找出"最大值所在的位置（索引）"，而不是最大值本身。`pred.argmax(1)` 是在每张图的 10 个类别分数里，找出分数最高的那个类别的编号，也就是模型的最终预测结果。

### epoch / batch 回顾 {.ignore-header}

一次完整遍历训练集叫一个 epoch；训练集被切成的每一小份叫一个 batch。本篇 `BATCH_SIZE=128`，60000 张训练图对应每个 epoch 469 个 batch，一共训练了 20 个 epoch。

### state_dict {.ignore-header}

模型里所有可训练参数（权重、偏置）的一份字典快照，`torch.save(model.state_dict(), path)` / `model.load_state_dict(...)` 是保存和加载模型最常用的方式。
