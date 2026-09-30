# AMS - Advanced Messaging System for linux
#   make                  compila ams, ams-user e le lingue in build/
#   make prove            prove delle parti interne (build/prove-unita)
#   make analizza         analisi statica di gcc (-fanalyzer)
#   make sanitizer        compila con AddressSanitizer e UBSan in build-san/
#   make pot              aggiorna po/ams.pot e i .po dai sorgenti
#   make clean

PREFIX    ?= /usr/local
LIBDIR    ?= $(PREFIX)/lib/ams
LOCALEDIR ?= $(PREFIX)/share/locale
B         ?= build

CC      ?= gcc
AVVISI   = -Wall -Wextra -Wpedantic -Wformat=2 -Wformat-security -Wshadow -Wpointer-arith \
           -Wcast-qual -Wwrite-strings -Wstrict-prototypes -Wmissing-prototypes -Wvla \
           -Wnull-dereference -Wimplicit-fallthrough -Wundef -Werror
DIFESE   = -D_FORTIFY_SOURCE=3 -fstack-protector-strong -fstack-clash-protection -fcf-protection -fPIE
CFLAGS  ?= -O2 -g
CFLAGS  += -std=c17 -D_GNU_SOURCE $(AVVISI) $(DIFESE) \
           -DLIBDIR='"$(LIBDIR)"' -DLOCALEDIR='"$(LOCALEDIR)"'
LDFLAGS += -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack
LIBS     = $(shell pkg-config --libs libsystemd)

COMUNI  = comune testo lingua evento utente sessioni
OGG     = $(COMUNI:%=$(B)/%.o)
LINGUE  = $(patsubst po/%.po,%,$(wildcard po/*.po))
MO      = $(LINGUE:%=$(B)/locale/%/LC_MESSAGES/ams.mo)

all: $(B)/ams $(B)/ams-user $(MO)

$(B)/%.o: src/%.c src/*.h | $(B)
	$(CC) $(CFLAGS) -c -o $@ $<

$(B)/ams: $(OGG) $(B)/ams.o $(B)/guida.o $(B)/archivio.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/ams-user: $(OGG) $(B)/ams-user.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/prove-unita: $(OGG) $(B)/prove-unita.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/prove-unita.o: tests/prove-unita.c src/*.h | $(B)
	$(CC) $(CFLAGS) -Isrc -c -o $@ $<

$(B)/locale/%/LC_MESSAGES/ams.mo: po/%.po
	@mkdir -p $(dir $@)
	msgfmt --check -o $@ $<

$(B):
	mkdir -p $(B)

prove: $(B)/prove-unita $(MO)
	AMS_TEST=1 AMS_LOCALEDIR=$(B)/locale $(B)/prove-unita

analizza:
	$(MAKE) B=build-analisi CFLAGS="-O1 -g -fanalyzer" all

sanitizer:
	$(MAKE) B=build-san CFLAGS="-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer" \
		LDFLAGS="-fsanitize=address,undefined" DIFESE="-fPIE" all build-san/prove-unita

pot:
	xgettext --from-code=UTF-8 -k -kT -kN_ -kTC:1c,2 -kNC_:1c,2 -ktl:2 -ktlc:2c,3 --add-comments=TRADUTTORI \
		--package-name=AMS --package-version=$$(sed -n 's/^#define AMS_VERSION "\(.*\)"/\1/p' src/comune.h) \
		-o po/ams.pot src/*.c
	for p in po/*.po; do msgmerge -q --update --backup=none $$p po/ams.pot; done

clean:
	rm -rf build build-analisi build-san

.PHONY: all prove analizza sanitizer pot clean
