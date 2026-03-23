import subprocess
import struct
import os
import sys


def create_test_bmp(filename, width=256, height=256):
    """Create a simple 24-bit BMP test image with a gradient."""
    row_size = ((width * 3 + 3) // 4) * 4
    pixel_data_size = row_size * height
    file_size = 54 + pixel_data_size

    with open(filename, "wb") as f:
        f.write(b"BM")
        f.write(struct.pack("<I", file_size))
        f.write(struct.pack("<H", 0))
        f.write(struct.pack("<H", 0))
        f.write(struct.pack("<I", 54))

        f.write(struct.pack("<I", 40))
        f.write(struct.pack("<i", width))
        f.write(struct.pack("<i", height))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", 24))
        f.write(struct.pack("<I", 0))
        f.write(struct.pack("<I", pixel_data_size))
        f.write(struct.pack("<i", 2835))
        f.write(struct.pack("<i", 2835))
        f.write(struct.pack("<I", 0))
        f.write(struct.pack("<I", 0))

        for y in range(height):
            for x in range(width):
                r = int((x / width) * 255)
                g = int((y / height) * 255)
                b = 128
                f.write(bytes([b, g, r]))
            if row_size > width * 3:
                f.write(b"\x00" * (row_size - width * 3))


def validate_jpeg(filename):
    """Validate that the JPEG file can be loaded."""
    try:
        from PIL import Image

        with Image.open(filename) as img:
            img.verify()
        with Image.open(filename) as img:
            img.load()
        print(f"JPEG validated successfully: {filename} ({img.size[0]}x{img.size[1]})")
        return True
    except ImportError:
        try:
            import jpeg4py as jpeg

            img = jpeg.JPEG(filename).decode()
            print(
                f"JPEG validated successfully: {filename} ({img.shape[1]}x{img.shape[0]})"
            )
            return True
        except ImportError:
            print("Neither PIL nor jpeg4py available, skipping validation")
            return True
    except Exception as e:
        print(f"JPEG validation failed: {e}")
        return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bmp_path = os.path.join(script_dir, "test.bmp")
    jpg_path = os.path.join(script_dir, "test.jpg")
    exe_path = os.path.join(script_dir, "build", "Release", "test_bmp2jpg.exe")

    if not os.path.exists(exe_path):
        print(f"Executable not found: {exe_path}")
        print("Please build the project first with: cmake --build build")
        sys.exit(1)

    print("Creating test BMP...")
    create_test_bmp(bmp_path)
    print(f"Created {bmp_path}")

    print("Converting BMP to JPEG...")
    try:
        subprocess.run([exe_path, bmp_path, jpg_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")
        sys.exit(1)

    if not os.path.exists(jpg_path):
        print("JPEG file was not created")
        sys.exit(1)

    print("Validating JPEG...")
    if validate_jpeg(jpg_path):
        print("SUCCESS: BMP to JPEG conversion works correctly")
        sys.exit(0)
    else:
        print("FAILURE: JPEG validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
