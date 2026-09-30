# Copyright e componenti di terzi

AMS - Advanced Messaging System
Copyright (c) 2026 nic-fio. Tutti i diritti riservati.

Il repository è privato. Non è concessa alcuna licenza d'uso, copia, modifica
o distribuzione: per qualunque uso serve un permesso esplicito dell'autore.

## Componenti di terzi

AMS non incorpora né distribuisce codice di terzi: `ams`, `ams-user`, gli
agganci delle shell, i cataloghi delle lingue e i manuali sono scritti per
questo progetto. Lo stile dei manuali viene da IR_Service, un altro progetto
dello stesso autore.

Usa, senza includerli, programmi e librerie già presenti nel sistema, ciascuno
con la propria licenza:

| Componente | Come lo usa AMS | Licenza |
|---|---|---|
| libsystemd | collegata dinamicamente a `ams` e `ams-user` (journal, sessioni di logind) | LGPL-2.1 o successiva |
| zenity, notify-send | lanciati come programmi esterni, per la finestra di conferma sul desktop | LGPL-2.1 o successiva |
| gettext (`msgfmt`, `xgettext`) | solo per compilare i cataloghi delle lingue: i `.mo` li legge un lettore di AMS, non la libintl | GPL-3.0 o successiva |
| Pygments | solo per generare i manuali (evidenziazione del codice) | BSD 2-Clause |
