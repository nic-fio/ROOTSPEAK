# Copyright e componenti di terzi

RootSpeak - Advanced Messaging System for Linux
Copyright (c) 2026 nic-fio. Tutti i diritti riservati.

Il repository è privato. Non è concessa alcuna licenza d'uso, copia, modifica
o distribuzione: per qualunque uso serve un permesso esplicito dell'autore.

## Componenti di terzi

RootSpeak non incorpora né distribuisce codice di terzi: `rspeak`, `rootspeak-user`, gli
agganci delle shell, i cataloghi delle lingue e i manuali sono scritti per
questo progetto. Lo stile dei manuali viene da IR_Service, un altro progetto
dello stesso autore.

Usa, senza includerli, programmi e librerie già presenti nel sistema, ciascuno
con la propria licenza:

| Componente | Come lo usa RootSpeak | Licenza |
|---|---|---|
| libsystemd | collegata dinamicamente a `rspeak` e `rootspeak-user` (journal, sessioni di logind) | LGPL-2.1 o successiva |
| zenity, notify-send | lanciati come programmi esterni, per la finestra di conferma sul desktop | LGPL-2.1 o successiva |
| gettext (`msgfmt`, `xgettext`) | solo per compilare i cataloghi delle lingue: i `.mo` li legge un lettore di RootSpeak, non la libintl | GPL-3.0 o successiva |
| Pygments | solo per generare i manuali (evidenziazione del codice) | BSD 2-Clause |
