/* Mirrored Unicode characters.
   Copyright (C) 2002, 2006, 2009-2020 Free Software Foundation, Inc.
   Written by Bruno Haible <bruno@clisp.org>, 2002.

   This program is free software: you can redistribute it and/or modify it
   under the terms of the GNU Lesser General Public License as published
   by the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

#include <config.h>

/* Specification.  */
#include "unictype.h"

/* Define u_mirror table.  */
#include "mirror.h"

bool
uc_mirror_char (ucs4_t uc, ucs4_t *puc)
{
  unsigned int index1 = uc >> mirror_header_0;
  if (index1 < mirror_header_1)
    {
      int lookup1 = u_mirror.level1[index1];
      if (lookup1 >= 0)
        {
          unsigned int index2 = (uc >> mirror_header_2) & mirror_header_3;
          int lookup2 = u_mirror.level2[lookup1 + index2];
          if (lookup2 >= 0)
            {
              unsigned int index3 = (uc & mirror_header_4);
              int lookup3 = u_mirror.level3[lookup2 + index3];

              *puc = uc + lookup3;
              return (lookup3 != 0);
            }
        }
    }
  *puc = uc;
  return false;
}
