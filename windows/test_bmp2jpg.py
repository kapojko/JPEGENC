import subprocess
import struct
import os
import sys


def create_test_bmp(filename, width=256, height=256, bpp=24):
    """Create a test BMP image with a color gradient."""
    if bpp == 24:
        bytes_per_pixel = 3
    elif bpp == 32:
        bytes_per_pixel = 4
    elif bpp == 16:
        bytes_per_pixel = 2
    else:
        raise ValueError(f"Unsupported BPP: {bpp}")

    if bpp == 16:
        mask_size = 12
        row_size = width * bytes_per_pixel
        pixel_data_size = row_size * height
        file_size = 54 + mask_size + pixel_data_size

        with open(filename, "wb") as f:
            f.write(b"BM")
            f.write(struct.pack("<I", file_size))
            f.write(struct.pack("<H", 0))
            f.write(struct.pack("<H", 0))
            f.write(struct.pack("<I", 54 + mask_size))

            f.write(struct.pack("<I", 40))
            f.write(struct.pack("<i", width))
            f.write(struct.pack("<i", height))
            f.write(struct.pack("<H", 1))
            f.write(struct.pack("<H", 16))
            f.write(struct.pack("<I", 3))
            f.write(struct.pack("<I", pixel_data_size))
            f.write(struct.pack("<i", 0))
            f.write(struct.pack("<i", 0))
            f.write(struct.pack("<I", 0))
            f.write(struct.pack("<I", 0))

            f.write(struct.pack("<I", 0xF800))
            f.write(struct.pack("<I", 0x07E0))
            f.write(struct.pack("<I", 0x001F))

            for y in range(height):
                for x in range(width):
                    r = int((x / width) * 255)
                    g = int((y / height) * 255)
                    b = 128

                    r5 = r >> 3
                    g6 = g >> 2
                    b5 = b >> 3
                    pixel = (r5 << 11) | (g6 << 5) | b5
                    f.write(struct.pack("<H", pixel))
    else:
        row_size = ((width * bytes_per_pixel + 3) // 4) * 4
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
            f.write(struct.pack("<H", bpp))
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

                    if bpp == 24:
                        f.write(bytes([b, g, r]))
                    elif bpp == 32:
                        f.write(bytes([b, g, r, 255]))

                if row_size > width * bytes_per_pixel:
                    f.write(b"\x00" * (row_size - width * bytes_per_pixel))


def validate_jpeg(filename):
    """Validate that the JPEG file can be loaded."""
    try:
        from PIL import Image

        with Image.open(filename) as img:
            img.verify()
        with Image.open(filename) as img:
            img.load()
        print(f"  JPEG validated: {img.size[0]}x{img.size[1]}")
        return True, Image.open(filename)
    except ImportError:
        print("  PIL not available, skipping validation")
        return True, None
    except Exception as e:
        print(f"  JPEG validation failed: {e}")
        return False, None


def compare_images(bmp_path, jpg_path, threshold=30):
    """Compare input BMP with output JPEG to detect encoding errors."""
    try:
        from PIL import Image
        import numpy as np

        bmp = Image.open(bmp_path)
        jpg = Image.open(jpg_path)

        if bmp.size != jpg.size:
            jpg = jpg.resize(bmp.size, Image.LANCZOS)

        bmp_arr = np.array(bmp.convert("RGB"), dtype=np.float32)
        jpg_arr = np.array(jpg.convert("RGB"), dtype=np.float32)

        mse = np.mean((bmp_arr - jpg_arr) ** 2)
        rmse = np.sqrt(mse)

        print(f"  Image comparison: RMSE={rmse:.2f} (threshold={threshold})")

        if rmse > threshold:
            print(f"  WARNING: RMSE exceeds threshold - possible encoding issue")
            return False
        return True

    except ImportError:
        print("  PIL/numpy not available, skipping image comparison")
        return True
    except Exception as e:
        print(f"  Image comparison failed: {e}")
        return False
        return True

    except ImportError:
        print("  PIL/numpy not available, skipping image comparison")
        return True
    except Exception as e:
        print(f"  Image comparison failed: {e}")
        return False
        return True

    except ImportError:
        print("  PIL/numpy not available, skipping image comparison")
        return True
    except Exception as e:
        print(f"  Image comparison failed: {e}")
        return False


def run_test(
    exe_path, test_name, bmp_path, jpg_path, pixel_type="RGB888", subsample="420"
):
    """Run a single encoding test."""
    print(f"\nTest: {test_name}")
    print(f"  Input:  {bmp_path}")
    print(f"  Output: {jpg_path}")
    print(f"  Args:   pixel={pixel_type}, subsample={subsample}")

    try:
        result = subprocess.run(
            [exe_path, bmp_path, jpg_path, pixel_type, subsample],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"  {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  Conversion failed: {e}")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        return False

    if not os.path.exists(jpg_path):
        print(f"  JPEG file was not created")
        return False

    valid, _ = validate_jpeg(jpg_path)
    if not valid:
        return False

    if not compare_images(bmp_path, jpg_path):
        return False

    return True


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(script_dir, "test")
    exe_path = os.path.join(script_dir, "build", "Release", "test_bmp2jpg.exe")

    if not os.path.exists(exe_path):
        print(f"Executable not found: {exe_path}")
        print("Please build the project first")
        sys.exit(1)

    os.makedirs(test_dir, exist_ok=True)

    tests = [
        {
            "name": "RGB888 + 4:2:0 (JPEGSubSample24)",
            "bmp": "test_rgb888_24bit.bmp",
            "pixel": "RGB888",
            "subsample": "420",
            "bpp": 24,
        },
        {
            "name": "RGB888 + 4:4:4 (JPEGSample24)",
            "bmp": "test_rgb888_24bit.bmp",
            "pixel": "RGB888",
            "subsample": "444",
            "bpp": 24,
        },
        {
            "name": "ARGB8888 + 4:2:0 (JPEGSubSample32)",
            "bmp": "test_argb8888_32bit.bmp",
            "pixel": "ARGB8888",
            "subsample": "420",
            "bpp": 32,
        },
        {
            "name": "ARGB8888 + 4:4:4 (JPEGSample32)",
            "bmp": "test_argb8888_32bit.bmp",
            "pixel": "ARGB8888",
            "subsample": "444",
            "bpp": 32,
        },
        {
            "name": "RGB565 + 4:2:0 (JPEGSubSample16)",
            "bmp": "test_rgb565_16bit.bmp",
            "pixel": "RGB565",
            "subsample": "420",
            "bpp": 16,
        },
        {
            "name": "RGB565 + 4:4:4 (JPEGSample16)",
            "bmp": "test_rgb565_16bit.bmp",
            "pixel": "RGB565",
            "subsample": "444",
            "bpp": 16,
        },
    ]

    created_files = set()
    passed = 0
    failed = 0

    for test in tests:
        bmp_path = os.path.join(test_dir, test["bmp"])
        jpg_path = os.path.join(
            test_dir,
            test["name"]
            .replace(" ", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace(":", "_")
            + ".jpg",
        )

        if test["bmp"] not in created_files:
            print(f"\nCreating {test['bpp']}-bit BMP: {bmp_path}")
            create_test_bmp(bmp_path, bpp=test["bpp"])
            created_files.add(test["bmp"])

        if run_test(
            exe_path, test["name"], bmp_path, jpg_path, test["pixel"], test["subsample"]
        ):
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Test images saved in: {test_dir}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
