cmake_minimum_required(VERSION 3.18)
project(cuda_tprod LANGUAGES CXX CUDA)

# Set CUDA architectures first
set(CMAKE_CUDA_ARCHITECTURES 80)

# Set language standards
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CUDA_STANDARD 20)

# CUDA flags
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} --std=c++20 -extended-lambda --expt-relaxed-constexpr -w -lineinfo --ftemplate-backtrace-limit=0 -Xcompiler -ftemplate-backtrace-limit=0")

# Find CUDA
find_package(CUDA REQUIRED)

# Set CUTLASS include path
set(CUTLASS_INCLUDE_DIR ${CMAKE_SOURCE_DIR}/cutlass/include/cutlass)
if(NOT EXISTS ${CUTLASS_INCLUDE_DIR})
    message(FATAL_ERROR "CUTLASS include directory not found at ${CUTLASS_INCLUDE_DIR}")
endif()

# Download and build Google Test
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

# Header-only library target
add_library(cuda_tprod_lib INTERFACE)
target_include_directories(cuda_tprod_lib INTERFACE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/vidrial
    ${CMAKE_SOURCE_DIR}/vidrial/cuda_utils
    ${CMAKE_SOURCE_DIR}/vidrial/kernels
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/copy
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/mma
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/sympow
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/sympow_mma
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/reduce
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/sympow_bwd
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/add_one
    ${CMAKE_SOURCE_DIR}/vidrial/kernels/flash
    ${CMAKE_SOURCE_DIR}/cutlass/include
)

# Enable testing
enable_testing()

# Individual test executables - updated paths
set(TEST_SOURCES
    vidrial/cuda_utils/tests/utils_test.cu
    vidrial/cuda_utils/tests/ldsm_test.cu
    vidrial/cuda_utils/tests/tprod_test.cu
    vidrial/cuda_utils/tests/frgthr_tiling_test.cu
    vidrial/cuda_utils/tests/copy_test.cu
    vidrial/cuda_utils/tests/swizzle_test.cu
    vidrial/kernels/copy/copy_cfg_test.cu
    vidrial/kernels/add_one/test.cu
    vidrial/kernels/mma/mma_cfg_test.cu
    vidrial/kernels/sympow/sympow_cfg_test.cu
    vidrial/kernels/sympow/test.cu
    vidrial/kernels/sympow_mma/test.cu
    vidrial/kernels/sympow_bwd/test.cu
    vidrial/kernels/reduce/test.cu
    vidrial/kernels/flash/test.cu
)

# Create individual test targets
foreach(TEST_SOURCE ${TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_SOURCE} NAME_WE)
    get_filename_component(TEST_DIR ${TEST_SOURCE} DIRECTORY)
    get_filename_component(TEST_DIR_NAME ${TEST_DIR} NAME)
    set(TARGET_NAME "${TEST_DIR_NAME}_${TEST_NAME}")
    add_executable(${TARGET_NAME} ${TEST_SOURCE})
    target_link_libraries(${TARGET_NAME} PRIVATE
        cuda_tprod_lib
        GTest::gtest_main
        GTest::gmock_main
        ${CUDA_LIBRARIES}
    )
    add_test(NAME ${TARGET_NAME} COMMAND ${TARGET_NAME})
endforeach()

# Combined test executable
add_executable(tests ${TEST_SOURCES})
target_link_libraries(tests PRIVATE
    cuda_tprod_lib
    GTest::gtest_main
    GTest::gmock_main
    ${CUDA_LIBRARIES}
)
add_test(NAME tests COMMAND tests)
