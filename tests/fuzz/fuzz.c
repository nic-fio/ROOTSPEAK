/* RootSpeak - Advanced Messaging System for Linux
 * Fuzzing (libFuzzer) of what reads untrusted data: the first byte picks
 * the target, the rest is the data.
 *   0 text cleaning                (text and title of messages)
 *   1 message format               (copies in the mailboxes, read by rootspeak-user)
 *   2 mailbox reading output       (confirmations and postponements written by the user, read by root)
 *   3 configuration */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "store.h"
#include "common.h"
#include "text.h"

int LLVMFuzzerTestOneInput(const uint8_t *data_bytes, size_t n);

int LLVMFuzzerTestOneInput(const uint8_t *data_bytes, size_t n)
{
	const char *s;
	char *z;

	if (n < 1)
		return 0;
	s = (const char *)data_bytes + 1;
	n--;
	z = malloc(n + 1);
	memcpy(z, s, n);
	z[n] = '\0';
	switch (data_bytes[0] % 4) {
	case 0: {
		buf_t b = {0};

		clean_text(s, n, &b);
		buf_free(&b);
		break;
	}
	case 1: {
		msg_t m;
		buf_t b = {0};

		if (msg_from_text(s, n, &m) == 0) {
			msg_format(&m, &b);
			msg_header(&m, &b);
			msg_free(&m);
		}
		buf_free(&b);
		break;
	}
	case 2: {
		mailbox_t c;

		mailbox_from_text(s, n, &c);
		mailbox_item(&c, 1);
		mailbox_free(&c);
		break;
	}
	default: {
		conf_t c;

		conf_from_text(z, &c);
		break;
	}
	}
	free(z);
	return 0;
}
