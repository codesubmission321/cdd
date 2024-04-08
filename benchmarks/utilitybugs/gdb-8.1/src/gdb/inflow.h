/* Low level interface to ptrace, for GDB when running under Unix.

   Copyright (C) 2003-2018 Free Software Foundation, Inc.

   This file is part of GDB.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

#ifndef INFLOW_H
#define INFLOW_H

#include <unistd.h>

/* Process group of the current inferior.  */
#ifdef HAVE_TERMIOS_H
extern pid_t inferior_process_group (void);
#endif

#endif /* inflow.h */
