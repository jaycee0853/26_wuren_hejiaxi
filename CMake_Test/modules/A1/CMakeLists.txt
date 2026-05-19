aux_source_directory(src A1_SRC)

add_library(A1 STATIC ${A1_SRC})

target_include_directories(A1 PUBLIC include)
