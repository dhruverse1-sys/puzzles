// AES-256-CBC single-block padding oracle: key = left || right, plaintext must end in 8 x 0x08.
// usage: pairs <ct_hex32> <iv_ascii16> <left: file | enum8x2 | enum8> <right: file>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <wmmintrin.h>
#include <emmintrin.h>
#include <smmintrin.h>
#include <omp.h>

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
static inline int test(const uint8_t *key, __m128i ct, __m128i iv, uint8_t *out) {
    __m128i k[15]; expand(key, k);
    __m128i x = _mm_xor_si128(ct, k[14]);
    for (int r = 13; r >= 1; r--) x = _mm_aesdec_si128(x, _mm_aesimc_si128(k[r]));
    x = _mm_aesdeclast_si128(x, k[0]);
    x = _mm_xor_si128(x, iv);
    uint8_t p[16]; _mm_storeu_si128((__m128i *)p, x);
    for (int j = 8; j < 16; j++) if (p[j] != 8) return 0;
    memcpy(out, p, 8); return 1;
}
static char **readlines(const char *fn, int want, long *n) {
    FILE *f = fopen(fn, "r"); if (!f) { perror(fn); exit(2); }
    long cap = 1024, c = 0; char **v = malloc(cap * sizeof(char *)); char buf[256];
    while (fgets(buf, sizeof buf, f)) {
        size_t l = strcspn(buf, "\r\n"); buf[l] = 0;
        if ((int)l != want) continue;
        if (c == cap) { cap *= 2; v = realloc(v, cap * sizeof(char *)); }
        v[c] = malloc(l + 1); memcpy(v[c], buf, l + 1); c++;
    }
    fclose(f); *n = c; return v;
}
int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: pairs ct_hex iv16 leftlen left(file|enum8x2) rightlen rightfile\n"); return 2; }
    uint8_t ctb[16], ivb[16];
    for (int i = 0; i < 16; i++) sscanf(argv[1] + 2 * i, "%2hhx", &ctb[i]);
    memcpy(ivb, argv[2], 16);
    __m128i ct = _mm_loadu_si128((__m128i *)ctb), iv = _mm_loadu_si128((__m128i *)ivb);
    int LL = atoi(argv[3]), RL = atoi(argv[5]);
    long nr; char **rv = readlines(argv[6], RL, &nr);
    int enumx2 = !strcmp(argv[4], "enum8x2"); int enumwd = !strcmp(argv[4], "enumwd8");
    long nl; char **lv = NULL;
    if (enumx2) nl = 100000000L; else if (enumwd) nl = 1475789056L; else lv = readlines(argv[4], LL, &nl);
    fprintf(stderr, "left %ld x right %ld = %.3g pairs\n", nl, nr, (double)nl * nr);
    long hits = 0;
    #pragma omp parallel for schedule(dynamic, 4096) reduction(+:hits)
    for (long a = 0; a < nl; a++) {
        uint8_t key[32]; uint8_t out[8];
        if (enumx2) { char s[9]; snprintf(s, 9, "%08ld", a); memcpy(key, s, 8); memcpy(key + 8, s, 8); }
        else if (enumwd) { static const char A[] = "0123456789wasd"; long x = a; for (int j = 7; j >= 0; j--) { key[j] = A[x % 14]; x /= 14; } }
        else memcpy(key, lv[a], LL);
        for (long b = 0; b < nr; b++) {
            memcpy(key + LL, rv[b], RL);
            if (test(key, ct, iv, out)) {
                #pragma omp critical
                { printf("HIT left=%.*s right=%s seg=", LL, (char *)key, rv[b]); for (int j = 0; j < 8; j++) printf("%02x", out[j]); printf("\n"); fflush(stdout); }
                hits++;
            }
        }
    }
    fprintf(stderr, "done, hits=%ld\n", hits);
    return 0;
}
