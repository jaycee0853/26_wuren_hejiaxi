cmake_minimum_required(VERSION 3.8)
project(ros2_homework_advanced_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(fsd_common_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(visualization_msgs REQUIRED)

add_executable(map_visualizer src/map_visualizer.cpp)
target_compile_features(map_visualizer PUBLIC cxx_std_17)
ament_target_dependencies(map_visualizer rclcpp fsd_common_msgs visualization_msgs)

install(TARGETS map_visualizer
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
  launch
  bag
  DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()