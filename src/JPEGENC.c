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

int JPEGGetLastError(JPEGE_IMAGE *pJPEG)
{
    if (!pJPEG) return JPEGE_INVALID_PARAMETER;
    return pJPEG->iError;
}

#include "jpegenc.inl"
