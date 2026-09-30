/* AMS - Advanced Messaging System for linux
 * Prove delle parti interne della versione in C.
 *   prove-unita                    tutte le prove
 *   prove-unita pulisci            pulisce stdin su stdout (confronto con il prototipo)
 *   prove-unita lingua L A M G     lingua scelta da LANGUAGE, LC_ALL, LC_MESSAGES, LANG
 *   prove-unita conf               valori letti dalla configurazione (AMS_CONF, con AMS_TEST=1)
 *   prove-unita mo FILE            legge un .mo qualunque (per il fuzzing): non deve mai fallire male */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "comune.h"
#include "evento.h"
#include "lingua.h"
#include "testo.h"

static int prove, falliti;

static void controlla(const char *cosa, bool ok)
{
	prove++;
	if (!ok) {
		falliti++;
		printf("  NO   %s\n", cosa);
	}
}

static bool pulito_uguale(const char *in, size_t n, const char *atteso)
{
	buf_t b = {0};
	bool ok;

	pulisci(in, n, &b);
	ok = strlen(atteso) == b.n && !memcmp(b.s ? b.s : "", atteso, b.n);
	if (!ok)
		printf("       pulisci: atteso «%s», ottenuto «%s»\n", atteso, b.s ? b.s : "");
	buf_free(&b);
	return ok;
}

static void prove_pulizia(void)
{
	controlla("CSI tolta", pulito_uguale("a\033[31mrosso\033[0m b", 18, "arosso b"));
	controlla("OSC tolta", pulito_uguale("x\033]0;titolo\007y", 13, "xy"));
	controlla("OSC senza BEL: resta il testo, sparisce ESC", pulito_uguale("x\033]0;t\ny", 8, "x]0;t\ny"));
	controlla("C0 tolti tranne tab e a capo", pulito_uguale("a\001\tb\n\rc\177", 8, "a\tb\nc"));
	controlla("C1 in UTF-8 tolti", pulito_uguale("a\xc2\x85" "b\xc2\xa0", 6, "ab\xc2\xa0"));
	controlla("UTF-8 normale intatto", pulito_uguale("perché è così", 16, "perché è così"));
}

static bool lingua_uguale(const char *l, const char *a, const char *m, const char *g, const char *atteso)
{
	char out[LINGUA_MAX];

	lingua_scegli(l, a, m, g, out);
	if (strcmp(out, atteso))
		printf("       lingua: attesa %s, ottenuta %s\n", atteso, out);
	return !strcmp(out, atteso);
}

static void prove_lingua(void)
{
	controlla("LANG=it_IT.UTF-8: italiano", lingua_uguale("", "", "", "it_IT.UTF-8", "it"));
	controlla("LANG=en_GB.UTF-8: inglese", lingua_uguale("", "", "", "en_GB.UTF-8", "en"));
	controlla("lingua senza traduzione: inglese", lingua_uguale("", "", "", "de_DE.UTF-8", "en"));
	controlla("LANG=C o assente: inglese", lingua_uguale("", "", "", "C.UTF-8", "en") && lingua_uguale(NULL, NULL, NULL, NULL, "en"));
	controlla("LC_ALL=C vince su LANG=it", lingua_uguale("", "C", "", "it_IT.UTF-8", "en"));
	controlla("LC_MESSAGES=it vince su LANG=en", lingua_uguale("", "", "it_IT.UTF-8", "en_US.UTF-8", "it"));
	controlla("LANGUAGE=de:it con LANG=en: italiano", lingua_uguale("de:it", "", "", "en_US.UTF-8", "it"));
	controlla("LANGUAGE ignorata con LANG=C", lingua_uguale("it", "", "", "C", "en"));
	controlla("valori strani: inglese", lingua_uguale("../../tmp/x", "", "", "a/b", "en"));
	{
		const char env[] = "PATH=/bin\0LANG=it_IT.UTF-8\0";
		char out[LINGUA_MAX];

		controlla("lingua dall'ambiente di un processo",
			  lingua_da_environ(env, sizeof env - 1, out) && !strcmp(out, "it"));
		controlla("ambiente vuoto: nessuna lingua", !lingua_da_environ("", 0, out));
	}
	controlla("traduzione italiana trovata", !strcmp(tl("it", "desktop"), "desktop") &&
		  !strcmp(tl("it", "Message %lld revoked."), "Messaggio %lld ritirato."));
	controlla("inglese: il testo di partenza", !strcmp(tl("en", "Message %lld revoked."), "Message %lld revoked."));
}

static void prove_messaggio(void)
{
	const char t[] = "format: 1\nid: 12\nfrom: root\ndate: 1700000000\ntitle: Prova\nexpires: 1700000100\n\nriga 1\n\nriga 3\n";
	msg_t m;
	buf_t b = {0};

	controlla("messaggio letto", msg_da_testo(t, sizeof t - 1, &m) == 0 && m.id == 12 && !strcmp(m.from, "root") &&
					     m.date == 1700000000 && !strcmp(m.title, "Prova") && m.expires == 1700000100 &&
					     !strcmp(m.body, "riga 1\n\nriga 3\n"));
	msg_formatta(&m, &b);
	controlla("messaggio riscritto uguale", b.n == sizeof t - 1 && !memcmp(b.s, t, b.n));
	controlla("scaduto dopo la scadenza", msg_scaduto(&m, 1700000100) && !msg_scaduto(&m, 1700000099));
	msg_libera(&m);
	buf_free(&b);
	controlla("senza data: rifiutato", msg_da_testo("id: 1\n\ntesto", 13, &m) < 0);
}

static void prove_conf(void)
{
	conf_t c;

	conf_da_testo("AMS_REMIND_MINUTES=45 # minuti\n  AMS_AGENT_POLL = 20  \n", &c);
	controlla("configurazione: commenti e spazi", c.remind_minutes == 45 && c.agent_poll == 20);
	conf_da_testo("AMS_REMIND_MINUTES=$(rm -rf /)\nAMS_AGENT_POLL=0\nALTRO=5\n", &c);
	controlla("configurazione: valori non validi ignorati", c.remind_minutes == 30 && c.agent_poll == 60);
	conf_da_testo("AMS_REMIND_MINUTES=1234567\nAMS_AGENT_POLL=-5\n", &c);
	controlla("configurazione: troppe cifre e negativi ignorati", c.remind_minutes == 30 && c.agent_poll == 60);
}

static void prove_eventi(void)
{
	buf_t b = {0};

	evento_testo("en", "CONFERMATO", 3, "mario", "terminale pts/2", "", "", &b);
	controlla("evento in inglese", !strcmp(b.s, "user mario: confirmed reading message 3 (terminal pts/2)"));
	buf_clear(&b);
	evento_testo("it", "CONFERMATO", 3, "mario", "terminale pts/2", "", "", &b);
	controlla("evento in italiano", !strcmp(b.s, "utente mario: confermata la lettura del messaggio 3 (terminale pts/2)"));
	buf_clear(&b);
	controlla("evento sconosciuto", !evento_testo("en", "BOH", 1, "", "", "", "", &b));
	buf_free(&b);
}

int main(int argc, char **argv)
{
	ams_init("prove-unita");
	if (argc > 1 && !strcmp(argv[1], "pulisci")) {
		buf_t in = {0}, out = {0};

		leggi_fd(0, (size_t)1 << 26, &in);
		pulisci(in.s ? in.s : "", in.n, &out);
		scrivi_tutto(1, out.s ? out.s : "", out.n);
		return 0;
	}
	if (argc == 6 && !strcmp(argv[1], "lingua")) {
		char out[LINGUA_MAX];

		lingua_scegli(argv[2], argv[3], argv[4], argv[5], out);
		puts(out);
		return 0;
	}
	if (argc == 2 && !strcmp(argv[1], "conf")) {
		conf_t c;

		conf_leggi(&c);
		printf("%ld %ld\n", c.remind_minutes, c.agent_poll);
		return 0;
	}
	if (argc == 3 && !strcmp(argv[1], "mo")) {
		buf_t in = {0};
		catalogo_t *c;

		if (leggi_file(argv[2], 1 << 24, false, &in) < 0)
			return 0;
		c = catalogo_da_memoria(in.s, in.n);
		catalogo_cerca(c, "desktop");
		catalogo_cerca(c, "zzz");
		catalogo_cerca(c, "");
		catalogo_libera(c);
		return 0;
	}
	prove_pulizia();
	prove_lingua();
	prove_messaggio();
	prove_conf();
	prove_eventi();
	if (falliti) {
		printf("FALLITE: %d su %d\n", falliti, prove);
		return 1;
	}
	printf("OK: %d prove\n", prove);
	return 0;
}
