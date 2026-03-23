# Windows BMP to JPEG Conversion Test

This directory contains a simple C test program that converts BMP images to JPEG using the JPEGENC library.

## Files

- `test.c` - C test program that converts a 24-bit or 32-bit BMP to JPEG
- `CMakeLists.txt` - CMake build configuration for MSVC
- `test_bmp2jpg.py` - Python script that generates test BMP, runs conversion, and validates JPEG
- `.gitignore` - Git ignore patterns for build artifacts and test outputs

## Building

### Prerequisites

- CMake 3.15 or later
- MSVC compiler (Visual Studio) or MinGW
- Python 3.x
- `uv` for Python dependency management

### Build with CMake

```bash
cd windows
mkdir build
cd build
cmake -G "NMake Makefiles" ..
cmake --build .
```

Or using MSVC generator:

```bash
cd windows
mkdir build
cd build
cmake -G "Visual Studio 17 2022" ..
cmake --build . --config Release
```

## CMSIS-DSP Integration

The library can use CMSIS-DSP for improved performance. When `CMSIS_DSP_PATH` is set, the build will include CMSIS-DSP headers and link against the CMSIS-DSP library.

### Building CMSIS-DSP (MSVC)

```bash
git clone https://github.com/ARM-software/CMSIS-DSP.git
cd CMSIS-DSP
mkdir build
cd build
cmake -G "Visual Studio 17 2022" .. -DHOST=ON
cmake --build . --config Release
```

This produces `CMSIS-DSP\build\Source\Release\CMSISDSP.lib`.

### Building CMSIS-DSP (MinGW)

```bash
git clone https://github.com/ARM-software/CMSIS-DSP.git
cd CMSIS-DSP
mkdir build
cd build
cmake -G "MinGW Makefiles" .. -DHOST=ON
cmake --build . --config Release
```

### Building with CMSIS-DSP

Set the environment variable before building:

```bash
# Windows (MSVC)
set CMSIS_DSP_PATH=D:\Github\CMSIS-DSP
cd windows
mkdir build
cd build
cmake -G "Visual Studio 17 2022" ..
cmake --build . --config Release
```

Or for MinGW:

```bash
# Windows (MinGW)
export CMSIS_DSP_PATH=/c/Github/CMSIS-DSP
cd windows
mkdir build
cd build
cmake -G "MinGW Makefiles" ..
cmake --build .
```

## Running

### Python setup with uv

Create virtual environment and install dependencies:

```bash
cd windows
uv venv
uv sync
```

### Using Python script (recommended)

The Python script handles everything: creating test BMP, running the C program, and validating the output:

```bash
cd windows
uv run python test_bmp2jpg.py
```

### Manual execution

```bash
cd windows/build
./test_bmp2jpg.exe ../test.bmp ../test.jpg
```

## How it works

1. The Python script generates a 256x256 24-bit BMP with a color gradient
2. The C program reads the BMP, allocates a buffer for JPEG output
3. Uses JPEGENC's memory-based API (`JPEGOpenRAM`, `JPEGEncodeBegin`, `JPEGAddFrame`, `JPEGEncodeEnd`)
4. Writes the resulting JPEG to disk
5. Python validates the JPEG can be loaded without errors

## Notes

- The test program only supports 24-bit and 32-bit BMP files
- Output format is always baseline JPEG with 4:2:0 subsampling and best quality
- The C code is pure C (not C++) to demonstrate the C API of JPEGENC
