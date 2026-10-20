#include <stdint.h>
#include <string.h>
#include <wmmintrin.h>
#include <emmintrin.h>
#include <smmintrin.h>
static inline void a1(__m128i *t1, __m128i *t2) {
    __m128i t4; *t2 = _mm_shuffle_epi32(*t2, 0xff);
    t4 = _mm_slli_si128(*t1, 4); *t1 = _mm_xor_si128(*t1, t4);
    t4 = _mm_slli_si128(t4, 4); *t1 = _mm_xor_si128(*t1, t4);
    t4 = _mm_slli_si128(t4, 4); *t1 = _mm_xor_si128(*t1, t4);
    *t1 = _mm_xor_si128(*t1, *t2);
}
static inline void a2(__m128i *t1, __m128i *t3) {
    __m128i t2, t4 = _mm_aeskeygenassist_si128(*t1, 0x0);
    t2 = _mm_shuffle_epi32(t4, 0xaa);
    t4 = _mm_slli_si128(*t3, 4); *t3 = _mm_xor_si128(*t3, t4);
    t4 = _mm_slli_si128(t4, 4); *t3 = _mm_xor_si128(*t3, t4);
    t4 = _mm_slli_si128(t4, 4); *t3 = _mm_xor_si128(*t3, t4);
    *t3 = _mm_xor_si128(*t3, t2);
}
#define R(rc) t2 = _mm_aeskeygenassist_si128(t3, rc); a1(&t1, &t2); k[i++] = t1; a2(&t1, &t3); k[i++] = t3;
static inline void expand(const uint8_t *key, __m128i *k) {
    __m128i t1 = _mm_loadu_si128((const __m128i *)key), t3 = _mm_loadu_si128((const __m128i *)(key + 16)), t2;
    int i = 0; k[i++] = t1; k[i++] = t3;
    R(0x01) R(0x02) R(0x04) R(0x08) R(0x10) R(0x20)
    t2 = _mm_aeskeygenassist_si128(t3, 0x40); a1(&t1, &t2); k[i++] = t1;
}
static inline int aes_test(const uint8_t *key, __m128i ct, __m128i iv, uint8_t *out) {
    __m128i k[15]; expand(key, k);
    __m128i x = _mm_xor_si128(ct, k[14]);
    for (int r = 13; r >= 1; r--) x = _mm_aesdec_si128(x, _mm_aesimc_si128(k[r]));
    x = _mm_aesdeclast_si128(x, k[0]);
    x = _mm_xor_si128(x, iv);
    uint8_t p[16]; _mm_storeu_si128((__m128i *)p, x);
    for (int j = 8; j < 16; j++) if (p[j] != 8) return 0;
    memcpy(out, p, 8); return 1;
}

static inline void dec_round_keys(const uint8_t *key, __m128i *d) {
    __m128i k[15]; expand(key, k);
    d[0] = k[14]; for (int r = 1; r <= 13; r++) d[r] = _mm_aesimc_si128(k[14 - r]); d[14] = k[0];
}
static inline int pad_ok(const __m128i *d, __m128i ct, __m128i iv, uint8_t *out) {
    __m128i x = _mm_xor_si128(ct, d[0]);
    for (int r = 1; r <= 13; r++) x = _mm_aesdec_si128(x, d[r]);
    x = _mm_aesdeclast_si128(x, d[14]); x = _mm_xor_si128(x, iv);
    uint8_t p[16]; _mm_storeu_si128((__m128i *)p, x);
    for (int j = 8; j < 16; j++) if (p[j] != 8) return 0;
    memcpy(out, p, 8); return 1;
}
