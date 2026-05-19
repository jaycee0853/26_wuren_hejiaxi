aux_source_directory(src A2_SRC)

add_library(A2 STATIC ${A2_SRC})

target_include_directories(A2 PUBLIC include)
