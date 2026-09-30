# AMS - Advanced Messaging System
#   make                  compila ams, ams-user e le lingue in build/
#   make prove            prove delle parti interne (build/unit-tests)
#   make test             prove veloci: prove, controlli dei manuali, tests/engine.sh
#   make docs             rigenera i manuali (python3 docs/sources/build.py)
#   make docs-check       solo i controlli dei manuali (tools/check-docs.py)
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

$(B)/ams: $(OGG) $(B)/ams.o $(B)/guida.o $(B)/archivio.o $(B)/tui.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/ams-user: $(OGG) $(B)/ams-user.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/unit-tests: $(OGG) $(B)/unit-tests.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/unit-tests.o: tests/unit-tests.c src/*.h | $(B)
	$(CC) $(CFLAGS) -Isrc -c -o $@ $<

$(B)/locale/%/LC_MESSAGES/ams.mo: po/%.po
	@mkdir -p $(dir $@)
	msgfmt --check -o $@ $<

$(B):
	mkdir -p $(B)

prove: $(B)/unit-tests $(MO)
	AMS_TEST=1 AMS_LOCALEDIR=$(B)/locale $(B)/unit-tests

# i controlli dei manuali prima di tests/engine.sh: il motore riscrive
# tests/results/engine.json (data e commit), che i manuali riportano
test: all prove docs-check
	tests/engine.sh

docs:
	python3 docs/sources/build.py

docs-check:
	python3 tools/check-docs.py

analizza:
	$(MAKE) B=build-analisi CFLAGS="-O1 -g -fanalyzer" all

sanitizer:
	$(MAKE) B=build-san CFLAGS="-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer" \
		LDFLAGS="-fsanitize=address,undefined" DIFESE="-fPIE" all build-san/unit-tests

pot:
	xgettext --from-code=UTF-8 -k -kT -kN_ -kTC:1c,2 -kNC_:1c,2 -ktl:2 -ktlc:2c,3 --add-comments=TRADUTTORI \
		--package-name=AMS --package-version=$$(sed -n 's/^#define AMS_VERSION "\(.*\)"/\1/p' src/comune.h) \
		-o po/ams.pot src/*.c
	for p in po/*.po; do msgmerge -q --update --backup=none $$p po/ams.pot; done

clean:
	rm -rf build build-analisi build-san

.PHONY: all prove test docs docs-check analizza sanitizer pot clean
