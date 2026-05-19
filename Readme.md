cmake作业
项目关系
CMake_Test/
├── CMakeLists.txt              # 顶层构建文件
├── main.cpp                    # 主程序入口
├── common/
│   ├── CMakeLists.txt          # 公共库扫描入口
│   ├── kalman/                 # header‑only 卡尔曼滤波模块
│   │   ├── CMakeLists.txt
│   │   └── include/...
│   └── math/                   # 数学库（依赖 OpenCV）
│       ├── CMakeLists.txt
│       ├── include/Math.h
│       └── src/Math.cpp
└── modules/
    ├── A1/                     # 模块 A1
    │   ├── CMakeLists.txt
    │   ├── include/...
    │   └── src/...
    ├── A2/                     # 模块 A2
    │   ├── CMakeLists.txt
    │   ├── include/A2.h
    │   └── src/A2.cpp
    ├── M1/                     # 模块 M1（依赖 A1）
    │   ├── CMakeLists.txt
    │   └── ...
    └── M2/                     # 模块 M2（依赖 A1, A2, kalman）
        ├── CMakeLists.txt
        └── ...
        test (main.cpp)
而依赖关系为
├── M1 ────── A1
├── M2 ────── A1 + A2 + kalman (INTERFACE → OpenCV)
└── math ─── OpenCV
#以上关系为AI生成

我做了什么
新建了顶层，A1，A2，M2,math
更改了common,kalman

AI做了什么
检查并理解项目要求，帮我看代码并检查
工具：deepseek,claude code

思考
我认为当下的人机协作确实如学姐所说十分高效，但同时我们也要自己掌握知识，AI是重要的辅助工具，但我们要学好
很多什么库怎么改其实我不了解也没听过，但AI是方便的搜索工具，快速指出重点，十分重要

学习链接
https://www.bilibili.com/video/BV1Tw411s7Pk?vd_source=c546b443c7eefff54f35d464bccc08d1
https://www.runoob.com/cmake/cmake-tutorial.html
https://cmake.org/cmake/help/latest/guide/tutorial/index.html
