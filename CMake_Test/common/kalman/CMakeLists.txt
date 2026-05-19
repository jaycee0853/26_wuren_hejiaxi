find_package(OpenCV REQUIRED)

add_library(kalman INTERFACE)
target_include_directories(kalman INTERFACE include)
target_link_libraries(kalman INTERFACE ${OpenCV_LIBS})
target_include_directories(kalman INTERFACE ${OpenCV_INCLUDE_DIRS})
