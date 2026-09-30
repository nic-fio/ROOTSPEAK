/* AMS - Advanced Messaging System for linux
 * Fuzzing (libFuzzer) di ciò che legge dati non fidati: il primo byte sceglie
 * il bersaglio, il resto è il dato.
 *   0 pulizia del testo            (testo e titolo dei messaggi)
 *   1 formato dei messaggi         (copie nelle caselle, lette da ams-user)
 *   2 uscita della lettura caselle (conferme e rinvii scritti dall'utente, letti da root)
 *   3 ambiente di un processo      (/proc/PID/environ di un utente, letto da root)
 *   4 configurazione
 *   5 catalogo .mo */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "archivio.h"
#include "comune.h"
#include "lingua.h"
#include "testo.h"

int LLVMFuzzerTestOneInput(const uint8_t *dati, size_t n);

int LLVMFuzzerTestOneInput(const uint8_t *dati, size_t n)
{
	const char *s;
	char *z;

	if (n < 1)
		return 0;
	s = (const char *)dati + 1;
	n--;
	z = malloc(n + 1);
	memcpy(z, s, n);
	z[n] = '\0';
	switch (dati[0] % 6) {
	case 0: {
		buf_t b = {0};

		pulisci(s, n, &b);
		buf_free(&b);
		break;
	}
	case 1: {
		msg_t m;
		buf_t b = {0};

		if (msg_da_testo(s, n, &m) == 0) {
			msg_formatta(&m, &b);
			msg_intestazione(&m, &b);
			msg_libera(&m);
		}
		buf_free(&b);
		break;
	}
	case 2: {
		casella_t c;

		casella_da_testo(s, n, &c);
		casella_voce(&c, 1);
		casella_libera(&c);
		break;
	}
	case 3: {
		char out[LINGUA_MAX];

		lingua_da_environ(s, n, out);
		break;
	}
	case 4: {
		conf_t c;

		conf_da_testo(z, &c);
		break;
	}
	default: {
		catalogo_t *c = catalogo_da_memoria(s, n);

		catalogo_cerca(c, "desktop");
		catalogo_cerca(c, z);
		catalogo_libera(c);
		break;
	}
	}
	free(z);
	return 0;
}
