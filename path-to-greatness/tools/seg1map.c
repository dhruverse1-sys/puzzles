// Segment 1 sweep: imagine from a small list (16 chars each); beach = 15 notes, token per note identity,
// identities: I0=A#5 I1=F#5 I2=B5 I3=6th(D#5/E5) I4=F5 I5=C#5 I6=B4 I7=A#4; one of {I3,I4,I6,I7} takes a 2-char token.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <wmmintrin.h>
#include <emmintrin.h>
#include <smmintrin.h>
#include <omp.h>
#include "aes.h"
static const int NOTE_ID[15] = {0,1,2,0,1,3,4,5,6,5,7,0,1,2,0};
int main(int argc, char **argv) {
    // argv[1]=ct hex, argv[2]=iv16, argv[3]=imagine list file, optional argv[4]=witness mode
    uint8_t ctb[16], ivb[16];
    for (int i = 0; i < 16; i++) sscanf(argv[1] + 2 * i, "%2hhx", &ctb[i]);
    memcpy(ivb, argv[2], 16);
    __m128i ct = _mm_loadu_si128((__m128i *)ctb), iv = _mm_loadu_si128((__m128i *)ivb);
    uint8_t wb[16]; for (int i = 0; i < 16; i++) sscanf(argv[4] + 2 * i, "%2hhx", &wb[i]);
    __m128i wct = _mm_loadu_si128((__m128i *)wb);
    char im[64][17]; int nim = 0; char buf[128]; FILE *f = fopen(argv[3], "r");
    while (fgets(buf, sizeof buf, f)) { size_t l = strcspn(buf, "\r\n"); buf[l] = 0; if (l == 16) strcpy(im[nim++], buf); }
    fclose(f);
    // two-char tokens
    char T2[200][3]; int nt2 = 0;
    for (int a = 0; a < 10; a++) for (int b = 0; b < 10; b++) { T2[nt2][0] = '0' + a; T2[nt2][1] = '0' + b; T2[nt2][2] = 0; nt2++; }
    const char *acc = "#b";
    for (int d = 0; d < 10; d++) for (int k = 0; k < 2; k++) {
        T2[nt2][0] = '0' + d; T2[nt2][1] = acc[k]; T2[nt2][2] = 0; nt2++;
        T2[nt2][0] = acc[k]; T2[nt2][1] = '0' + d; T2[nt2][2] = 0; nt2++;
    }
    const int SPECIAL[4] = {3, 4, 6, 7};
    fprintf(stderr, "imagine %d, T2 %d, total per imagine %.3g\n", nim, nt2, 4.0 * 1e7 * nt2);
    long hits = 0;
    for (int ii = 0; ii < nim; ii++) {
        for (int sp = 0; sp < 4; sp++) {
            int S = SPECIAL[sp];
            int others[7], no = 0; for (int i = 0; i < 8; i++) if (i != S) others[no++] = i;
            #pragma omp parallel for schedule(dynamic, 1) reduction(+:hits)
            for (long m = 0; m < 10000000L; m++) {
                char tok1[8]; long x = m;
                for (int j = 0; j < 7; j++) { tok1[others[j]] = '0' + (x % 10); x /= 10; }
                uint8_t key[40]; memcpy(key, im[ii], 16);
                for (int t = 0; t < nt2; t++) {
                    int p = 16;
                    for (int n = 0; n < 15; n++) {
                        int id = NOTE_ID[n];
                        if (id == S) { key[p++] = T2[t][0]; key[p++] = T2[t][1]; }
                        else key[p++] = tok1[id];
                    }
                    uint8_t out[8]; __m128i d[15]; dec_round_keys(key, d);
                    if (pad_ok(d, wct, iv, out)) {
                        #pragma omp critical
                        { printf("WITNESS imagine=%.16s beach=%.16s\n", (char *)key, (char *)key + 16); fflush(stdout); }
                    }
                    if (pad_ok(d, ct, iv, out)) {
                        #pragma omp critical
                        { printf("HIT imagine=%.16s beach=%.16s seg=", (char *)key, (char *)key + 16); for (int j = 0; j < 8; j++) printf("%02x", out[j]); printf("\n"); fflush(stdout); }
                        hits++;
                    }
                }
            }
            fprintf(stderr, "imagine %s special I%d done, hits so far %ld\n", im[ii], S, hits);
        }
    }
    fprintf(stderr, "ALL DONE hits=%ld\n", hits);
    return 0;
}
