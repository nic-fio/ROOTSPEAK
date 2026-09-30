# AMS - Advanced Messaging System for linux
# Testi della guida integrata (ams --help) in italiano. Le voci di comandi e
# opzioni sono anche nel riferimento del manuale utente, con lo stesso testo:
# tools/check-docs.py lo controlla. Ogni lingua ha le stesse voci.
# shellcheck disable=SC2034

# Voci "etichetta¦descrizione".
AMS_HELP_COMMANDS=(
	"send [opzioni] [TESTO]¦Invia un messaggio ai destinatari indicati con --to. Senza TESTO né --file, il testo viene letto da stdin."
	"list¦Elenca i messaggi inviati, con quanti destinatari hanno confermato ciascun messaggio."
	"status ID¦Mostra il testo del messaggio e lo stato di ogni destinatario: inviato, consegnato (nella sua casella) o confermato, con data, ora e canale."
	"revoke ID¦Ritira un messaggio: chi non l'ha ancora visto non lo vedrà più, e finestre e domande ancora aperte si chiudono da sole."
	"log ID¦Mostra la storia del messaggio dal registro di sistema: invio, consegne, rinvii, conferme e ritiro, con data e ora."
	"purge DURATA¦Cancella i messaggi inviati da più di DURATA (per esempio 90d), con le copie e le conferme nelle caselle degli utenti; gli eventi restano nel registro di sistema."
	"version¦Mostra la versione di AMS."
	"help, --help, -h¦Mostra questa guida. La apre anche «ams» senza argomenti."
)

AMS_HELP_OPTIONS=(
	"--to DEST¦Destinatari, separati da virgole senza spazi: un utente (mario), un gruppo Unix (@sviluppo), all (tutti gli utenti umani) oppure online (solo quelli collegati adesso)."
	"--title TITOLO¦Titolo mostrato nell'intestazione del messaggio e nella finestra del desktop."
	"--expires DURATA¦Scadenza, dopo la quale il messaggio non viene più mostrato: 30m, 2h, 3d oppure data e ora (\"2026-10-04 12:00\"; le date a parole vanno in inglese)."
	"--file FILE¦Legge il testo del messaggio da FILE."
)

AMS_HELP_EXAMPLES=(
	"ams send --to mario \"Il tuo account scade venerdì.\"¦Messaggio con conferma di lettura a un solo utente."
	"ams send --to @sviluppo --title Manutenzione --file avviso.txt¦Testo preso da un file, con titolo, a tutti i membri del gruppo sviluppo."
	"ams send --to online --expires 15m \"Riavvio alle 13:00.\"¦Avviso urgente a chi è collegato adesso; dopo 15 minuti non viene più mostrato né sollecitato."
	"ams send --to all --expires 3d \"Nuova policy password.\"¦A tutti gli utenti; dopo tre giorni smette di essere mostrato."
	"ams list¦Quali messaggi sono stati inviati e quante conferme hanno."
	"ams status 12¦Chi ha confermato il messaggio 12, quando e da dove."
	"ams log 12¦La storia del messaggio 12: invio, consegne, rinvii, conferme."
	"ams purge 90d¦Cancella i messaggi di più di 90 giorni fa, con copie e conferme."
	"ams revoke 12¦Ritira il messaggio 12."
)

AMS_HELP_FILES=(
	"/etc/ams/ams.conf¦Configurazione: minuti prima di riproporre un messaggio rimandato, intervallo di controllo dell'agente del desktop."
	"/var/lib/ams/¦I messaggi: sent/ (copie di riferimento, solo root) e users/UTENTE/ (la casella di ogni utente, leggibile solo da lui e da root)."
	"sudo journalctl -t ams¦Il registro di sistema: invii, consegne, conferme e ritiri."
	"/usr/local/share/doc/ams/AMS_Manuale_Utente.html¦Il manuale utente completo, da aprire in un browser."
)

AMS_HELP_DESCRIPTION="AMS permette agli amministratori di mandare messaggi di testo agli utenti della \
macchina e di sapere chi li ha letti. I messaggi compaiono nei terminali (console, ssh, terminali del \
desktop, tmux) e sul desktop, in una finestra con i pulsanti «Ho letto» e «Più tardi»; chi non è \
collegato li trova al login successivo. Ogni messaggio chiede la conferma di lettura e AMS la \
ripropone finché l'utente non la dà, senza mai bloccare il lavoro. Ogni utente vede AMS nella sua \
lingua. Il comando è riservato agli amministratori (gruppo sudo o wheel) e si rilancia da solo con sudo."

AMS_HELP_SYNOPSIS=(
	"ams send --to DEST [opzioni] [TESTO]"
	"ams list"
	"ams status ID"
	"ams revoke ID"
	"ams log ID"
	"ams purge DURATA"
	"ams version"
)

declare -gA AMS_HELP_L=(
	[title]="Manuale di ams"
	[name]="ams — invia messaggi agli utenti della macchina e ne segue la conferma di lettura"
	[short]="ams — messaggi agli utenti con conferma di lettura"
	[h_name]="NOME"
	[h_synopsis]="SINTASSI"
	[h_description]="DESCRIZIONE"
	[h_commands]="COMANDI"
	[h_options]="OPZIONI DI SEND"
	[h_examples]="ESEMPI"
	[h_files]="FILE"
	[h_environment]="AMBIENTE"
	[h_exit]="STATO DI USCITA"
	[h_see]="VEDERE ANCHE"
	[pager]="Pager usato per impaginare questa guida quando il terminale è troppo piccolo per quella interattiva (predefinito: less). Come NO_COLOR, arriva ad ams solo se sudo la conserva (env_keep in sudoers)."
	[no_color]="Se impostata, disabilita i colori."
	[exit0]="Completato con successo."
	[exit1]="Errore: il messaggio d'errore, che inizia con «ams:», dice quale."
	[see]="wall(1), write(1), e il manuale utente in /usr/local/share/doc/ams/AMS_Manuale_Utente.html"
	[manual]="AMS %s · manuale completo: /usr/local/share/doc/ams/AMS_Manuale_Utente.html"
	[tabs]="Info Comandi Opzioni Esempi File"
	[t_commands]="Comandi"
	[t_options]="Opzioni di send"
	[t_examples]="Esempi"
	[t_files]="File e registro"
	[frame]="ams — guida"
	[lines]="righe %s-%s/%s"
	[hint]="←/→ schede · ↑/↓ scorri · PgUp/PgDn · g/G · q esci"
)
