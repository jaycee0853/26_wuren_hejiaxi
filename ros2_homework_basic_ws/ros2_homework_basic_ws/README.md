# 基础作业 - 乌龟八字形运动

这个作业让乌龟跑八字，一开始我以为很难，后来画了一下发现还行。

## 文件结构

```
ros2_homework_basic_ws/
  src/
    ros2_homework_basic_package/
      config/
        eight_params.yaml        # 参数配置
      launch/
        figure_eight.launch.py   # 一键启动
      result/                    # 截图和视频放这里
      src/
        figure_eight.cpp         # 八字形运动节点
      CMakeLists.txt
      package.xml
  README.md
```

## 怎么跑起来

环境是Ubuntu 22.04 + ROS2 humble，跟上课讲的环境一样。

```bash
cd ros2_homework_basic_ws
colcon build
source install/setup.bash
ros2 launch ros2_homework_basic_package figure_eight.launch.py
```

第一次编译完一定要source，不然`ros2 run`会找不到包，这个坑我踩了不止一次，每次新终端都要source。

不想用launch文件的话也可以手动启动：
```bash
# 终端1
ros2 run turtlesim turtlesim_node

# 终端2（记得source）
source install/setup.bash
ros2 run ros2_homework_basic_package figure_eight
```

速度可以在yaml里改，不用重编译，TA上课说过这个好处：
```yaml
# config/eight_params.yaml
figure_eight_node:
  ros__parameters:
    linear_velocity: 2.0
    angular_velocity: 1.0
```

## 思路和代码

我一开始看到"八字形"想得很复杂，后来画了一下发现其实就是一个圆加一个反方向的圆，两个圆在起点相切。PPT里也提示了这点。

怎么让乌龟画圆？同时给linear.x和angular.z就行，线速度前进，角速度转向，合起来就是圆周运动。怎么换方向？angular.z取反，正的逆时针，负的顺时针。

一个圆画完就回到起点了，这时候翻转方向，下一个圆就从同一个点开始，自然就相切了。周期 T = 2π/ω，算出来用定时器定时翻转。

代码里有两个定时器，一个每100ms发一次Twist消息，一个周期设为2π/ω秒到时间就翻转angular.z的符号。我一开始想用计数器数消息数量，但这样和发布频率耦合死了，后来想了想直接用定时器更清楚。

这里顺便记一下学到的东西：
- 话题通信就是发布方往话题上发消息，订阅方从话题上收，一个话题可以多个发布方多个订阅方。turtlesim默认听`/turtle1/cmd_vel`
- Twist消息有6个字段（linear.xyz + angular.xyz），2D的turtlesim只用linear.x和angular.z
- 参数服务器：`declare_parameter`声明，`get_parameter`拿，yaml配置改起来方便
- launch文件：`PathJoinSubstitution` + `FindPackageShare`定位yaml，启动命令`ros2 launch 包名 文件名`

## 踩的坑

- 忘了source。编译完直接`ros2 run`报错找不到包。每次新终端都要`source install/setup.bash`，老师说这个很常忘，真的是。

- 八字形怎么画。我一开始查资料看到路径规划算法什么的，太复杂了。后来回到原点：八字就是两个圆，画完一个翻转方向就行。PPT里其实也提示了"如何保证两个圆相切"这个问题。

- YAML缩进。第一次写yaml用Tab缩进，参数没加载上。改成空格才行。YAML对缩进超级敏感，节点名还得跟代码里的`Node("figure_eight_node")`保持一致。

- 方向翻转的时机。考虑过计数器方案（发多少条Twist之后翻转），但这样得算1秒内发多少条，麻烦。最后直接用第二个定时器，周期就是2π/ω，简单清楚。

- 调参数。我试了几组参数，linear=2.0, angular=1.0的时候圆不大不小比较合适。linear=1.0, angular=1.0圆小一点会贴到地图边缘，linear=3.0, angular=1.0圆太大超出turtlesim窗口。最后用2.0/1.0。

- AI使用。我用AI查了Twist消息各字段含义、定时器怎么写循环、yaml格式这些基础问题，思路和代码都是自己想的，遵守PPT第46页"可以用AI但不能直接写代码"的规则。
