# serial 14

# Copyright (C) 2003, 2007, 2009-2020 Free Software Foundation, Inc.
# This file is free software; the Free Software Foundation
# gives unlimited permission to copy and/or distribute it,
# with or without modifications, as long as this notice is preserved.

# Written by Paul Eggert and Jim Meyering.

AC_DEFUN([gl_FUNC_TZSET],
[
  AC_REQUIRE([gl_HEADER_TIME_H_DEFAULTS])
  AC_REQUIRE([AC_CANONICAL_HOST])
  AC_CHECK_FUNCS_ONCE([tzset])
  if test $ac_cv_func_tzset = no; then
    HAVE_TZSET=0
  fi
  REPLACE_TZSET=0
  case "$host_os" in
    mingw*) REPLACE_TZSET=1 ;;
  esac
])
