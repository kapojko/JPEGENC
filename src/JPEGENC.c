// SPDX-FileCopyrightText: 2021 Larry Bank <bitbank@pobox.com>
// SPDX-License-Identifier: Apache-2.0
//
// JPEG Encoder C wrapper
//
#include "JPEGENC.h"
#include <string.h>

#ifndef PROGMEM
#define PROGMEM
#endif

#ifdef _MSC_VER
#define __builtin_bswap64 _byteswap_uint64
#endif

int JPEGOpenRAM(JPEGE_IMAGE *pJPEG, uint8_t *pData, int iDataSize)
{
    if (!pJPEG || !pData || iDataSize < 1024) return JPEGE_INVALID_PARAMETER;
    memset(pJPEG, 0, sizeof(JPEGE_IMAGE));
    pJPEG->pOutput = pData;
    pJPEG->iBufferSize = iDataSize;
    pJPEG->pHighWater = &pData[iDataSize - 512];
    return JPEGE_SUCCESS;
}

int JPEGOpenCallback(JPEGE_IMAGE *pJPEG, JPEGE_WRITE_CALLBACK *pfnWrite)
{
    if (!pJPEG || !pfnWrite) return JPEGE_INVALID_PARAMETER;
    memset(pJPEG, 0, sizeof(JPEGE_IMAGE));
    pJPEG->pfnWrite = pfnWrite;
    pJPEG->pHighWater = &pJPEG->ucFileBuf[JPEGE_FILE_BUF_SIZE - 512];
    return JPEGE_SUCCESS;
}

int JPEGGetLastError(JPEGE_IMAGE *pJPEG)
{
    if (!pJPEG) return JPEGE_INVALID_PARAMETER;
    return pJPEG->iError;
}

#ifdef USE_CMSIS_DSP

#include "arm_math.h"

#ifdef _WIN32
#define JPEGENC_ALIGN(x) __declspec(align(x))
#else
#define JPEGENC_ALIGN(x) __attribute__((aligned(x)))
#endif

static const q15_t JPEGENC_COEFF_Y[3]  = { 1225,  2404,   467};
static const q15_t JPEGENC_COEFF_CB[3] = { -691, -1357,  2048};
static const q15_t JPEGENC_COEFF_CR[3] = { 2048, -1715,  -333};

static inline void jpegenc_cmsis_rgb2ycbcr(uint8_t r, uint8_t g, uint8_t b,
                                           int16_t *y, int16_t *cb, int16_t *cr)
{
    JPEGENC_ALIGN(4) q15_t rgb[3];
    q63_t acc;

    rgb[0] = (q15_t)r;
    rgb[1] = (q15_t)g;
    rgb[2] = (q15_t)b;

    arm_dot_prod_q15(rgb, JPEGENC_COEFF_Y, 3, &acc);
    *y = (int16_t)((acc >> 12) - 128);

    arm_dot_prod_q15(rgb, JPEGENC_COEFF_CB, 3, &acc);
    *cb = (int16_t)(acc >> 12);

    arm_dot_prod_q15(rgb, JPEGENC_COEFF_CR, 3, &acc);
    *cr = (int16_t)(acc >> 12);
}

static inline int16_t jpegenc_cmsis_chroma_avg4(int16_t v0, int16_t v1, int16_t v2, int16_t v3)
{
    JPEGENC_ALIGN(4) q15_t vals[4];
    q15_t mean;

    vals[0] = v0;
    vals[1] = v1;
    vals[2] = v2;
    vals[3] = v3;

    arm_mean_q15(vals, 4, &mean);
    return mean;
}

#endif /* USE_CMSIS_DSP */

#include "jpegenc.inl"
