/* AMS - Advanced Messaging System for linux
 * ams-user: aiutante interno, non è un comando per l'utente. Gira con
 * l'identità dell'utente, lanciato dall'aggancio della shell (prompt) e
 * dall'avvio automatico del desktop (agent): mostra i messaggi e registra la
 * conferma di lettura. */
#include "comune.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#include "evento.h"
#include "lingua.h"
#include "sessioni.h"
#include "testo.h"

static char *U, *D; /* nome dell'utente e sua casella */
static conf_t conf;
static volatile sig_atomic_t sveglia, fine;

static void su_sveglia(int s)
{
	(void)s;
	sveglia = 1;
}

static void su_fine(int s)
{
	(void)s;
	fine = 1;
}

static char *percorso(const char *sotto, long long id, const char *suffisso)
{
	return xasprintf("%s/%s/%lld%s", D, sotto, id, suffisso);
}

static bool c_e(const char *sotto, long long id, const char *suffisso)
{
	char *p = percorso(sotto, id, suffisso);
	bool r = esiste(p);

	free(p);
	return r;
}

/* Vero se la copia nella casella è scaduta (o illeggibile: si tratta come
 * non più mostrabile solo se manca). */
static bool scaduto(long long id)
{
	char *p = percorso("inbox", id, "");
	msg_t m;
	bool r = false;

	if (msg_leggi(p, &m) == 0) {
		r = msg_scaduto(&m, adesso());
		msg_libera(&m);
	}
	free(p);
	return r;
}

static void segna_letto(long long id)
{
	char *da = percorso("inbox", id, ""), *a = percorso("read", id, ""), *t = percorso("state", id, ".term"),
	     *g = percorso("state", id, ".gui");

	rename(da, a);
	unlink(t);
	unlink(g);
	free(da);
	free(a);
	free(t);
	free(g);
}

/* ID dei messaggi da mostrare, in ordine. I messaggi scaduti e quelli già
 * confermati (un'interruzione fra la conferma e lo spostamento) passano in read/. */
static void in_attesa(strv_t *out)
{
	char *inbox = xasprintf("%s/inbox", D);
	strv_t ids = {0};

	elenca_numeri(inbox, &ids);
	for (size_t i = 0; i < ids.n; i++) {
		long long id;
		char *f;
		struct stat st;

		leggi_numero(ids.v[i], &id);
		f = percorso("inbox", id, "");
		if (stat(f, &st) < 0 || !S_ISREG(st.st_mode)) {
			free(f);
			continue;
		}
		free(f);
		if (c_e("acks", id, "")) {
			segna_letto(id);
			continue;
		}
		if (scaduto(id)) {
			char *da = percorso("inbox", id, ""), *a = percorso("read", id, "");

			rename(da, a);
			free(da);
			free(a);
			continue;
		}
		strv_add(out, ids.v[i]);
	}
	strv_free(&ids);
	free(inbox);
}

/* Vero se l'utente ha rimandato il messaggio su quel canale da meno di N minuti. */
static bool rimandato(long long id, const char *canale)
{
	char *suff = xasprintf(".%s", canale), *p = percorso("state", id, suff);
	struct stat st;
	bool r = stat(p, &st) == 0 && (long long)(adesso() - st.st_mtime) < conf.remind_minutes * 60;

	free(suff);
	free(p);
	return r;
}

static void rimanda(long long id, const char *canale)
{
	char *suff = xasprintf(".%s", canale), *p = percorso("state", id, suff);
	int fd = open(p, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0644);

	if (fd >= 0) {
		futimens(fd, NULL);
		close(fd);
	}
	evento("RINVIATO", id, U, !strcmp(canale, "term") ? "terminale" : "desktop", "", "");
	free(suff);
	free(p);
}

/* Registra la conferma. Vale la prima: la conferma è scritta in un file
 * temporaneo e pubblicata con link, che fallisce se acks/ID esiste già; così
 * «già confermato» e «scrittura fallita» restano distinti, e non può esistere
 * una conferma scritta a metà.
 * Esito: 0 registrata (o già presente); 1 non registrata (il messaggio resta
 * e verrà richiesto di nuovo); 2 messaggio scaduto; 3 messaggio ritirato. */
static int conferma(long long id, const char *canale)
{
	char *ack = percorso("acks", id, ""), *tmp, *dir;
	char riga[256];
	int fd, n, r = 0;

	if (esiste(ack)) {
		segna_letto(id);
		free(ack);
		return 0;
	}
	/* Senza copia nella casella il messaggio è stato ritirato: niente conferma.
	 * Se il ritiro arriva fra questo controllo e link, vale la data: ams
	 * status non conta una conferma successiva al ritiro. */
	if (!c_e("inbox", id, "")) {
		free(ack);
		return 3;
	}
	if (scaduto(id)) {
		segna_letto(id);
		free(ack);
		return 2;
	}
	tmp = xasprintf("%s/acks/.%lld.%d", D, id, (int)getpid());
	n = snprintf(riga, sizeof riga, "%lld %s\n", (long long)adesso(), canale);
	unlink(tmp);
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0644);
	if (fd < 0 || n <= 0 || scrivi_tutto(fd, riga, (size_t)n) < 0 || fsync(fd) < 0 || close(fd) < 0 ||
	    link(tmp, ack) < 0) {
		const char *err = strerror(errno);

		if (fd >= 0)
			close(fd);
		unlink(tmp);
		if (esiste(ack)) {
			segna_letto(id);
		} else {
			evento("CONFERMA_FALLITA", id, U, canale, err, "");
			r = 1;
		}
		free(tmp);
		free(ack);
		return r;
	}
	unlink(tmp);
	/* la conferma va su disco prima di dire «Confermato» */
	dir = xasprintf("%s/acks", D);
	sync_path(dir);
	free(dir);
	segna_letto(id);
	evento("CONFERMATO", id, U, canale, "", "");
	free(tmp);
	free(ack);
	return 0;
}

/* ---- terminale: chiamato dall'aggancio della shell prima di ogni prompt ---- */

static void mostra_terminale(long long id)
{
	char *p = percorso("inbox", id, "");
	msg_t m;
	buf_t h = {0};

	if (msg_leggi(p, &m) == 0) {
		msg_intestazione(&m, &h);
		putchar('\n');
		printf(T("── AMS · Message from the administrator · %s ──"), h.s);
		printf("\n%s────────────────────────────────────────\n", m.body);
		msg_libera(&m);
	}
	buf_free(&h);
	free(p);
}

/* Chiede la conferma. Esito: 0 sì, 1 no, 2 già confermato altrove (per
 * esempio dal desktop) mentre la domanda era in attesa, 3 messaggio ritirato,
 * 4 messaggio scaduto mentre la domanda era in attesa. Il terminale resta in
 * modo canonico: ciò che l'utente sta scrivendo non si perde fra un
 * controllo e l'altro. */
static int chiedi(long long id)
{
	int tty = open("/dev/tty", O_RDONLY | O_CLOEXEC | O_NOCTTY);
	char risposta[256] = "";

	fputs(T("[AMS] Do you confirm you have read the message? [y/N] "), stdout);
	fflush(stdout);
	if (tty < 0)
		return 1;
	for (;;) {
		struct pollfd p = {.fd = tty, .events = POLLIN};
		int r = poll(&p, 1, 1000);

		if (r > 0) {
			ssize_t l = read(tty, risposta, sizeof risposta - 1);

			risposta[l > 0 ? l : 0] = '\0';
			break;
		}
		if (r < 0 && errno != EINTR)
			break;
		if (c_e("acks", id, "")) {
			putchar('\n');
			close(tty);
			return 2;
		}
		if (!c_e("inbox", id, "")) {
			putchar('\n');
			close(tty);
			return 3;
		}
		if (scaduto(id)) {
			putchar('\n');
			close(tty);
			return 4;
		}
	}
	close(tty);
	return strchr("sSyY", risposta[0]) && risposta[0] ? 0 : 1;
}

static int cmd_prompt(bool login)
{
	const char *t = ttyname(0);
	char *dove;
	strv_t ids = {0};
	int dopo = 0;

	if (!t)
		return 0;
	dove = xasprintf("terminale %s", !strncmp(t, "/dev/", 5) ? t + 5 : t);
	in_attesa(&ids);
	for (size_t i = 0; i < ids.n; i++) {
		long long id;

		leggi_numero(ids.v[i], &id);
		if (!login && rimandato(id, "term")) {
			dopo++;
			continue;
		}
		mostra_terminale(id);
		switch (chiedi(id)) {
		case 0:
			switch (conferma(id, dove)) {
			case 0: fputs(T("[AMS] Confirmed."), stdout); break;
			case 2: fputs(T("[AMS] The message has expired: the confirmation was not recorded."), stdout); break;
			case 3: fputs(T("[AMS] The administrator has revoked the message."), stdout); break;
			default: fputs(T("[AMS] The confirmation could not be recorded: you will be asked again."), stdout); break;
			}
			break;
		case 2:
			segna_letto(id);
			fputs(T("[AMS] Message already confirmed elsewhere (for example on the desktop)."), stdout);
			break;
		case 3:
			fputs(T("[AMS] The administrator has revoked the message."), stdout);
			break;
		case 4:
			segna_letto(id);
			fputs(T("[AMS] The message has expired."), stdout);
			break;
		default:
			rimanda(id, "term");
			printf(T("[AMS] You will be asked again in %ld minutes."), conf.remind_minutes);
			break;
		}
		putchar('\n');
	}
	if (dopo == 1)
		puts(T("[AMS] You have 1 message from the administrator to confirm."));
	else if (dopo > 1) {
		printf(T("[AMS] You have %d messages from the administrator to confirm."), dopo);
		putchar('\n');
	}
	strv_free(&ids);
	free(dove);
	return 0;
}

/* ---- desktop: avviato automaticamente nella sessione grafica ---- */

static sigset_t attesa; /* maschera durante le attese: USR1 e fine arrivano */

/* Aspetta al più ms millisecondi, o un segnale. */
static void aspetta(int ms)
{
	struct timespec ts = {ms / 1000, (long)(ms % 1000) * 1000000L};

	ppoll(NULL, 0, &ts, &attesa);
}

static void avvisa_conferma_fallita(void)
{
	pid_t pid = fork();

	if (pid == 0) {
		int nul = open("/dev/null", O_RDWR);

		if (nul >= 0) {
			dup2(nul, 1);
			dup2(nul, 2);
		}
		execlp("notify-send", "notify-send", "-a", "AMS", T("AMS · Confirmation not recorded"),
		       T("The confirmation could not be recorded: the message will be shown again."), (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, NULL, 0) < 0 && errno == EINTR)
			;
}

/* La finestra di conferma. L'agente la attende e registra la risposta appena
 * arriva; intanto, ogni secondo, la chiude se l'utente ha confermato da un
 * terminale, se l'amministratore ha ritirato il messaggio o se è scaduto. Il
 * segnale di sveglia (un messaggio nuovo) non la chiude. */
static void mostra_finestra(long long id)
{
	char *f = percorso("inbox", id, "");
	msg_t m;
	buf_t testo = {0};
	pid_t pid;
	int stato = 0;
	bool chiusa_da_noi = false;
	long long attesa_fine = 0;

	if (msg_leggi(f, &m) < 0) {
		free(f);
		return;
	}
	msg_intestazione(&m, &testo);
	buf_printf(&testo, "\n\n%s", m.body);
	msg_libera(&m);
	fflush(stdout);
	pid = fork();
	if (pid == 0) {
		char *titolo = xasprintf("--title=%s", T("AMS · Message from the administrator"));
		char *text = xasprintf("--text=%s", testo.s);
		char *ok = xasprintf("--ok-label=%s", T("I have read it"));
		char *no = xasprintf("--cancel-label=%s", T("Later"));
		int nul = open("/dev/null", O_RDWR);
		sigset_t vuoto;

		sigemptyset(&vuoto);
		sigprocmask(SIG_SETMASK, &vuoto, NULL);
		signal(SIGUSR1, SIG_DFL);
		signal(SIGTERM, SIG_DFL);
		signal(SIGHUP, SIG_DFL);
		signal(SIGINT, SIG_DFL);
		if (nul >= 0)
			dup2(nul, 2);
		execlp("zenity", "zenity", "--question", "--no-markup", "--width=460", titolo, text, ok, no, (char *)NULL);
		_exit(127);
	}
	buf_free(&testo);
	if (pid < 0) {
		free(f);
		return;
	}
	for (;;) {
		pid_t w = waitpid(pid, &stato, WNOHANG);

		if (w == pid)
			break;
		if (w < 0 && errno != EINTR)
			break;
		if (!chiusa_da_noi && (c_e("acks", id, "") || !c_e("inbox", id, "") || scaduto(id))) {
			kill(pid, SIGTERM);
			chiusa_da_noi = true;
		}
		/* all'uscita dalla sessione: si aspetta ancora un poco la finestra
		 * (anche lei riceve il segnale), poi la si chiude */
		if (fine && !attesa_fine)
			attesa_fine = (long long)adesso() + 2;
		if (attesa_fine && (long long)adesso() >= attesa_fine && !chiusa_da_noi) {
			kill(pid, SIGTERM);
			chiusa_da_noi = true;
		}
		aspetta(1000);
	}
	if (c_e("acks", id, "") || !c_e("inbox", id, "")) {
		free(f);
		return;
	}
	if (scaduto(id)) {
		segna_letto(id);
		free(f);
		return;
	}
	/* zenity esce con 0 per «Ho letto», con 1 per «Più tardi» o la finestra
	 * chiusa dall'utente. Altri esiti (finestra uccisa) non sono una scelta
	 * dell'utente: niente rinvio, la finestra torna al giro successivo. */
	if (WIFEXITED(stato) && WEXITSTATUS(stato) == 0) {
		if (conferma(id, "desktop") == 1 && c_e("inbox", id, ""))
			avvisa_conferma_fallita();
	} else if (WIFEXITED(stato) && WEXITSTATUS(stato) == 1) {
		rimanda(id, "gui");
	}
	free(f);
}

static char *pronto;

static void togli_pronto(void)
{
	if (pronto)
		unlink(pronto);
}

static int cmd_agent(void)
{
	const char *run = getenv("XDG_RUNTIME_DIR");
	char *lock = xasprintf("%s/ams-agent.lock", run && *run ? run : "/tmp");
	int fd = open(lock, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
	char s[32];
	int n;
	sigset_t blocca;
	struct sigaction sa = {0};

	/* Un solo agente per utente. Il lock non passa ai processi figli
	 * (O_CLOEXEC): una finestra rimasta orfana non blocca un nuovo agente. */
	if (fd < 0 || flock(fd, LOCK_EX | LOCK_NB) < 0)
		return 0;
	/* All'uscita dalla sessione arriva SIGTERM: l'agente finisce di
	 * registrare la risposta già data ed esce al primo punto sicuro. I
	 * segnali restano bloccati tranne durante le attese: nessuno va perso. */
	sa.sa_handler = su_fine;
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	sigaction(SIGINT, &sa, NULL);
	sigemptyset(&blocca);
	sigaddset(&blocca, SIGUSR1);
	sigaddset(&blocca, SIGTERM);
	sigaddset(&blocca, SIGHUP);
	sigaddset(&blocca, SIGINT);
	sigprocmask(SIG_BLOCK, &blocca, &attesa);
	sigdelset(&attesa, SIGUSR1);
	sigdelset(&attesa, SIGTERM);
	sigdelset(&attesa, SIGHUP);
	sigdelset(&attesa, SIGINT);
	/* `ams send` manda SIGUSR1 per svegliare l'agente, ma solo al PID scritto
	 * qui, cioè a un agente che sa già riceverlo. */
	pronto = xasprintf("%s/ams-agent.pronto", run && *run ? run : "/tmp");
	atexit(togli_pronto);
	n = snprintf(s, sizeof s, "%d\n", (int)getpid());
	if (scrivi_atomico(pronto, s, (size_t)n, 0644) < 0)
		return 1;
	while (!fine && sessione_grafica(getuid())) {
		strv_t ids = {0};

		/* una sveglia che arriva da qui in poi (anche con una finestra
		 * aperta) fa ripartire subito il giro */
		sveglia = 0;
		/* la configurazione si rilegge a ogni giro: una modifica vale subito */
		conf_leggi(&conf);
		in_attesa(&ids);
		for (size_t i = 0; i < ids.n && !fine; i++) {
			long long id;

			leggi_numero(ids.v[i], &id);
			if (!rimandato(id, "gui"))
				mostra_finestra(id);
		}
		strv_free(&ids);
		if (fine)
			break;
		/* attesa interrompibile: il segnale di `ams send` la termina subito */
		for (long ms = conf.agent_poll * 1000; ms > 0 && !sveglia && !fine; ms -= 1000)
			aspetta(ms > 1000 ? 1000 : (int)ms);
	}
	return 0;
}

int main(int argc, char **argv)
{
	struct sigaction sa = {0};
	struct passwd *pw;

	/* Prima di tutto: il segnale di sveglia non deve uccidere l'agente mentre
	 * parte. */
	sa.sa_handler = su_sveglia;
	sigaction(SIGUSR1, &sa, NULL);
	ams_init("ams-user");
	lingua_init();
	conf_leggi(&conf);
	pw = getpwuid(getuid());
	if (!pw)
		return 1;
	U = xstrdup(pw->pw_name);
	D = xasprintf("%s/users/%s", ams_var, U);
	if (argc >= 2 && !strcmp(argv[1], "prompt"))
		return cmd_prompt(argc >= 3 && !strcmp(argv[2], "--login"));
	if (argc >= 2 && !strcmp(argv[1], "agent"))
		return cmd_agent();
	/* solo per le prove: la registrazione della conferma, da sola */
	if (ams_test && argc == 4 && !strcmp(argv[1], "conferma")) {
		long long id;

		return leggi_numero(argv[2], &id) ? conferma(id, argv[3]) : 1;
	}
	fputs(T("ams-user: internal AMS helper, not meant to be run directly"), stderr);
	fputc('\n', stderr);
	return 1;
}
