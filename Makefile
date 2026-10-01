# RootSpeak - Advanced Messaging System for Linux
#   make                  builds rspeak and rootspeak-user in build/
#   make unit             unit tests (build/unit-tests)
#   make test             quick tests: unit tests, manual checks, tests/engine.sh
#   make docs             regenerates the manuals (python3 docs/sources/build.py)
#   make docs-check       only the manual checks (tools/check-docs.py)
#   make analyze          gcc static analysis (-fanalyzer)
#   make sanitizer        builds with AddressSanitizer and UBSan in build-san/
#   make clean

PREFIX    ?= /usr/local
LIBDIR    ?= $(PREFIX)/lib/rootspeak
B         ?= build

CC      ?= gcc
WARNINGS   = -Wall -Wextra -Wpedantic -Wformat=2 -Wformat-security -Wshadow -Wpointer-arith \
           -Wcast-qual -Wwrite-strings -Wstrict-prototypes -Wmissing-prototypes -Wvla \
           -Wnull-dereference -Wimplicit-fallthrough -Wundef -Werror
HARDENING   = -D_FORTIFY_SOURCE=3 -fstack-protector-strong -fstack-clash-protection -fcf-protection -fPIE
CFLAGS  ?= -O2 -g
CFLAGS  += -std=c17 -D_GNU_SOURCE $(WARNINGS) $(HARDENING) \
           -DLIBDIR='"$(LIBDIR)"'
LDFLAGS += -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack
LIBS     = $(shell pkg-config --libs libsystemd)

COMMON  = common text event user sessions
OBJ     = $(COMMON:%=$(B)/%.o)

all: $(B)/rspeak $(B)/rootspeak-user

$(B)/%.o: src/%.c src/*.h | $(B)
	$(CC) $(CFLAGS) -c -o $@ $<

$(B)/rspeak: $(OBJ) $(B)/rspeak.o $(B)/help.o $(B)/store.o $(B)/tui.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/rootspeak-user: $(OBJ) $(B)/rootspeak-user.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/unit-tests: $(OBJ) $(B)/unit-tests.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

$(B)/unit-tests.o: tests/unit-tests.c src/*.h | $(B)
	$(CC) $(CFLAGS) -Isrc -c -o $@ $<

$(B):
	mkdir -p $(B)

unit: $(B)/unit-tests
	RSPEAK_TEST=1 $(B)/unit-tests

# the manual checks before tests/engine.sh: the engine rewrites
# tests/results/engine.json (date and commit), which the manuals show
test: all unit docs-check
	tests/engine.sh

docs:
	python3 docs/sources/build.py

docs-check:
	python3 tools/check-docs.py

analyze:
	$(MAKE) B=build-analyze CFLAGS="-O1 -g -fanalyzer" all

sanitizer:
	$(MAKE) B=build-san CFLAGS="-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer" \
		LDFLAGS="-fsanitize=address,undefined" HARDENING="-fPIE" all build-san/unit-tests

clean:
	rm -rf build build-analyze build-san

.PHONY: all unit test docs docs-check analyze sanitizer clean
