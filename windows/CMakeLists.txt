cmake_minimum_required(VERSION 3.15)
project(jpegenc_test C)

set(CMAKE_C_STANDARD 99)

include_directories(${CMAKE_SOURCE_DIR}/../src)

add_executable(test_bmp2jpg test.c ${CMAKE_SOURCE_DIR}/../src/JPEGENC.c)
