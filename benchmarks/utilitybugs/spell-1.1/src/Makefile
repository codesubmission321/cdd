# Makefile for GNU Spell.

# This file is part of GNU Spell.
# Copyright (C) 1996,2010 Free Software Foundation, Inc.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Start of system configuration section.

SHELL = /bin/sh

srcdir = .
exec_prefix = ${prefix}
prefix = /home/coq/cdd/benchmarks/utilitybug/spell-1.1/src/build
VERSION = 1.1

AUTOCONF = autoconf
CC = gcc
CFLAGS = -g -O2
CPPFLAGS = -I$(srcdir) 
DEFS = -DHAVE_CONFIG_H
DVIPS = dvips
INSTALL = /usr/bin/install -c
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_PROGRAM = ${INSTALL}
LDFLAGS = 
LIBS = 
MAKEINFO = makeinfo
TEXI2DVI = texi2dvi
TEXI2PDF = texi2pdf

bindir = $(exec_prefix)/bin
infodir = $(prefix)/info

# End of system configuration section.

SRCS = spell.c 
OBJS = spell.o

DISTFILES = $(SRCS) COPYING INSTALL Makefile.in README \
	config.h.in configure configure.in fdl.texi install-sh \
	mkinstalldirs sample \
	spell.info spell.texi version.texi

all: spell info

.SUFFIXES:
.SUFFIXES: .c .o

.c.o:
	$(CC) $(CPPFLAGS) $(DEFS) $(CFLAGS) -c $< -o $@

spell: $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) $(LIBS) -o $@

install: installdirs install-info
	$(INSTALL_PROGRAM) spell $(bindir)/spell

install-info:
	$(INSTALL_DATA) $(srcdir)/spell.info $(infodir)/spell.info

uninstall:
	rm -f $(bindir)/spell $(infodir)/spell.info

clean:
	rm -f spell *.o core spell.dvi spell.ps spell.pdf *~

distclean: clean mostlyclean
	rm -f Makefile config.cache config.h config.log config.status
	rm -Rf autom4te.cache

mostlyclean:
	rm -f *.aux *.cp *.cps *.dvi *.ps *.pdf *.fn *.fns *.ky *.log *.toc
	rm -f *pg *.tp *.vr *.op

maintainer-clean: maintainer-clean-msg distclean clean-info
	rm -f configure
	rm -Rf spell-*

maintainer-clean-msg:
	@echo "This command is intended for maintainers to use; it"
	@echo "deletes files that may require special tools to rebuild."

clean-info: mostlyclean
	rm -f spell.info

TAGS: $(SRCS)
	etags $(SRCS)

info: spell.info

spell.info: spell.texi version.texi
	$(MAKEINFO) $(srcdir)/spell.texi

dvi: spell.dvi

spell.dvi: spell.texi fdl.texi version.texi
	$(TEXI2DVI) $(srcdir)/spell.texi

ps: spell.ps

spell.ps: spell.dvi
	$(DVIPS) -o $@ ./spell.dvi

pdf: spell.pdf

spell.pdf: spell.texi fdl.texi version.texi
	$(TEXI2PDF) $(srcdir)/spell.texi

dist: $(DISTFILES)
	rm -rf spell-$(VERSION)
	mkdir spell-$(VERSION)
	chmod 777 spell-$(VERSION)
	for file in $(DISTFILES); \
        do \
	  ln $(srcdir)/$$file spell-$(VERSION) 2> /dev/null \
	    || cp -p $(srcdir)/$$file spell-$(VERSION); \
	done
	chmod -R a+r spell-$(VERSION)
	tar -chozf spell-$(VERSION).tar.gz spell-$(VERSION)
	rm -rf spell-$(VERSION)

check:

installcheck:

installdirs: mkinstalldirs
	$(srcdir)/mkinstalldirs $(bindir) $(infodir)

Makefile: Makefile.in config.status
	CONFIG_FILES=$@ CONFIG_HEADERS= ./config.status

config.status: configure
	./config.status --recheck

configure: configure.in
	cd $(srcdir) && $(AUTOCONF)

# Prevent GNU make v3 from overflowing arg limit on SysV.
.NOEXPORT:

