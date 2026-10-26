---
outline: [2,3]
---

# ROS 2 基础

## Part 1：认识 ROS 2

### ROS 是什么

> **一句话理解：ROS 就是一个"让机器人里各个小程序互相说话"的工具箱。**

一台机器人要做很多事：读摄像头、识别物体、规划路线、控制电机。ROS（Robot Operating System，机器人操作系统）把每件事写成一个独立的小程序，叫**节点（Node）**，再负责让这些小程序互相传数据。

**打个比方**：节点是公司里的员工，ROS 是公司的工作群。员工不用知道彼此坐在哪，只要在对应的频道里发消息、收消息就行。

ROS 名字里有"操作系统"，但它**不是** Windows、Ubuntu 那种系统，而是装在 Ubuntu 上的一套软件。

### ROS 与 ROS 2 的发展时间线

#### 时间线

```
2007  斯坦福大学的机器人项目里诞生雏形，随后由 Willow Garage 公司接手开发
2010  ROS 1 第一个正式版本发布（Box Turtle）
2012  成立开源机器人基金会（OSRF，Open Source Robotics Foundation）专门维护 ROS
        ↓  ROS 1 在学校和实验室里大量使用
2014  开始设计 ROS 2，要解决 ROS 1 的老问题
2017  ROS 2 第一个正式版本发布（Ardent）
2020  ROS 1 最后一个版本 Noetic 发布；同年 ROS 2 Foxy 发布，ROS 2 开始成熟
2022  ROS 2 Humble（长期支持版），资料最多，用的人最多
2024  ROS 2 Jazzy（长期支持版），目前的主流选择
2025  ROS 1 正式停止维护，从此只剩 ROS 2
2026  ROS 2 Lyrical（长期支持版）
```

#### 为什么要从头做一个 ROS 2

ROS 1 一开始是给实验室做研究用的，用到真实产品上就暴露出几个毛病：

| 问题 | ROS 1 | ROS 2 |
|---|---|---|
| 有没有"总管" | 必须先启动 `roscore`，它一挂，全部节点都断 | 没有总管，节点自己互相找到对方 |
| 网络不稳定时 | 容易断连 | 底层换成工业标准 DDS（Data Distribution Service，数据分发服务），可以设置"丢了要不要重发" |
| 多台机器人 | 很难支持 | 原生支持 |
| 实时性、安全性 | 基本没考虑 | 在设计时就考虑了 |

**一句话总结：ROS 1 是实验室原型，ROS 2 是为了上真实产品重新做的版本。新学的话直接学 ROS 2。**

#### 版本规律

每年 5 月发一个新版本，名字按字母顺序排：

```
Foxy → Galactic → Humble → Iron → Jazzy → Kilted → Lyrical
```

偶数年的版本是**长期支持版（LTS，Long-Term Support）**，维护 5 年，最适合拿来学习和做项目。

### rclpy 和 rclcpp

这两个是你写 ROS 2 程序时实际用的**客户端库（Client Library）**，作用一模一样：创建节点、发消息、收消息。区别只在用什么语言写。

| | **rclpy** | **rclcpp** |
|---|---|---|
| 语言 | Python | C++ |
| 名字含义 | ROS Client Library for **Py**thon | ROS Client Library for **C++** |
| 优点 | 代码短、不用编译、上手快 | 运行快、功能全 |
| 缺点 | 处理大数据（图像、点云）时较慢 | 代码长、要编译、上手难 |
| 适合做 | 任务逻辑、发控制指令、快速试验 | 摄像头驱动、图像处理、高频控制 |

**举个例子**：同样是"每 0.5 秒发一条 hello"，rclpy 大约 15 行代码，写完就能直接运行；rclcpp 大约 30 行，还要配置 CMake 并编译。

**最关键的一点：两者可以混着用。** 它们底层走的是同一套通信系统，所以 Python 节点和 C++ 节点能直接互相收发消息。一般先用 Python 把整个系统跑通，哪个节点太慢了，再单独把它改写成 C++。

## Part 2：节点、话题和消息

> **一句话理解：节点负责干活，话题负责传数据，消息规定传的数据长什么样。**

这一部分只讲概念，不写代码。全程用同一个例子：**飞手用地面站控制无人机飞行，机上的相机负责拍照，画面里一出现烟或火就报警。**

### 节点（Node）

节点就是**一个只负责一件事的小程序**。每个节点只做自己那件事，做完就把结果发出去，需要的节点再接着用。节点之间不直接调用对方的代码，只靠 ROS 2 传数据。

**打个比方**：还是 Part 1 里的公司。每个员工（节点）只干自己的活，干完把结果发到工作群里，下一个员工看到了再接着干。

野火报警里，飞行由飞手负责，ROS 2 这边只要 3 个节点：

```
[相机节点] ──照片──▶ [烟火识别节点] ──"有烟火！"──▶ [报警节点] ──▶ 地面站
```

| 节点 | 只负责一件事 |
|---|---|
| 相机节点 | 拍照，把照片发出去 |
| 烟火识别节点 | 用 YOLO26 看照片里有没有烟或火 |
| 报警节点 | 收到"有烟火"，就通知地面站的飞手 |

**拆开的好处**：
- **一个出错不影响其他**：识别节点崩了，相机节点照样在拍，重启识别节点就能接着用。
- **改一个不用动其他**：训练出一个更准的烟火识别模型，只需要换掉识别节点里的模型文件，相机节点和报警节点一行都不用改。

### 话题（Topic）

> **一句话理解：话题（Topic）就像一个"广播频道"，有人往频道里喊话，订阅了这个频道的人就都能听到。**

节点之间"传数据"，最常用的方式就是**话题通信（Topic Communication）**。喊话的人不需要知道谁在听，听的人也不需要知道是谁在喊。

#### 三个角色和一份"数据"

| 概念 | 英文 | 作用 | 类比 |
|---|---|---|---|
| 发布者 | Publisher | 往话题里发数据 | 电台主播 |
| 订阅者 | Subscriber | 从话题里收数据 | 收音机听众 |
| 话题 | Topic | 数据走的"频道名"，比如 `/camera/image` | 电台频率，比如 FM 101.7 |
| 消息 | Message | 话题里传的那份数据本身 | 主播说的那段话 |

一个节点可以同时当发布者和订阅者。比如烟火识别节点：订阅照片，再发布识别结果。

#### 用野火报警串起来

把上面的 3 个节点换成话题来连：

```
[相机节点] ──发布──▶ /camera/image ──订阅──▶ [烟火识别节点] ──发布──▶ /fire_alert ──订阅──▶ [报警节点]
                                   └──订阅──▶ [录像节点]
```

- 相机节点每秒往 `/camera/image` 发 30 张照片。
- 烟火识别节点和录像节点**同时**订阅它，各拿一份，互不干扰。
- 相机节点根本不知道有几个节点在用它的照片，这就叫**解耦（Decoupling）**。

**好处**：以后想加一个"把画面传回地面站"的节点，只要新写一个订阅 `/camera/image` 的节点，**相机节点一行都不用改**。

#### 话题通信的特点

1. **多对多**：一个话题可以有多个发布者，也可以有多个订阅者。
2. **单向、异步（Asynchronous）**：发布者发完就继续干自己的事，不等回复。好比群里发通知，发完就走，不管谁看了没。
3. **适合持续不断的数据流**：传感器数据、位置、速度这类一直在更新的东西。

如果需要"问一句、等一句回答"，比如"请拍一张照片，拍完告诉我存在哪"，话题就不合适了，要用另一种通信方式：**服务（Service）**，见后面的 Part 6。

### 消息（Message）

话题里不能随便塞东西，每个话题都规定了一种**消息类型（Message Type）**，就像一张固定格式的表格，每一格填什么都定好了。

ROS 2 自带很多常用的消息类型：

| 消息类型 | 装的是什么 | 野火报警里谁在用 |
|---|---|---|
| `std_msgs/msg/String` | 一段文字 | 简单的报警文字，比如"发现烟火" |
| `sensor_msgs/msg/Image` | 一张图片：宽、高、编码方式、像素数据 | 相机节点发的照片 |
| `geometry_msgs/msg/Point` | 一个点的坐标 x、y、z | 火点的位置 |

也可以自己定义消息（具体做法见后面的 Part 5）。比如一条"烟火警报"消息可以这样设计：

| 字段 | 类型 | 举例 |
|---|---|---|
| 目标类别 | 文字 | `fire` |
| 置信度（Confidence） | 小数 | `0.92`，表示 YOLO26 有 92% 的把握 |
| 画面里的位置 | 4 个整数 | 框的左上角 `(120, 80)`、宽 `60`、高 `45` |

**最关键的一点：发布者和订阅者的话题名、消息类型都必须完全一致，才能通信。** 话题名差一个字母（`/fire_alert` 和 `/fire_alarm`），或者一边发 `String`、另一边按 `Image` 收，都会**什么都收不到，而且不会报错**。这是新手排查问题时最容易忽略的地方。

### QoS：丢了要不要重发

Part 1 提到 ROS 2 的底层是 DDS，可以设置"丢了要不要重发"，这个设置就叫 **QoS（Quality of Service，服务质量）**。最常用的是可靠性这一项：

| 模式 | 意思 | 类比 | 适合 |
|---|---|---|---|
| Reliable（可靠） | 保证送到，丢了就重发 | 挂号信 | 控制指令、报警消息，一条都不能丢 |
| Best Effort（尽力而为） | 发了就算，丢了不管 | 看直播，卡了一帧就直接跳过 | 摄像头照片，每秒 30 张，丢一两张无所谓，更看重快 |

**举个例子**：`/camera/image` 用 Best Effort，网络卡顿时丢掉几张旧照片，烟火识别节点直接拿最新的一张来识别；`/fire_alert` 用 Reliable，因为漏掉一条"发现火"的警报后果严重。

**一个常见的坑**：发布者用 Best Effort、订阅者用 Reliable，两边**不兼容，订阅者收不到任何数据**。订阅者要求"保证送到"，发布者却做不到。反过来（发布者 Reliable、订阅者 Best Effort）是可以的。PX4 通过 uXRCE-DDS 发到 ROS 2 的话题大多是 Best Effort，所以订阅 PX4 的话题时，要把订阅者的 QoS 也设成 Best Effort。

## Part 3：功能包和工作空间

> **一句话理解：功能包是装节点代码的文件夹，工作空间是装功能包的总文件夹。**

三个概念一层套一层：

```
工作空间（Workspace）  ⊃  功能包（Package）  ⊃  节点（Node）
      公司大楼                   部门                 员工
```

一个工作空间里可以放很多功能包，一个功能包里可以有好几个节点。下面接着用野火报警的 3 个节点。

### 功能包（Package）

功能包就是**装节点代码的文件夹**，再加一张"说明书"，写明包名和它依赖哪些别的包。它是 ROS 2 里打包、分享代码的基本单位。

**打个比方**：节点是员工，功能包是部门。招人、搬家、交接工作都按部门整体来办。

野火报警的 3 个节点可以这样分到包里：

| 功能包 | 里面的节点 | 来源 |
|---|---|---|
| `usb_cam` | 相机节点 | **别人写好的**，一条命令就能装上：`sudo apt install ros-jazzy-usb-cam` |
| `fire_alert` | 烟火识别节点、报警节点 | **你自己写的** |

这就是功能包最大的用处：**别人做好的功能，直接装上就能用**。相机驱动这种通用的东西，不用自己从头写。

你自己写的 `fire_alert` 包（Python 版）大概长这样（省略了几个自动生成的文件）：

```
fire_alert/
├── package.xml      ← 说明书：包名、作者、依赖哪些包
├── setup.py         ← 告诉 ROS 2 这个包里有哪些节点
└── fire_alert/
    ├── detector.py  ← 烟火识别节点
    └── alarm.py     ← 报警节点
```

运行节点时先写包名，再写节点名，就像先找部门、再找人：

```bash
ros2 run usb_cam usb_cam_node_exe    # 启动相机节点
ros2 run fire_alert detector         # 启动烟火识别节点
ros2 run fire_alert alarm            # 启动报警节点
```

### 工作空间（Workspace）

工作空间就是**放你自己写的功能包的总文件夹**，你在这里写代码、编译、运行。

上面的 `fire_alert` 包要放进一个工作空间，比如叫 `fire_ws`：

```
~/fire_ws/              ← 工作空间
├── src/                ← 你只需要管这里：所有功能包的源代码
│   └── fire_alert/
├── build/              ← 编译时的中间文件（自动生成）
├── install/            ← 编译好、可以运行的结果（自动生成）
└── log/                ← 编译日志（自动生成）
```

一开始只要建好 `src/`，另外三个文件夹会在编译时自动出现。

那 `usb_cam` 在哪？用 `apt` 装的包会装进系统里的 ROS 2 目录，**不在你的工作空间里**：

| | 放在哪 | 怎么来的 |
|---|---|---|
| `usb_cam` | `/opt/ros/jazzy` | 别人写的，`apt` 直接装 |
| `fire_alert` | `~/fire_ws/src` | 你自己写的，要自己编译 |

### 从建工作空间到运行

一共 4 步：

```bash
# 1. 建工作空间，在 src 里创建功能包
mkdir -p ~/fire_ws/src
cd ~/fire_ws/src
ros2 pkg create --build-type ament_python fire_alert

# 2. 回到工作空间根目录，编译
cd ~/fire_ws
colcon build

# 3. 告诉当前终端："我的包在这里"
source install/setup.bash

# 4. 运行
ros2 run fire_alert detector
```

**注意**：一定要在工作空间**根目录**（`~/fire_ws`）运行 `colcon build`，不要在 `src/` 里运行，否则 `build/`、`install/` 会生成到错误的位置。

### 为什么每个终端都要 `source`

> **一句话理解：`source install/setup.bash` 就是告诉当前这个终端："我自己写的包装在 `~/fire_ws/install` 里，找包、找 Python 模块时也去那里找。"**

`setup.bash` 里主要是一堆 `export`，设置这几个**环境变量（Environment Variable）**：

| 环境变量 | 作用 | 不设置会怎样 |
|---|---|---|
| `AMENT_PREFIX_PATH` | ROS 2 去哪些目录找功能包 | `ros2 run fire_alert camera` 报 `Package 'fire_alert' not found` |
| `PYTHONPATH` | Python 去哪些目录找模块 | `ModuleNotFoundError: No module named 'fire_alert_interfaces'` |
| `PATH` | 去哪些目录找可执行程序 | 找不到命令 |
| `LD_LIBRARY_PATH` | 去哪些目录找 C/C++ 动态库（`.so`） | C++ 节点启动时找不到库 |

可以亲手对比一下：

```bash
$ echo $AMENT_PREFIX_PATH
/opt/ros/jazzy                       # 只有系统自带的包

$ source ~/fire_ws/install/setup.bash
$ echo $AMENT_PREFIX_PATH
/home/tony/fire_ws/install/fire_alert:/opt/ros/jazzy     # 你的包被加到了最前面
```

**为什么每个终端都要来一次？** 在 Linux 里，每个终端都是一个独立的**进程（Process）**，环境变量存在这个进程自己的内存里：

```
终端 A：source 过   →  AMENT_PREFIX_PATH 里有 fire_alert   ✅
终端 B：新开的      →  AMENT_PREFIX_PATH 里只有 /opt/ros   ❌
```

**打个比方**：环境变量是贴在**这一个**终端上的便利贴。终端 A 贴了"去 `~/fire_ws/install` 找包"，终端 B 上并没有这张便利贴；关掉终端 A，便利贴也跟着扔了。

**为什么必须用 `source`，不能直接 `./install/setup.bash`？** 直接运行会先开一个**子进程**执行脚本，变量都设在子进程里，脚本跑完子进程退出，变量也就没了。`source` 是在**当前终端里**一行一行执行，设置才能留下来。

**两个 `setup.bash`**：

| 文件 | 负责什么 | 名称 |
|---|---|---|
| `/opt/ros/jazzy/setup.bash` | ROS 2 本身：`rclpy`、`std_msgs`、`ros2` 命令 | 底层（Underlay） |
| `~/fire_ws/install/setup.bash` | 你自己写的包 | 上层（Overlay） |

编译时如果已经 source 过系统那个，`install/setup.bash` 会把它一起带上，所以平时只 source 工作空间这一个就够了。

**什么时候要重新 `source`**：

| 情况 | 要不要 |
|---|---|
| 新开一个终端 | ✅ 要 |
| **第一次**编译出一个新包（比如 Part 5 新建的 `fire_alert_interfaces`） | ✅ 要，`source` 只会登记当时已经存在的包 |
| 改了 `.msg` 并重新编译 | ✅ 建议重新 source，并重启节点 |
| 只改了 Python 节点代码，且编译时用了 `--symlink-install` | ❌ 不用，直接重新运行 |

**省事的办法：写进 `~/.bashrc`**。每次新开终端都会自动执行一遍 `~/.bashrc`：

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/fire_ws/install/setup.bash" >> ~/.bashrc
```

第二行要等工作空间至少编译过一次、`install/` 已经存在之后再加，否则每次开终端都会报"找不到文件"。如果同时有好几个工作空间，最好只把系统那一行写进 `.bashrc`，工作空间手动 source，免得几个工作空间的包互相串了。

## Part 4：用 rclpy 写两个会通信的节点

> **一句话理解：相机节点每秒往话题 `/camera/photo` 里"喊"一句"拍到 photo_1.jpg 了"，识别节点订阅这个话题，每听到一句就开始识别。**

这一节就用野火报警里最前面的两个节点，写出能真正跑起来的代码：

```
[相机节点 camera] ──发布──▶ /camera/photo ──订阅──▶ [识别节点 detector]
```

### 先设计话题

写代码之前，先把"频道"定下来。两边必须用**同一个话题名、同一种消息类型**（Part 2 里说过，差一点就什么都收不到）：

| 项目 | 设计 | 说明 |
|---|---|---|
| 话题名 | `/camera/photo` | 频道名，两个节点都写这个 |
| 消息类型 | `std_msgs/msg/String` | 一段文字，最简单的消息 |
| 消息内容 | `photo_1.jpg`、`photo_2.jpg`…… | 用文件名假装是一张照片 |
| 发布者 | 相机节点 `camera` | 每 1 秒发一条 |
| 订阅者 | 识别节点 `detector` | 收到一条就处理一条 |

**为什么不直接发真照片？** 发真照片要用 `sensor_msgs/msg/Image`，还要用 `cv_bridge` 在 ROS 图片和 OpenCV 图片之间转换，代码会多一倍。先用一段文字把"发 → 收"的流程跑通，以后把 `String` 换成 `Image`，**整体结构完全不变**。

### 相机节点：发布者（camera.py）

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class CameraNode(Node):
    def __init__(self):
        super().__init__("camera")
        self.publisher = self.create_publisher(String, "/camera/photo", 10)
        self.timer = self.create_timer(1.0, self.take_photo)
        self.count = 0

    def take_photo(self):
        self.count += 1
        msg = String()
        msg.data = f"photo_{self.count}.jpg"
        self.publisher.publish(msg)
        self.get_logger().info(f"拍了一张：{msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    rclpy.shutdown()
```

逐行讲解：

| 代码 | 意思 |
|---|---|
| `import rclpy` | 导入 ROS 2 的 Python 客户端库（Part 1） |
| `from rclpy.node import Node` | 导入节点基类，所有节点都从它继承 |
| `from std_msgs.msg import String` | 导入"一段文字"这种消息类型 |
| `class CameraNode(Node):` | 定义相机节点。继承 `Node` 后，自动拥有发布、订阅、定时器、日志这些能力 |
| `super().__init__("camera")` | 把节点注册到 ROS 2，**节点名**叫 `camera`。这一行必须写 |
| `self.create_publisher(String, "/camera/photo", 10)` | 创建发布者，三个参数：**发什么类型**（`String`）、**发到哪个话题**（`/camera/photo`）、**队列长度**（`10`，下面细讲） |
| `self.create_timer(1.0, self.take_photo)` | 创建定时器：每 1.0 秒自动调用一次 `take_photo`。注意 `take_photo` 后面**没有括号**，是把函数"交给"定时器，而不是现在就调用 |
| `self.count = 0` | 计数器，记录拍到第几张 |
| `def take_photo(self):` | 定时器的**回调函数（Callback）**：每次定时器到点，就执行这里面的代码 |
| `self.count += 1` | 张数加 1 |
| `msg = String()` | 拿一张空白的 `String` "表格" |
| `msg.data = f"photo_{self.count}.jpg"` | 往表格的 `data` 格里填内容。`String` 只有 `data` 这一格 |
| `self.publisher.publish(msg)` | **发出去**：把这条消息发到 `/camera/photo` 话题里 |
| `self.get_logger().info(...)` | 打印一行日志，方便看到"确实发了" |
| `rclpy.init(args=args)` | ① 开机：初始化 ROS 2 |
| `node = CameraNode()` | ② 创建节点：发布者、定时器都在这一步建好 |
| `rclpy.spin(node)` | ③ 一直运行：定时器每到 1 秒，`spin` 就去调用一次 `take_photo` |
| `rclpy.shutdown()` | ④ 关机：释放资源 |

**队列长度 `10` 是什么？** 发布者手里有一个"待发箱"，最多放 10 条。比如网络突然卡了 3 秒，这 3 秒里拍的 3 张照片先放在待发箱里排队，网络好了再发。如果卡太久、攒到第 11 条，最旧的那条就被扔掉。这是 Part 2 里 QoS 的一部分，**新手直接写 `10` 就行**。

### 识别节点：订阅者（detector.py）

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DetectorNode(Node):
    def __init__(self):
        super().__init__("detector")
        self.subscription = self.create_subscription(
            String, "/camera/photo", self.on_photo, 10
        )

    def on_photo(self, msg):
        self.get_logger().info(f"收到 {msg.data}，开始识别烟火...")

def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    rclpy.spin(node)
    rclpy.shutdown()
```

前 3 行导入和最后的 `main` 跟相机节点完全一样，只讲不一样的地方：

| 代码 | 意思 |
|---|---|
| `super().__init__("detector")` | 节点名叫 `detector` |
| `self.create_subscription(String, "/camera/photo", self.on_photo, 10)` | 创建订阅者，四个参数：**收什么类型**（`String`）、**听哪个话题**（`/camera/photo`）、**收到后交给谁处理**（`self.on_photo`）、**队列长度**（`10`） |
| `def on_photo(self, msg):` | 订阅的回调函数。每收到一条消息，ROS 2 就调用它一次，并把消息作为 `msg` 传进来 |
| `msg.data` | 取出消息里的文字，比如 `photo_3.jpg` |

**对比着看，发布和订阅几乎是对称的：**

| | 相机节点（发布者） | 识别节点（订阅者） |
|---|---|---|
| 创建 | `create_publisher(类型, 话题, 10)` | `create_subscription(类型, 话题, 回调, 10)` |
| 谁触发 | 定时器每 1 秒触发 `take_photo` | 新消息到达触发 `on_photo` |
| 干什么 | `publish(msg)` 把消息发出去 | 从 `msg.data` 读出内容 |

真实项目里，`on_photo` 里面就是"把照片交给 YOLO26 推理，发现烟火就再发布到 `/fire_alert`"，结构和这里一模一样，只是函数体变长了。

**三个"名字"别搞混：**

| 名字 | 例子 | 是什么 | 在哪能看到 |
|---|---|---|---|
| 类名 | `CameraNode` | Python 里的类名，随便起 | 只在代码里 |
| 节点名 | `camera` | 节点在 ROS 2 里的名字 | `ros2 node list` |
| 话题名 | `/camera/photo` | 数据走的频道 | `ros2 topic list` |

**真正决定两个节点能不能通信的，只有话题名和消息类型。** 类名、节点名、文件名都不影响。

### 跑起来看看

1. 把 `camera.py` 放到 Part 3 的 `fire_alert/fire_alert/` 文件夹里，和 `detector.py` 放一起。
2. 在 `setup.py` 里登记这两个节点，告诉 ROS 2 "`ros2 run` 时这个名字对应哪个文件的 `main`"：

```python
entry_points={
    'console_scripts': [
        'camera = fire_alert.camera:main',      # ros2 run fire_alert camera   → camera.py 的 main()
        'detector = fire_alert.detector:main',  # ros2 run fire_alert detector → detector.py 的 main()
    ],
},
```

3. 在 `package.xml` 里加上依赖（用 `ros2 pkg create ... --dependencies rclpy std_msgs` 创建包时会自动加好）：

```xml
<depend>rclpy</depend>
<depend>std_msgs</depend>
```

4. 编译，然后**开两个终端**，各自 `source` 后运行一个节点（节点多了以后，可以用 Part 7 的 launch 一条命令全部启动）：

```bash
cd ~/fire_ws && colcon build
```

```bash
# 终端 1
source ~/fire_ws/install/setup.bash
ros2 run fire_alert camera
```

```bash
# 终端 2
source ~/fire_ws/install/setup.bash
ros2 run fire_alert detector
```

两个终端各自每秒多一行（时间戳省略）：

```
# 终端 1（相机）
[INFO] [...] [camera]: 拍了一张：photo_1.jpg
[INFO] [...] [camera]: 拍了一张：photo_2.jpg
[INFO] [...] [camera]: 拍了一张：photo_3.jpg

# 终端 2（识别）
[INFO] [...] [detector]: 收到 photo_2.jpg，开始识别烟火...
[INFO] [...] [detector]: 收到 photo_3.jpg，开始识别烟火...
```

识别节点没收到 `photo_1.jpg`，因为它比相机晚启动，第 1 张发出去时还没人在听。就像收音机晚开了几秒，错过的节目不会补播。

### 用命令行"偷看"话题

再开第 3 个终端（记得 `source`），不用写代码就能检查话题：

| 命令 | 输出 | 用途 |
|---|---|---|
| `ros2 topic list` | `/camera/photo`（还有两个系统自带的话题） | 看现在有哪些话题 |
| `ros2 topic echo /camera/photo` | `data: photo_7.jpg`，然后每秒一条 | 直接偷听话题内容，相当于临时加了一个订阅者 |
| `ros2 topic info /camera/photo` | `Type: std_msgs/msg/String`、`Publisher count: 1`、`Subscription count: 1` | 看类型、有几个发布者和订阅者 |
| `ros2 topic hz /camera/photo` | `average rate: 1.000` | 看每秒发多少条 |

**排查"收不到"时最有用的是 `ros2 topic info`**。比如识别节点里不小心把话题写成了 `/camera/photos`（多了个 s），它不会报错，只是一直安静。这时用 `ros2 topic list` 会看到**两个**话题：`/camera/photo` 和 `/camera/photos`，再用 `info` 分别看：`/camera/photo` 是"1 个发布者、0 个订阅者"，`/camera/photos` 是"0 个发布者、1 个订阅者"。两边各说各的，问题一眼就出来了。

### 回头看：每个 rclpy 程序都是四步

两个节点的 `main` 都是同样四步，可以对应成开一家店：

| 步骤 | 代码 | 类比 | 实际做了什么 |
|---|---|---|---|
| ① | `rclpy.init()` | 拉开卷帘门、接通电源 | 初始化 ROS 2 的通信底层（DDS），并解析命令行参数 |
| ② | `CameraNode()` | 店员上岗 | 创建节点，注册名字 `camera`，建好发布者和定时器 |
| ③ | `rclpy.spin(node)` | 店员守在柜台前等客人 | 卡在这里不停循环：有新消息、定时器到点，就调用对应的回调函数 |
| ④ | `rclpy.shutdown()` | 关门、断电 | 释放 ROS 2 占用的资源 |

**顺序不能乱**：没 `init` 就创建节点会直接报错；`shutdown` 之后不能再创建节点或收发消息。

### `spin` 为什么必不可少

`spin` 的意思是"转圈"。它就是一个死循环，每转一圈都检查一遍"有没有事要干"：

```
while 没按 Ctrl+C:
    有新消息到了？   → 调用订阅回调（识别节点的 on_photo）
    定时器到点了？   → 调用定时器回调（相机节点的 take_photo）
    都没有？         → 继续等
```

回头看两个节点的代码，你会发现**我们从来没有自己调用过 `take_photo` 或 `on_photo`**，只是在 `__init__` 里把它们"登记"给了定时器和订阅者。真正去调用它们的是 `spin`。

- **有 `spin`**：相机每秒拍一张，识别节点每秒收一张。
- **没有 `spin`**：程序执行完第 ② 步就直接走到 `shutdown`，然后结束。相机一张都不会拍，识别节点一条都收不到，节点"上岗一秒就下班"。

**一句话：回调函数只是"登记"了要做什么，真正去执行它们的是 `spin`。**

### 更稳妥的写法：按 Ctrl+C 不报错

上面的 `main` 按 Ctrl+C 时，终端会刷出一大段 `KeyboardInterrupt` 报错，而且 `spin` 被打断后，后面的 `shutdown` 根本执行不到。实际项目里一般这样写（两个节点都一样，只是类名不同）：

```python
def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass                    # 按 Ctrl+C 是正常退出，不当成错误
    finally:
        node.destroy_node()     # 不管怎么退出，都先销毁节点
        rclpy.shutdown()        # 再关闭 ROS 2
```

`finally` 里的代码**无论正常结束还是被打断都会执行**，保证"关门断电"这一步一定做完。

### 常用方法速查

| 方法 | 作用 | 什么时候用 |
|---|---|---|
| `rclpy.init(args=args)` | 初始化 ROS 2 | 程序最开头，**只调一次** |
| `self.create_publisher(类型, 话题, 10)` | 创建发布者 | 节点要往外发数据时 |
| `self.create_subscription(类型, 话题, 回调, 10)` | 创建订阅者 | 节点要接收数据时 |
| `self.create_timer(秒数, 回调)` | 创建定时器，每隔几秒调用一次回调 | 需要定期干活，比如每秒拍一张 |
| `publisher.publish(msg)` | 把一条消息发到话题 | 在定时器回调或订阅回调里 |
| `rclpy.spin(node)` | 一直运行节点，处理所有回调，直到 Ctrl+C | 最常用，99% 的节点都这样写 |
| `rclpy.spin_once(node, timeout_sec=0.1)` | 只转**一圈**：处理一个回调就返回，最多等 0.1 秒 | 想在自己的 `while` 循环里顺便处理消息时 |
| `rclpy.ok()` | 返回 `True`/`False`：ROS 2 是否还在运行 | 配合 `spin_once` 写循环：`while rclpy.ok():` |
| `node.destroy_node()` | 销毁节点，释放它的发布者、订阅者、定时器 | `shutdown` 之前，显式清理 |
| `rclpy.shutdown()` | 关闭 ROS 2 | 程序最后，**只调一次** |
| `self.get_logger().info("...")` | 打印 INFO 日志，自动带时间戳和节点名 | 代替 `print()` |

**注意：没有 `rclpy.close()` 这个方法**，关闭用的是 `rclpy.shutdown()`。容易记混，因为很多别的库用 `close()`。

**日志（Logger）分 5 个级别**，从轻到重：`debug` → `info` → `warn` → `error` → `fatal`。比 `print()` 好的地方在于输出自带节点名，比如 `[camera]`、`[detector]`。系统里同时跑十几个节点时，看前缀就知道是谁打印的。

## Part 5：自定义消息

> **一句话理解：`.msg` 文件就是一张自己设计的"表格模板"。编译时 ROS 2 把它翻译成 Python 类和 C++ 结构体，节点里像用 `String` 一样 `import` 进来就能用。**

### 为什么 `String` 不够用

Part 4 的相机节点只发了一个文件名 `photo_3.jpg`。现在识别节点还想知道**这是第几张**、**拍照时无人机飞多高**（高度不同，火在画面里的大小不同）。

如果硬塞进 `String`，只能拼成一串文字，再让对方拆开：

```python
# 相机节点：拼
msg.data = "3,photo_3.jpg,50.0"

# 识别节点：拆
id_str, filename, alt_str = msg.data.split(",")
altitude = float(alt_str)
```

问题很明显：

- **顺序全靠约定**：哪天相机节点把高度挪到第一个，识别节点不会报错，只会把 `50.0` 当成张数，悄悄算错。
- **类型全靠手动转换**：`"50.0"` 是文字，每次都要自己 `float()`。
- **别人看不懂**：`ros2 topic echo` 只能看到一串 `"3,photo_3.jpg,50.0"`，不知道每一段是什么意思。

换成自定义消息后，每个字段都有**名字**和**类型**：

```python
msg.id = 3
msg.filename = "photo_3.jpg"
msg.altitude = 50.0
```

对方用 `msg.altitude` 直接取，拿到的就是小数，不用拆也不用转。

### 设计 `PhotoInfo.msg`

```
uint32 id          # 第几张，从 1 开始
string filename    # 文件名，比如 photo_3.jpg
float32 altitude   # 拍照时无人机的高度，单位：米
```

格式就是**一行一个字段：`类型 字段名`**，`#` 后面是注释。

**命名规则（写错会编译失败）：**

| 写什么 | 规则 | 正确 | 错误 |
|---|---|---|---|
| 文件名 | 大驼峰（CamelCase），首字母大写 | `PhotoInfo.msg` | `photo_info.msg` |
| 字段名 | 小写加下划线（snake_case） | `altitude`、`frame_id` | `Altitude`、`frameId` |

**常用字段类型：**

| 类型 | 装什么 | 例子 |
|---|---|---|
| `bool` | 真/假 | `bool is_fire` |
| `int32` / `uint32` | 整数 / 非负整数 | `uint32 id` |
| `float32` / `float64` | 小数（单精度 / 双精度） | `float32 confidence` |
| `string` | 文字 | `string label` |
| `类型[]` | 列表，长度不固定 | `float32[] scores` |
| `包名/消息名` | 嵌套别的消息 | `std_msgs/Header header`（带时间戳和坐标系名） |

**Python 里对应的类型**：`uint32` → `int`，`float32` → `float`，`string` → `str`，`float32[]` → 列表（或数组）。赋值时类型不对会直接报错，比如 `msg.id = "3"` 会抛 `AssertionError`。这正是自定义消息比 `String` 安全的地方。

### 第 1 步：建一个专门放消息的包

Part 4 之后的工作空间里只有一个 `fire_alert` 包。现在再加一个 `fire_alert_interfaces`：

```bash
cd ~/fire_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 fire_alert_interfaces
cd fire_alert_interfaces
rm -rf include src      # 这两个是给 C++ 代码准备的空文件夹，接口包用不上
mkdir msg
```

然后把上面的内容存成 `msg/PhotoInfo.msg`。

**为什么必须是 `ament_cmake`？** 把 `.msg` 翻译成 Python 和 C++ 代码的工具叫 `rosidl`，它只能在 CMake 构建流程里运行，`ament_python` 包的 `setup.py` 调用不了它。截至 Lyrical（2026 年 5 月发布的 LTS），这一点仍然没有变。所以**消息放 CMake 包，节点照样写 Python**，两边互不影响。

### 第 2 步：在 `CMakeLists.txt` 里登记

`ros2 pkg create` 生成的 `CMakeLists.txt` 里有一些测试相关的内容，接口包用不到，可以整个替换成：

```cmake
cmake_minimum_required(VERSION 3.8)
project(fire_alert_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/PhotoInfo.msg"
)

ament_package()
```

| 代码 | 意思 |
|---|---|
| `project(fire_alert_interfaces)` | 包名。下面的 `${PROJECT_NAME}` 就是它 |
| `find_package(rosidl_default_generators REQUIRED)` | 找到"翻译工具" `rosidl` |
| `rosidl_generate_interfaces(...)` | **核心一行**：把列出来的 `.msg` 文件翻译成 Python 和 C++ 代码。以后加新消息，就在括号里加一行 |
| `ament_package()` | 固定结尾，告诉 ROS 2 "这个包配置完了" |

如果消息里嵌套了别的包的消息，比如用了 `std_msgs/Header`，要多两处：`find_package(std_msgs REQUIRED)`，以及在 `rosidl_generate_interfaces(...)` 括号里加 `DEPENDENCIES std_msgs`。

### 第 3 步：在 `package.xml` 里登记

在 `<buildtool_depend>ament_cmake</buildtool_depend>` 下面加 3 行：

```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

| 代码 | 意思 |
|---|---|
| `buildtool_depend rosidl_default_generators` | **编译时**要用到翻译工具 |
| `exec_depend rosidl_default_runtime` | **运行时**要用到消息的底层支持库 |
| `member_of_group rosidl_interface_packages` | 声明"我是一个接口包"，`colcon` 会照这个来安排编译 |

`CMakeLists.txt` 和 `package.xml` 分工不同：`CMakeLists.txt` 写**怎么编译**，`package.xml` 写**依赖谁**。两处都要写，少一处都会出错。

### 第 4 步：编译并检查

```bash
cd ~/fire_ws
colcon build --packages-select fire_alert_interfaces   # 只编译这一个包，更快
source install/setup.bash
ros2 interface show fire_alert_interfaces/msg/PhotoInfo
```

能打印出 `.msg` 里的 3 个字段，就说明成功了：

```
uint32 id          # 第几张，从 1 开始
string filename    # 文件名，比如 photo_3.jpg
float32 altitude   # 拍照时无人机的高度，单位：米
```

**编译时到底发生了什么？** `rosidl` 读入 `PhotoInfo.msg`，生成了好几份代码，放进 `install/` 里：

```
PhotoInfo.msg ──rosidl 翻译──┬──▶ Python 类  PhotoInfo  （rclpy 用）
                             ├──▶ C++ 结构体 PhotoInfo  （rclcpp 用）
                             └──▶ DDS 传输用的类型描述   （底层通信用）
```

就像同一张表格模板，印出了中文版、英文版，还有一份给快递公司看的版本。Python 节点和 C++ 节点各用各的，但传出去的数据格式完全一样，所以**Python 写的相机节点和 C++ 写的识别节点也能直接通信**。

### 第 5 步：节点改用 `PhotoInfo`

先在 `fire_alert` 的 `package.xml` 里加一行依赖，表示"我要用 `fire_alert_interfaces` 里的消息"：

```xml
<depend>fire_alert_interfaces</depend>
```

**相机节点**（`camera.py`）只改 4 处，用 `# 改` 标出：

```python
import rclpy
from rclpy.node import Node
from fire_alert_interfaces.msg import PhotoInfo                              # 改


class CameraNode(Node):
    def __init__(self):
        super().__init__("camera")
        self.publisher = self.create_publisher(PhotoInfo, "/camera/photo", 10)  # 改
        self.timer = self.create_timer(1.0, self.take_photo)
        self.count = 0

    def take_photo(self):
        self.count += 1
        msg = PhotoInfo()                                                     # 改
        msg.id = self.count                                                   # 改：分别填 3 个字段
        msg.filename = f"photo_{self.count}.jpg"
        msg.altitude = 50.0                                                   # 假装无人机悬停在 50 米
        self.publisher.publish(msg)
        self.get_logger().info(f"拍了第 {msg.id} 张：{msg.filename}")
```

**识别节点**（`detector.py`）只改 3 处：

```python
import rclpy
from rclpy.node import Node
from fire_alert_interfaces.msg import PhotoInfo                     # 改


class DetectorNode(Node):
    def __init__(self):
        super().__init__("detector")
        self.subscription = self.create_subscription(
            PhotoInfo, "/camera/photo", self.on_photo, 10            # 改
        )

    def on_photo(self, msg):
        self.get_logger().info(                                     # 改：直接按名字取字段
            f"收到第 {msg.id} 张 {msg.filename}，高度 {msg.altitude:.1f} 米，开始识别烟火..."
        )
```

`main` 函数一行都不用改。

| 位置 | 改之前 | 改之后 |
|---|---|---|
| 导入 | `from std_msgs.msg import String` | `from fire_alert_interfaces.msg import PhotoInfo` |
| 创建发布者/订阅者 | 类型写 `String` | 类型写 `PhotoInfo` |
| 填内容 | `msg.data = "..."` | `msg.id`、`msg.filename`、`msg.altitude` 分别填 |
| 取内容 | `msg.data` | `msg.altitude` 等，按名字直接取 |

**导入路径的规律**：`from 包名.msg import 消息名`。`.msg` 文件叫 `PhotoInfo.msg`，类名就是 `PhotoInfo`。

**注意：两个节点要一起改。** 话题名还是 `/camera/photo`，但类型从 `String` 变成了 `PhotoInfo`。如果只改了一边，两边类型不一致，就会出现 Part 2 说的"收不到也不报错"。

### 第 6 步：一起编译、运行

```bash
cd ~/fire_ws
colcon build              # 两个包一起编译
source install/setup.bash
```

不用操心先编译哪个：`fire_alert` 的 `package.xml` 里写了依赖 `fire_alert_interfaces`，`colcon` 会**自动先编译接口包**。

和 Part 4 一样开两个终端运行，识别节点这边会看到：

```
[INFO] [...] [detector]: 收到第 2 张 photo_2.jpg，高度 50.0 米，开始识别烟火...
[INFO] [...] [detector]: 收到第 3 张 photo_3.jpg，高度 50.0 米，开始识别烟火...
```

再开一个终端（同样要 `source`）偷看话题，每个字段都带着名字：

```bash
$ ros2 topic echo /camera/photo
id: 7
filename: photo_7.jpg
altitude: 50.0
---
```

### 源代码怎么管理

**1. 消息和节点分两个包放**

```
~/fire_ws/
├── .gitignore                    ← 写上 build/ install/ log/
└── src/
    ├── fire_alert_interfaces/    ← ament_cmake：只放消息
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   └── msg/
    │       └── PhotoInfo.msg
    └── fire_alert/               ← ament_python：只放节点
        ├── package.xml           ← <depend>fire_alert_interfaces</depend>
        ├── setup.py
        └── fire_alert/
            ├── camera.py
            ├── detector.py
            └── alarm.py
```

分开的好处：

- **别人只想要你的消息**：比如地面站程序想订阅 `/camera/photo`，只装 `fire_alert_interfaces` 就够了，不用连带装上 YOLO26 和一大堆识别依赖。
- **构建方式不同**：消息只能用 CMake，节点用 Python 写更方便。分开后各管各的，不用把 Python 节点也塞进 CMake 包。
- **命名习惯**：接口包统一叫 `xxx_interfaces`，一看就知道里面只有消息。官方自带的 `std_msgs`、`sensor_msgs` 也是这样单独成包的。

从 Lyrical 开始，也可以在**一个 `ament_cmake` 包里**同时放消息和 Python 节点，但官方发布说明仍然推荐把消息单独放一个包。

**2. Git 只管 `src/`**

`build/`、`install/`、`log/` 都是编译自动生成的，随时可以删掉重来，**不要提交到 Git**。在工作空间根目录建一个 `.gitignore`：

```
build/
install/
log/
```

换一台电脑时，把代码拉下来，`colcon build` 一下就全回来了。

**3. 改了什么，要重新做什么**

| 改了什么 | 要做什么 |
|---|---|
| `.msg` 文件（加字段、改类型） | 重新 `colcon build`，**再 `source` 一次**，两个节点都要重启 |
| 只改了 Python 节点代码 | 重新 `colcon build` 再运行。如果编译时加了 `--symlink-install`，改完直接重新运行就行，不用再编译 |
| 新加了一个 `.msg` 文件 | 先在 `CMakeLists.txt` 的 `rosidl_generate_interfaces(...)` 里加上它，再重新编译 |

`--symlink-install` 的意思是：`install/` 里不复制一份 Python 文件，而是放一个指向 `src/` 里源文件的快捷方式。改了 `src/` 里的代码，`install/` 里马上就是新的。**写 Python 节点时推荐一直带着它**：`colcon build --symlink-install`。

### 新手常见报错

| 报错 | 原因 | 怎么办 |
|---|---|---|
| `ModuleNotFoundError: No module named 'fire_alert_interfaces'` | 当前终端没 `source`，或者接口包还没编译 | `colcon build` 后 `source install/setup.bash` |
| `ros2 topic echo` 报 `The message type 'fire_alert_interfaces/msg/PhotoInfo' is invalid` | 运行 `echo` 的那个终端没 `source` | 在那个终端也 `source` 一次 |
| `AttributeError: 'PhotoInfo' object has no attribute 'altitude'` | 改了 `.msg` 但没重新编译，Python 用的还是旧版本 | 重新 `colcon build` 并 `source` |
| 编译报 `.msg` 文件名或字段名不合法 | 文件名不是大驼峰，或字段名用了大写 | 改成 `PhotoInfo.msg`、`altitude` |
| `AssertionError`（赋值那一行） | 字段类型不对，比如给 `uint32` 赋了字符串 `"3"` | 按 `.msg` 里的类型赋值 |

### 练习：把 Part 2 的烟火警报也做成消息

识别节点发现烟火后要发给报警节点。照 Part 2 的设计，在同一个接口包里再加一个 `msg/FireAlert.msg`：

```
string label         # fire 或 smoke
float32 confidence   # YOLO26 的置信度，比如 0.92
int32 x              # 框左上角 x
int32 y              # 框左上角 y
int32 w              # 框宽
int32 h              # 框高
```

然后在 `CMakeLists.txt` 里加一行 `"msg/FireAlert.msg"`，重新编译。识别节点在 `on_photo` 里发布到 `/fire_alert`，报警节点订阅它，整条野火报警链路就连起来了。

## Part 6：服务

> **一句话理解：服务（Service）就是"打电话"：一个节点问一句（请求，Request），另一个节点办完事回一句（响应，Response）。**

Part 2 里的话题像广播，发完就不管谁听没听。但有些事情需要**等对方回话**，比如识别节点想让相机"用高分辨率拍一张，拍完告诉我存在哪"，这时就要用服务。

### 服务和话题的区别

| | 话题（Topic） | 服务（Service） |
|---|---|---|
| 比喻 | 广播电台：一直在播，想听就开收音机 | 打电话：问一句，答一句 |
| 方向 | 单向，发完就走 | 双向，有请求就有响应 |
| 什么时候发 | 持续不断，比如每秒 30 张照片 | 需要时才问一次 |
| 角色 | 发布者 / 订阅者 | **服务端（Server）** / **客户端（Client）** |
| 数量 | 多个发布者、多个订阅者都行 | **只能有一个服务端**，客户端可以有很多个 |
| 野火报警里 | 相机持续发布 `/camera/photo` | 识别节点请求 `/camera/take_photo`：拍一张高清照片 |

**怎么选**：数据**一直在更新**（画面、位置、速度），用话题；**偶尔做一件事，并且要知道结果**（拍一张、切换模式、复位传感器），用服务。

一次服务调用的过程：

```
识别节点（客户端）                         相机节点（服务端）
      │ ──请求：拍一张高清照片──▶                 │
      │                                    拍照、保存……
      │ ◀──响应：成功，photo_hd_1.jpg──            │
```

服务端平时什么都不做，**有人请求了才执行一次**。就像客服热线：没人打进来，客服就等着；一来电，就处理这一个问题，然后挂断。

### `.srv`：服务的格式

话题用 `.msg` 规定消息格式，服务用 `.srv`。区别是 `.srv` 用 `---` 分成两半：**上面是请求，下面是响应**。

ROS 2 自带一个最简单的服务类型 `std_srvs/srv/Trigger`（触发），不用自己定义就能用：

```
                 # 请求：什么都不用带，就是"喂，干活"
---
bool success     # 响应：成没成功
string message   # 响应：附带一句话，这里用来放文件名
```

如果请求里要带参数，比如指定分辨率，就自定义一个 `TakePhoto.srv`：

```
string resolution   # 请求：比如 "1920x1080"
---
bool success        # 响应：拍成功了没有
string filename     # 响应：照片存在哪
```

做法和 Part 5 的 `.msg` 完全一样：放进 `fire_alert_interfaces/srv/` 文件夹，在 `CMakeLists.txt` 的 `rosidl_generate_interfaces(...)` 里加一行 `"srv/TakePhoto.srv"`，重新编译。Python 里用 `from fire_alert_interfaces.srv import TakePhoto` 导入。

### 写一个拍照服务端（camera_service.py）

下面直接用自带的 `Trigger`，不用编译接口包：

```python
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class CameraServiceNode(Node):
    def __init__(self):
        super().__init__("camera_service")
        self.srv = self.create_service(Trigger, "/camera/take_photo", self.on_take_photo)
        self.count = 0

    def on_take_photo(self, request, response):
        self.count += 1
        response.success = True
        response.message = f"photo_hd_{self.count}.jpg"
        self.get_logger().info(f"收到拍照请求，已保存 {response.message}")
        return response


def main(args=None):
    rclpy.init(args=args)
    node = CameraServiceNode()
    rclpy.spin(node)
    rclpy.shutdown()
```

和 Part 4 的相机节点相比，只有这几行是新的：

| 代码 | 意思 |
|---|---|
| `from std_srvs.srv import Trigger` | 导入服务类型。注意是 `.srv`，不是 `.msg` |
| `self.create_service(Trigger, "/camera/take_photo", self.on_take_photo)` | 创建服务端，三个参数：**服务类型**、**服务名**、**收到请求后交给谁处理** |
| `def on_take_photo(self, request, response):` | 服务的回调函数。ROS 2 会传进来两样东西：客户端发来的 `request`，和一张空白的 `response` |
| `response.success = True` / `response.message = ...` | 把结果填进响应 |
| `return response` | **必须 `return`**，响应才会发回给客户端。忘了写，客户端就收不到回答 |

`main` 还是 Part 4 讲过的四步，一点没变。和订阅回调一样，`on_take_photo` 也是由 `spin` 来调用的。

运行前还要两步登记：在 `setup.py` 的 `console_scripts` 里加一行 `'camera_service = fire_alert.camera_service:main'`，在 `package.xml` 里加 `<depend>std_srvs</depend>`。

### 用命令行当客户端

编译、`source` 之后，在一个终端启动服务端：

```bash
ros2 run fire_alert camera_service
```

另一个终端（同样要 `source`）用 `ros2 service call` 临时当一回客户端，"打个电话"：

```bash
$ ros2 service call /camera/take_photo std_srvs/srv/Trigger
requester: making request: std_srvs.srv.Trigger_Request()

response:
std_srvs.srv.Trigger_Response(success=True, message='photo_hd_1.jpg')
```

服务端那边同时打印：

```
[INFO] [...] [camera_service]: 收到拍照请求，已保存 photo_hd_1.jpg
```

每调用一次，`photo_hd_` 后面的数字就加 1。

常用的服务命令：

| 命令 | 用途 |
|---|---|
| `ros2 service list` | 看现在有哪些服务 |
| `ros2 service type /camera/take_photo` | 看服务类型，这里输出 `std_srvs/srv/Trigger` |
| `ros2 service call 服务名 类型 "请求内容"` | 发一次请求。`Trigger` 的请求是空的，所以省略了最后的 `"请求内容"` |
| `ros2 interface show std_srvs/srv/Trigger` | 看请求和响应各有哪些字段 |

### 在代码里当客户端

识别节点想在代码里请求拍照，核心就 3 行：

```python
self.client = self.create_client(Trigger, "/camera/take_photo")    # 在 __init__ 里创建客户端
future = self.client.call_async(Trigger.Request())                  # 发请求，不等待，马上返回
future.add_done_callback(lambda f: self.get_logger().info(f"照片在 {f.result().message}"))  # 回答到了再处理
```

`call_async` 里的 async 是"异步"的意思：请求发出去后**不傻等**，节点继续干别的。等响应回来了，`spin` 再去调用 `add_done_callback` 登记的函数。就像打电话给客服说"查好了回电给我"，挂了电话继续干活。

**一个常见的坑**：服务端没启动时，请求发出去不会有人回答。实际代码里一般先用 `self.client.wait_for_service(timeout_sec=1.0)` 确认服务端在线，再发请求。

### 顺带一提：动作（Action）

如果要做的事**很久才能做完**，而且中途想看进度，比如"飞到 500 米外的火点上空"，服务就不太合适：客户端只能干等最后的结果，不知道进行到哪了，也没法中途喊停。这时用第三种通信方式：**动作（Action）**。它可以随时报告进度（"还剩 200 米"），中途也能取消。

| 通信方式 | 一句话 | 例子 |
|---|---|---|
| 话题 | 一直广播 | 相机持续发画面 |
| 服务 | 问一句，答一句 | 拍一张高清照片 |
| 动作 | 交代一个长任务，过程中不断汇报，可以中途取消 | 飞到火点上空 |

### 野火报警里什么时候用服务

判断标准就一句话：**偶尔做一次的事，并且发起方需要知道结果，就用服务；一直在流动的数据，用话题。**

| 场景 | 客户端 → 服务端 | 请求 | 响应 | 为什么用服务 |
|---|---|---|---|---|
| ① 拍高清照片取证 | 识别节点 → 相机节点 | 拍一张原图分辨率的照片 | 成功了没有、文件名 | YOLO26 平时只看缩小的 640×640 画面，发现火以后才要一张高清原图给飞手确认。偶尔一次，而且要知道存在哪 |
| ② 暂停或恢复识别 | 地面站 → 识别节点 | `true` 开始 / `false` 暂停 | 设置成功了没有 | 起飞、降落、返航时不用找火，暂停识别能省机载电脑的算力和电。用自带的 `std_srvs/srv/SetBool` 就行 |
| ③ 飞手确认警报 | 地面站 → 报警节点 | "这是误报"或"已确认，在处理" | 收到 | 报警节点会一直重复提醒，飞手点一下"已确认"它才停。必须确定报警节点收到了，所以要等回答 |
| ④ 像素坐标换算成经纬度 | 识别节点 → 定位节点 | 框在画面里的位置，比如 `(120, 80)` | 火点的经纬度 | 一次纯计算：给输入，要输出。定位节点手里有无人机当前的位置、高度和云台角度，能算出火在地面上的哪里 |
| ⑤ 查询状态 | 地面站 → 识别节点 | "汇报一下" | 当前模型名、每秒处理几帧 | 飞手想看一眼时才问，不需要一直广播 |

把这几个服务加进 Part 2 的链路，大概是这样（实线是话题，虚线是服务）：

```
[相机节点] ──/camera/photo──▶ [识别节点] ──/fire_alert──▶ [报警节点] ──▶ 地面站
     ▲                         ┊      ┊                        ▲
     └┈┈┈ ① 拍高清照片 ┈┈┈┈┈┈┈┈┘      └┈┈ ④ 像素→经纬度 ┈┈▶ [定位节点]
                                ▲                              ┊
地面站 ┈┈┈ ② 暂停/恢复识别 ┈┈┈┈┈┘     地面站 ┈┈ ③ 确认警报 ┈┈┈┈┘
```

**容易用错的地方："发现火"的警报本身要用话题，不要用服务。** 看起来像是"识别节点通知报警节点"，好像可以用服务，其实不合适：

- **想听的不止一个**：报警节点、录像节点（发现火就开始存视频）、地面站都想知道。话题可以有多个订阅者，服务一次只能问一个服务端。
- **识别节点不应该等**：用服务的话，识别节点得等报警节点回答完才能接着看下一张照片，这期间可能漏掉新的火点。
- **怕丢就设 QoS**：Part 2 讲过，把 `/fire_alert` 设成 Reliable 就能保证送到，不需要靠服务的"回答"来确认。

同样，"飞到火点上空"要花一分钟左右，中途还要看进度、可能要取消，应该用上一节的动作，而不是服务。

**一张表总结：**

| 需求 | 用什么 |
|---|---|
| 相机画面、无人机位置、电量 | 话题（一直在更新） |
| 发现火的警报 | 话题 + Reliable（多个节点要听，识别节点不能等） |
| 拍高清照片、暂停识别、确认警报、坐标换算、查状态 | **服务**（偶尔一次，要知道结果） |
| 飞到火点、绕火场飞一圈拍全景 | 动作（时间长，要看进度，能取消） |
| 改配置，比如把置信度阈值调成 `0.6` | **参数（Parameter）**：用 `ros2 param set` 就能改，不用自己写服务。它底层其实也是服务，ROS 2 已经帮你写好了 |

## Part 7：launch

> **一句话理解：launch 就是"一键启动"：把要启动哪些节点、各自用什么参数写进一个 launch 文件，一条命令全部启动，按一次 Ctrl+C 全部关掉。**

### 为什么需要 launch

Part 4 里跑两个节点，要开两个终端，每个都先 `source` 再 `ros2 run`：

```bash
# 终端 1
ros2 run fire_alert camera
# 终端 2
ros2 run fire_alert detector
```

两个还好。真到了无人机上，还有报警节点、相机驱动、定位节点、录像节点、和 PX4 通信的节点……十几个节点一个个手动启动，很容易漏，而且每次上电都要重来一遍。

**打个比方**：`ros2 run` 像一个个按开关开灯；launch 文件像智能家居里的"回家模式"，按一下，灯、空调、窗帘一起打开。

### 一个最简单的 launch 文件

在 `fire_alert` 包里新建 `launch/fire_alert.launch.py`：

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package="fire_alert", executable="camera"),
        Node(package="fire_alert", executable="detector", respawn=True),
    ])
```

逐行讲解：

| 代码 | 意思 |
|---|---|
| `from launch import LaunchDescription` | 导入"启动清单" |
| `from launch_ros.actions import Node` | 导入"启动一个 ROS 2 节点"这个动作。注意这个 `Node` 和写节点时用的 `rclpy.node.Node` **不是一个东西**，名字一样而已 |
| `def generate_launch_description():` | 函数名是**固定的**，`ros2 launch` 会来找这个函数 |
| `LaunchDescription([...])` | 启动清单，列表里每一项是一个要启动的东西 |
| `Node(package="fire_alert", executable="camera")` | 启动一个节点，相当于 `ros2 run fire_alert camera`。`executable` 就是 `setup.py` 里 `console_scripts` 登记的名字 |
| `respawn=True` | 这个节点要是崩了，**自动重新启动**。Part 2 说过"识别节点崩了，重启它就能接着用"，这一项就是让它自动重启 |

以后写好了报警节点，在列表里再加一行 `Node(package="fire_alert", executable="alarm")` 就行。

### 登记到 `setup.py`

launch 文件和节点代码不一样，**不会自动被装进 `install/`**，要在 `setup.py` 的 `data_files` 里加一行：

```python
import os
from glob import glob

# 在 setup() 的 data_files 列表里加：
(os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
```

意思是：把 `launch/` 文件夹里所有 `.launch.py` 文件，复制到 `install/fire_alert/share/fire_alert/launch/`，`ros2 launch` 就去那里找。

**漏了这一步，`ros2 launch` 会报找不到这个文件**，这是新手最常踩的坑。另外在 `package.xml` 里加一行 `<exec_depend>ros2launch</exec_depend>`，声明运行时要用到 launch。

现在的包结构：

```
fire_alert/
├── launch/
│   └── fire_alert.launch.py   ← 新加的
├── package.xml
├── setup.py                   ← 登记 launch 文件
└── fire_alert/
    ├── camera.py
    └── detector.py
```

### 跑起来看看

重新编译、`source` 后，一条命令启动两个节点：

```bash
ros2 launch fire_alert fire_alert.launch.py
```

格式是 `ros2 launch 包名 launch文件名`，和 `ros2 run 包名 节点名` 一样，先找部门再找人。

两个节点的日志都打印在**同一个终端**里，最前面多了一个进程名前缀，比如 `[camera-1]`、`[detector-2]`，看前缀就知道是谁说的：

```
[camera-1] [INFO] [...] [camera]: 拍了一张：photo_1.jpg
[detector-2] [INFO] [...] [detector]: 收到 photo_1.jpg，开始识别烟火...
[camera-1] [INFO] [...] [camera]: 拍了一张：photo_2.jpg
[detector-2] [INFO] [...] [detector]: 收到 photo_2.jpg，开始识别烟火...
```

按一次 Ctrl+C，两个节点一起关掉。

### launch 还能做什么

除了"一起启动"，launch 文件还能顺手配置每个节点，**不用改节点代码**：

| 功能 | 写法 | 野火报警里的例子 |
|---|---|---|
| 传参数 | `parameters=[{"confidence": 0.6}]` | 识别节点的置信度阈值（节点里要先用 `declare_parameter` 声明这个参数） |
| 改话题名（重映射，Remapping） | `remappings=[("/camera/photo", "/camera_front/photo")]` | 识别节点代码里写死了听 `/camera/photo`，不改代码就让它改听前置相机的 `/camera_front/photo`。注意只能换话题名，**消息类型还是得一致** |
| 改节点名 | `name="detector_front"` | 同一个识别程序跑两份，一份叫 `detector_front` 看前置相机，一份叫 `detector_down` 看下视相机。名字不改的话，两个节点都叫 `detector`，会撞名 |
| 包含别人的 launch 文件 | `IncludeLaunchDescription(...)` | `usb_cam` 包自带 launch 文件，直接引进来，不用自己写相机配置 |
| 自动重启 | `respawn=True` | 识别节点崩了自动拉起来 |

比如无人机上有前置、下视两个相机，同一个识别程序跑两份，各看一个：

```python
Node(
    package="fire_alert",
    executable="detector",
    name="detector_front",                                  # 改节点名，避免撞名
    remappings=[("/camera/photo", "/camera_front/photo")],  # 改听前置相机
    respawn=True,
),
Node(
    package="fire_alert",
    executable="detector",
    name="detector_down",
    remappings=[("/camera/photo", "/camera_down/photo")],   # 改听下视相机
    respawn=True,
),
```

`detector.py` 一行没改，靠 launch 文件就变成了两个各干各的节点。

### `ros2 run` 和 `ros2 launch` 怎么选

| | `ros2 run` | `ros2 launch` |
|---|---|---|
| 一次启动几个节点 | 1 个 | 想启动几个就几个 |
| 参数 | 每次在命令行里手动敲 | 写在文件里，每次都一样 |
| 关闭 | 每个终端各按一次 Ctrl+C | 按一次 Ctrl+C 全部关掉 |
| 适合 | 调试单个节点 | 整套系统一起跑，比如无人机上电后的正式运行 |

launch 文件除了 Python，也可以用 XML 或 YAML 写，但 ROS 2 里最常见的是 Python 版，文件名习惯以 `.launch.py` 结尾。
