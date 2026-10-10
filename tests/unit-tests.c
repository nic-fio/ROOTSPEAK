/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * Tests of the internals of the C version.
 *   unit-tests                    all the tests
 *   unit-tests clean              cleans stdin onto stdout (comparison with the prototype)
 *   unit-tests conf               values read from the configuration (RSPEAK_CONF, with RSPEAK_TEST=1) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "common.h"
#include "event.h"
#include "text.h"

static int tests, failed;

static void check(const char *what, bool ok)
{
	tests++;
	if (!ok) {
		failed++;
		printf("  NO   %s\n", what);
	}
}

static bool cleaned_equals(const char *in, size_t n, const char *expected)
{
	buf_t b = {0};
	bool ok;

	clean_text(in, n, &b);
	ok = strlen(expected) == b.n && !memcmp(b.s ? b.s : "", expected, b.n);
	if (!ok)
		printf("       clean_text: expected «%s», got «%s»\n", expected, b.s ? b.s : "");
	buf_free(&b);
	return ok;
}

static void test_cleaning(void)
{
	check("CSI removed", cleaned_equals("a\033[31mred\033[0m b", 15, "ared b"));
	check("OSC removed", cleaned_equals("x\033]0;title\007y", 12, "xy"));
	check("OSC without BEL: the text stays, ESC goes", cleaned_equals("x\033]0;t\ny", 8, "x]0;t\ny"));
	check("C0 removed except tab and newline", cleaned_equals("a\001\tb\n\rc\177", 8, "a\tb\nc"));
	check("C1 in UTF-8 removed", cleaned_equals("a\xc2\x85" "b\xc2\xa0", 6, "ab\xc2\xa0"));
	check("normal UTF-8 untouched", cleaned_equals("naïve café ünïcode", 22, "naïve café ünïcode"));
}

static void test_message(void)
{
	const char t[] = "format: 1\nid: 12\nfrom: root\ndate: 1700000000\ntitle: Test\nexpires: 1700000100\n\nline 1\n\nline 3\n";
	msg_t m;
	buf_t b = {0};

	check("message read", msg_from_text(t, sizeof t - 1, &m) == 0 && m.id == 12 && !strcmp(m.from, "root") &&
					     m.date == 1700000000 && !strcmp(m.title, "Test") && m.expires == 1700000100 &&
					     !strcmp(m.body, "line 1\n\nline 3\n"));
	msg_format(&m, &b);
	check("message written back the same", b.n == sizeof t - 1 && !memcmp(b.s, t, b.n));
	check("expired after the expiry", msg_expired(&m, 1700000100) && !msg_expired(&m, 1700000099));
	msg_free(&m);
	buf_free(&b);
	check("without a date: refused", msg_from_text("id: 1\n\ntext!", 13, &m) < 0);
}

static void test_conf(void)
{
	conf_t c;

	conf_from_text("RSPEAK_REMIND_MINUTES=45 # minutes\n  RSPEAK_AGENT_POLL = 20  \n", &c);
	check("configuration: comments and spaces", c.remind_minutes == 45 && c.agent_poll == 20);
	conf_from_text("RSPEAK_REMIND_MINUTES=$(rm -rf /)\nRSPEAK_AGENT_POLL=0\nOTHER=5\n", &c);
	check("configuration: invalid values ignored", c.remind_minutes == 30 && c.agent_poll == 60);
	conf_from_text("RSPEAK_REMIND_MINUTES=1234567\nRSPEAK_AGENT_POLL=-5\n", &c);
	check("configuration: too many digits and negative values ignored", c.remind_minutes == 30 && c.agent_poll == 60);
}

static void test_events(void)
{
	buf_t b = {0};

	event_text("CONFIRMED", 3, "mario", "terminal pts/2", "", "", &b);
	check("event text", !strcmp(b.s, "user mario: confirmed reading message 3 (terminal pts/2)"));
	buf_clear(&b);
	check("unknown event", !event_text("UNKNOWN", 1, "", "", "", "", &b));
	buf_free(&b);
}

int main(int argc, char **argv)
{
	rspeak_init("unit-tests");
	if (argc > 1 && !strcmp(argv[1], "clean")) {
		buf_t in = {0}, out = {0};

		read_fd(0, (size_t)1 << 26, &in);
		clean_text(in.s ? in.s : "", in.n, &out);
		write_all(1, out.s ? out.s : "", out.n);
		return 0;
	}
	if (argc == 2 && !strcmp(argv[1], "conf")) {
		conf_t c;

		conf_read(&c);
		printf("%ld %ld\n", c.remind_minutes, c.agent_poll);
		return 0;
	}
	test_cleaning();
	test_message();
	test_conf();
	test_events();
	if (failed) {
		printf("FAILED: %d of %d\n", failed, tests);
		return 1;
	}
	printf("OK: %d tests\n", tests);
	return 0;
}
