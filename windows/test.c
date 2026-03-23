#define PROGMEM
#include "../src/JPEGENC.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

static JPEGE_IMAGE jpeg;

static uint8_t *ReadBMP(const char *fname, int *width, int *height, int *bpp)
{
    int y, w, h, bits, offset;
    uint8_t *s, *d, *pTemp, *pBitmap;
    int pitch, bytewidth;
    int iSize, iDelta;
    FILE *infile;

    infile = fopen(fname, "rb");
    if (infile == NULL) {
        printf("Error opening input file %s\n", fname);
        return NULL;
    }
    fseek(infile, 0, SEEK_END);
    iSize = (int)ftell(infile);
    fseek(infile, 0, SEEK_SET);
    pBitmap = (uint8_t *)malloc(iSize);
    pTemp = (uint8_t *)malloc(iSize);
    fread(pTemp, 1, iSize, infile);
    fclose(infile);

    if (pTemp[0] != 'B' || pTemp[1] != 'M' || pTemp[14] < 0x28) {
        free(pBitmap);
        free(pTemp);
        printf("Not a Windows BMP file!\n");
        return NULL;
    }
    w = *(int32_t *)&pTemp[18];
    h = *(int32_t *)&pTemp[22];
    bits = *(int16_t *)&pTemp[26] * *(int16_t *)&pTemp[28];
    if (bits <= 8) {
        free(pBitmap);
        free(pTemp);
        printf("Only 24/32-bpp BMP supported!\n");
        return NULL;
    }
    offset = *(int32_t *)&pTemp[10];
    bytewidth = (w * bits) >> 3;
    pitch = (bytewidth + 3) & 0xfffc;
    d = pBitmap;
    s = &pTemp[offset];
    iDelta = pitch;
    if (h > 0) {
        iDelta = -pitch;
        s = &pTemp[offset + (h-1) * pitch];
    } else {
        h = -h;
    }
    for (y = 0; y < h; y++) {
        if (bits == 32) {
            int i;
            for (i = 0; i < bytewidth; i += 4) {
                d[i] = s[i+2];
                d[i+1] = s[i+1];
                d[i+2] = s[i];
                d[i+3] = s[i+3];
            }
        } else {
            memcpy(d, s, bytewidth);
        }
        d += bytewidth;
        s += iDelta;
    }
    *width = w;
    *height = h;
    *bpp = bits;
    free(pTemp);
    return pBitmap;
}

void usage(const char *prog) {
    printf("Usage: %s <infile.bmp> <outfile.jpg> [pixel_type] [subsample]\n", prog);
    printf("  pixel_type: RGB888 (default), RGB565, ARGB8888\n");
    printf("  subsample: 420 (default), 444\n");
}

int main(int argc, const char * argv[])
{
    int rc, iWidth, iHeight, iBpp, iBytePP, iPitch, iDataSize, iBufSize;
    uint8_t *pBitmap, *pOutput;
    uint8_t ucPixelType = JPEGE_PIXEL_RGB888;
    uint8_t ucSubSample = JPEGE_SUBSAMPLE_420;
    JPEGENCODE jpe;
    FILE *outfile;

    if (argc < 3 || argc > 5) {
        usage(argv[0]);
        return 1;
    }

    if (argc >= 4) {
        if (strcmp(argv[3], "RGB565") == 0) {
            ucPixelType = JPEGE_PIXEL_RGB565;
        } else if (strcmp(argv[3], "ARGB8888") == 0) {
            ucPixelType = JPEGE_PIXEL_ARGB8888;
        } else if (strcmp(argv[3], "RGB888") != 0) {
            printf("Unknown pixel type: %s\n", argv[3]);
            usage(argv[0]);
            return 1;
        }
    }

    if (argc >= 5) {
        if (strcmp(argv[4], "444") == 0) {
            ucSubSample = JPEGE_SUBSAMPLE_444;
        } else if (strcmp(argv[4], "420") != 0) {
            printf("Unknown subsample: %s\n", argv[4]);
            usage(argv[0]);
            return 1;
        }
    }

    pBitmap = ReadBMP(argv[1], &iWidth, &iHeight, &iBpp);
    if (pBitmap == NULL) {
        fprintf(stderr, "Unable to read BMP file: %s\n", argv[1]);
        return 1;
    }

    if (ucPixelType == JPEGE_PIXEL_RGB565) {
        iBytePP = 2;
    } else if (ucPixelType == JPEGE_PIXEL_RGB888) {
        iBytePP = 3;
    } else {
        iBytePP = 4;
    }
    iPitch = iBytePP * iWidth;

    iBufSize = iWidth * iHeight * 3;
    pOutput = (uint8_t *)malloc(iBufSize);
    if (pOutput == NULL) {
        printf("Failed to allocate output buffer\n");
        free(pBitmap);
        return 1;
    }

    rc = JPEGOpenRAM(&jpeg, pOutput, iBufSize);
    if (rc != JPEGE_SUCCESS) {
        printf("Failed to open encoder, error: %d\n", rc);
        free(pBitmap);
        free(pOutput);
        return 1;
    }

    rc = JPEGEncodeBegin(&jpeg, &jpe, iWidth, iHeight, ucPixelType, ucSubSample, JPEGE_Q_BEST);
    if (rc != JPEGE_SUCCESS) {
        printf("Failed to begin encoding, error: %d\n", rc);
        free(pBitmap);
        free(pOutput);
        return 1;
    }

    rc = JPEGAddFrame(&jpeg, &jpe, pBitmap, iPitch);
    if (rc != JPEGE_SUCCESS) {
        printf("Failed to add frame, error: %d\n", rc);
        free(pBitmap);
        free(pOutput);
        return 1;
    }

    iDataSize = JPEGEncodeEnd(&jpeg);
    printf("Output JPEG size = %d bytes (pixel=%s, subsample=%s)\n", 
           iDataSize, argv[3] ? argv[3] : "RGB888", argv[4] ? argv[4] : "420");

    outfile = fopen(argv[2], "wb");
    if (outfile == NULL) {
        printf("Failed to open output file: %s\n", argv[2]);
        free(pBitmap);
        free(pOutput);
        return 1;
    }
    fwrite(pOutput, 1, iDataSize, outfile);
    fclose(outfile);

    free(pBitmap);
    free(pOutput);
    return 0;
}
