find_package(OpenCV REQUIRED)
aux_source_directory(src MATH_SRC)

add_library(math STATIC ${MATH_SRC})

target_include_directories(math PUBLIC include)
target_link_libraries(math PUBLIC ${OpenCV_LIBS})

target_include_directories(math PUBLIC ${OpenCV_INCLUDE_DIRS})
