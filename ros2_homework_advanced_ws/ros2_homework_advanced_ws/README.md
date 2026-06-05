# 进阶作业 - 锥桶地图可视化

这个作业是让锥桶在RViz里显示出来，一开始我连bag是什么都不太清楚，搞了半天。

## 文件结构

```
ros2_homework_advanced_ws/
  src/
    fsd_common_msgs/              # 车队自定义消息包
      msg/                        # Map.msg, Cone.msg等
      CMakeLists.txt
      package.xml
    ros2_homework_advanced_package/
      bag/
        map_to_visualize/         # bag数据
      launch/
        visualize_map.launch.py   # 一键启动
      result/                     # 截图和视频放这里
      src/
        map_visualizer.cpp        # 锥桶可视化节点
      CMakeLists.txt
      package.xml
  README.md
```

## 怎么跑起来

```bash
cd ros2_homework_advanced_ws
colcon build
source install/setup.bash
ros2 launch ros2_homework_advanced_package visualize_map.launch.py
```

launch文件里同时启动了可视化节点、RViz、还有bag循环回放。RViz打开后需要手动配一下，这个卡了我很久。

不想用launch的话：
```bash
# 终端1：回放bag
ros2 bag play src/ros2_homework_advanced_package/bag/map_to_visualize --loop

# 终端2：可视化节点
ros2 run ros2_homework_advanced_package map_visualizer

# 终端3：RViz
rviz2
```

## RViz配置（这一步最容易卡）

1. 启动后RViz默认Fixed Frame是"map"，但bag里的frame_id不一定是"map"。先用这个查一下：
   ```bash
   ros2 topic echo /estimation/slam/map --once
   ```
   看header.frame_id那一行。
2. 在RViz左上角Fixed Frame那里改成你查到的名字。
3. 点左下角Add → By topic → 找到 `/cone_markers` → 双击添加。
4. 就能看到红蓝黄灰四种颜色的锥桶了。

我一开始Fixed Frame设错了，Marker怎么都出不来，查了一下消息header才搞明白，PPT里也提示要"思考坐标系问题"。

## 思路和代码

整体就是：bag回放发Map消息 → 我的节点订阅 → 转Marker发布 → RViz显示。

bag回放会往`/estimation/slam/map`发消息，Map里有四种锥桶数组（黄/蓝/红/未知），每个Cone有position(x,y,z)和color。我的节点订阅到消息后，把每种锥桶转成Marker，颜色对应好，用MarkerArray一次发出去，RViz就能显示了。

Marker我选的CYLINDER（圆柱体），上课讲过Marker有球、立方、箭头、文本等好多种类型，圆柱体看着最像锥桶。frame_id优先用消息header里的，没有才用参数默认值。为什么要用MarkerArray？上课讲过一次发多个Marker用MarkerArray比循环单个发更高效，老师PPT里也提了这点。

学的东西顺便记一下：
- ros2 bag：录制时是订阅节点，回放时是发布节点。bag是个文件夹里面有.db3和metadata.yaml。常用命令就是play回放，info看信息，--loop循环。这作业直接给了bag所以不用录
- 自定义消息：fsd_common_msgs是车队自己定义的消息，不是ROS2自带的。Map.msg里有四种锥桶数组，Cone.msg里有位置颜色置信度。要用得先编译这个包，它会自动生成C++头文件
- Marker：frame_id坐标系，ns+id唯一标识，type形状（CUBE/SPHERE/CYLINDER/ARROW等），pose位置，scale大小，color颜色。alpha必须>0否则不可见
- 坐标系问题：RViz有Fixed Frame概念，所有东西都要在这个坐标系下。frame_id对不上就显示不出来

## 踩的坑

- Marker不显示。最大的坑。Fixed Frame默认是"map"，但bag里的frame_id可能是别的（比如"world"），Marker发布出去RViz也找不到。

- Marker一直叠加。我一开始把lifetime设成0（永久显示），结果地图消息一直在更新，旧的Marker不消失新的又来了，RViz里全是重叠的圆。改成0.5秒过期就好了，因为新消息不断来，旧Marker自动消失就不会叠加。

- bag路径。想让launch文件里能`ros2 bag play`，得用`FindPackageShare`定位bag文件夹的绝对路径，bag还得放在功能包目录下并在CMakeLists.txt里install。

- source。和基础作业一样，新终端一定要source，不然找不到包。

- AI使用。我用AI查了Marker字段含义、MarkerArray用法、bag play参数这些，代码和思路都是自己想的，遵守PPT第46页的规则。
