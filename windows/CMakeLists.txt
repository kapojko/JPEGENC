cmake_minimum_required(VERSION 3.15)
project(jpegenc_test C)

set(CMAKE_C_STANDARD 99)

include_directories(${CMAKE_SOURCE_DIR}/../src)

add_executable(test_bmp2jpg test.c ${CMAKE_SOURCE_DIR}/../src/JPEGENC.c)

if(DEFINED ENV{CMSIS_DSP_PATH})
    set(CMSIS_DSP_PATH $ENV{CMSIS_DSP_PATH})
    if(MSVC)
        link_directories(${CMSIS_DSP_PATH}/build/Source/Release)
        target_link_libraries(test_bmp2jpg CMSISDSP.lib)
    elseif(MINGW)
        link_directories(${CMSIS_DSP_PATH}/build/Source/GCC)
        target_link_libraries(test_bmp2jpg CMSISDSP)
    endif()
    add_definitions(-DUSE_CMSIS_DSP)
    include_directories(${CMSIS_DSP_PATH}/Include)
endif()
