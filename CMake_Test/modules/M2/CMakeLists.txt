aux_source_directory(src M2_SRC)

add_library(M2 STATIC ${M2_SRC})

target_include_directories(M2 PUBLIC include)
target_link_libraries(M2 PUBLIC A1 A2 kalman)
