/* spell.c -- clone of Unix `spell'.

   This file is part of GNU Spell.
   Copyright (C) 1996,2010 Free Software Foundation, Inc.
   Written by Thomas Morgan <tmorgan@pobox.com> and others

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/* Local headers.  */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* System headers.  */

#include <sys/types.h>
#include <ctype.h>
#include <errno.h>
#include <memory.h>
#include <pwd.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>
#include <getopt.h>

#ifdef HAVE_STRING_H
#include <string.h>
#else /* not HAVE_STRING_H */
#include <strings.h>
#endif /* not HAVE_STRING_H */

/* Always add at least this many bytes when extending the buffer.  */
#define MIN_CHUNK 64

#ifndef STDIN_FILENO
#define STDIN_FILENO 0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2
#endif /* STDIN_FILENO */

#ifndef SIG_ERR
#define SIG_ERR (-1)
#endif

#ifndef EXIT_SUCCESS
#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1
#endif /* EXIT_SUCCESS */

/* Used for communication through a pipe.  */
struct pipe
  {
    /* File descriptors used by the parent process.  */
    int pin;			/* Input channel.  */
    FILE* fpin;
    int pout;			/* Output channel.  */
    int perr;			/* Error channel (for reading).  */
    FILE* fperr;

    /* File descriptors used by the child process.  */
    int cin;			/* Input channel.  */
    int cout;			/* Output channel.  */
    int cerr;			/* Error channel (for writing).  */

    fd_set error_set;		/* Descriptor set used to check for
				   errors (contains perr).  */
  };
typedef struct pipe pipe_t;

#ifndef HAVE_STRERROR
static char *strerror (int);
#endif

static char *xstrdup (const char *);
static void *xmalloc (size_t);
static void *xrealloc (void *, size_t);
static void error (int status, int errnum, const char *message,...);
static void sig_chld (int);
static void sig_pipe (int);
void new_pipe (pipe_t *);
void parent (pipe_t *, int, char **);
void read_file (pipe_t *, FILE *, char *);
void read_ispell (pipe_t *, char *, int);
void read_ispell_errors (pipe_t *);
void run_ispell_in_child (pipe_t *);

/* Switch information for `getopt'.  */
const struct option long_options[] =
{
  {"all-chains", no_argument, NULL, 'l'},
  {"british", no_argument, NULL, 'b'},
  {"dictionary", required_argument, NULL, 'd'},
  {"help", no_argument, NULL, 'h'},
  {"ispell", required_argument, NULL, 'i'},
  {"ispell-version", no_argument, NULL, 'I'},
  {"number", no_argument, NULL, 'n'},
  {"print-file-name", no_argument, NULL, 'o'},
  {"print-stems", no_argument, NULL, 'x'},
  {"stop-list", required_argument, NULL, 's'},
  {"verbose", no_argument, NULL, 'v'},
  {"version", no_argument, NULL, 'V'},
  {NULL, 0, NULL, 0}
};

/* The name of the executable this process comes from.  */
char *program_name = NULL;

/* Location of Ispell/Aspell.  */
char *ispell_prog = NULL;

/* Dictionary to use.  Just use the default if NULL.  */
char *dictionary = NULL;

/* Display Ispell's version (--ispell-version, -I). */
int show_ispell_version = 0;

/* Whether we've read from stdin already.  */
int read_stdin = 0;

/* Whether we're using the British dictionary (--british, -b).  */
int british = 0;

/* Whether we're printing out words even if they need affixes added to
   be spelled correctly (--verbose, -v).  */
int verbose = 0;

/* Whether we're prepending line numbers to the lines (--number, -n).  */
int number_lines = 0;

/* Whether we're printing the file names before the lines
   (--print-file-name, -o).  */
int print_file_names = 0;

/* Whether we're reading from the terminal.  We never will.  */
int interactive = 0;

int
main (int argc, char **argv)
{
  int opt = 0;			/* Current option.  */
  int opt_error = 0;		/* Whether an option error occurred.  */
  int show_help = 0;		/* Display help (--help, -h).  */
  int show_version = 0;		/* Display the version (--version, -V).  */
  pid_t pid = 0;		/* Child's pid.  */
  pipe_t ispell_pipe;		/* The descriptors for our pipe.  */

  program_name = argv[0];

  /* Option processing loop.  */
  while (1)
    {
      opt = getopt_long (argc, argv, "IVbdhilnosvx", long_options,
			 (int *) 0);

      if (opt == EOF)
	break;

      switch (opt)
	{
	case 'I':
	  show_ispell_version = 1;
	  break;
	case 'V':
	  show_version = 1;
	  break;
	case 'b':
	  british = 1;
	  break;
	case 'd':
	  if (optarg != NULL)
	    dictionary = xstrdup (optarg);
	  else
	    error (0, 0, "option argument not given");
	  break;
	case 'h':
	  show_help = 1;
	  break;
	case 'i':
	  if (optarg != NULL)
	    ispell_prog = xstrdup (optarg);
	  else
	    error (0, 0, "option argument not given");
	  break;
	case 'l':
	  break;
	case 'n':
	  number_lines = 1;
	  break;
	case 'o':
	  print_file_names = 1;
	  break;
	case 's':
	  break;
	case 'v':
	  verbose = 1;
	  break;
	case 'x':
	  break;
	default:
	  opt_error = 1;
	  break;
	}
    }

  if (opt_error)
    {
      printf ("Try `%s --help' for more information.\n", program_name);
      exit (EXIT_FAILURE);
    }

  if (show_version)
    {
      puts ( "GNU Spell " VERSION "\n"
	"Copyright (C) 1996,2010 Free Software Foundation, Inc.\n"
	"License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\n"
	"This is free software: you are free to change and redistribute it.\n"
	"There is NO WARRANTY, to the extent permitted by law.\n"
	);
      exit (EXIT_SUCCESS);
    }

  if (show_help)
    {
      printf ("Usage: %s [OPTION]... [FILE]...\n", program_name);
      puts ("This is GNU Spell, a Unix spell emulator.\n\n"
	     "  -I, --ispell-version\t\tPrint Ispell's version.\n"
	     "  -V, --version\t\t\tPrint the version number.\n"
	     "  -b, --british\t\t\tUse the British dictionary.\n"
	     "  -d, --dictionary=FILE\t\tUse FILE to look up words.\n"
	     "  -h, --help\t\t\tPrint a summary of the options.\n"
	     "  -i, --ispell=PROGRAM\t\tCalls PROGRAM as Ispell.\n"
	     "  -l, --all-chains\t\tIgnored; for compatibility.\n"
	     "  -n, --number\t\t\tPrint line numbers before lines.\n"
	     "  -o, --print-file-name\t\tPrint file names before lines.\n"
	     "  -s, --stop-list=FILE\t\tIgnored; for compatibility.\n"
	     "  -v, --verbose\t\t\tPrint words not literally found.\n"
	     "  -x, --print-stems\t\tIgnored; for compatibility.\n\n"
	     "Please use Info to read more (type `info spell').\n"
	     "Report bugs to: cate@gnu.org\n"
	     "spell home page: <http://www.gnu.org/software/spell/>\n"
	     "General help using GNU software: <http://www.gnu.org/gethelp/>\n"
	   );
      exit (EXIT_SUCCESS);
    }

  if (!ispell_prog)
    ispell_prog = "ispell";

  new_pipe (&ispell_pipe);

  pid = fork ();

  if (pid < 0)
    error (EXIT_FAILURE, errno, "error forking to run Ispell");
  else if (pid > 0)
    parent (&ispell_pipe, argc, argv);
  else
    run_ispell_in_child (&ispell_pipe);

  exit (EXIT_SUCCESS);
}


/* Read the file *FILE, opened in the file stream *STREAM.  Send
   output, line by line, through *THE_PIPE (created by `new_pipe').  */
#undef INITIAL_BUFF_SIZE
#define INITIAL_BUFF_SIZE   2048

void
read_file (pipe_t * the_pipe, FILE * stream, char *file)
{
  size_t buff_size = INITIAL_BUFF_SIZE;
  char *buff = xmalloc(sizeof(char[INITIAL_BUFF_SIZE]));
  ssize_t len, rlen, zlen;
  char *wbuff;
  unsigned long line = 0;

  while (1)
    {
      len = getline(&buff, &buff_size, stream);
      line++;
      if (len < 0) {
        if (feof(stream)) {
	    free(buff);
            return;
	} else {
	    error (EXIT_FAILURE, errno, "%s: error reading line", file);
	}
     }
    /* In case there was no newline at the end of the file.  */
    if (len>0  && buff[len-1] != '\n') {
      if (len >= buff_size-1)
	buff = xrealloc(buff, buff_size += 16);
      buff[len] = '\n';
      len++;
    }
    /* The '\0' chars in the string are transformed to a space ' ' */
    wbuff = buff;
    rlen = 0;
    zlen = 0;
    while (1) {
      rlen = strlen(wbuff);
      zlen += rlen;
      if (zlen >= len)
	break;
      wbuff[rlen] = ' ';
      wbuff += rlen;
    }

    rlen = write (the_pipe->pout, "^", 1);
    if (rlen <= 0)
        error (EXIT_FAILURE, errno, "error writing to Ispell");

    wbuff = buff;
    while (len > 0) {
      rlen = write (the_pipe->pout, wbuff, len);
      if (rlen <= 0)
	error (EXIT_FAILURE, errno, "error writing to Ispell");
      len -= rlen;
      wbuff += rlen;
    }
    fsync(the_pipe->pout);

    read_ispell_errors (the_pipe);
    read_ispell (the_pipe, file, line);
    read_ispell_errors (the_pipe);
  }

  if (fclose (stream) == EOF)
    error (0, errno, "%s: close error", file);
  free(buff);
}

/* Read all of Ispell's corrections for a line of text (already
   submitted) from the open pipe *ISPELL_PIPE (created by `new_pipe').
   Must be called from the parent process communicating with Ispell.
   Print out the misspelled words, processing until seeing a blank
   line.  */
#undef INITIAL_BUFF_SIZE
#define INITIAL_BUFF_SIZE   256

void
read_ispell (pipe_t * ispell_pipe, char *file, int line)
{
  size_t buff_size = INITIAL_BUFF_SIZE;
  char *buff = xmalloc(sizeof(char[INITIAL_BUFF_SIZE]));
  ssize_t len;
  char b0;

  while (1)
    {
      len = getline(&buff, &buff_size, ispell_pipe->fpin);
      if (len == -1) {
	if (feof(ispell_pipe->fpin))
	    exit (EXIT_SUCCESS);
	else
	    error(EXIT_FAILURE, errno, "error reading data from ispell/aspell");
     }
     b0 = buff[0];
     /* Ispell gives us a blank line when it's finished processing
        the line we just gave it.  */
     if (len == 1 && b0 == '\n') {
      free(buff);
	return;
      }
      /* There was no problem with this word.  */
      if (b0 == '*' || b0 == '+'
	  || b0 == '-')
	continue;

      /* The word appears to have been misspelled.  */
      if (b0 == '&' || b0 == '#'
	  || (b0 == '?' && verbose))
	{
	  int pos;

	  if (print_file_names)
	    {
	      printf ("%s:", file);
	      if (!number_lines)
		putchar (' ');
	    }
	  if (number_lines)
	    printf ("%d: ", line);

	  for (pos = 2; buff[pos] != ' '; pos++)
	    putchar (buff[pos]);
	  putchar ('\n');

	  continue;
	}

      if (b0 == '?' && !verbose)
	continue;

      error (0, 0, "unrecognized Ispell line `%s'", buff);
    }
  free(buff);
}

/* Read from the stderr of the connected process as long as there
   remains data in the channel, and print each error.  Must be called
   from the parent process connected with Ispell by *THE_PIPE (created
   by `new_pipe').  */
#undef INITIAL_BUFF_SIZE
#define INITIAL_BUFF_SIZE   256

void
read_ispell_errors (pipe_t * the_pipe)
{
  struct timeval time_out;
  size_t buff_size = INITIAL_BUFF_SIZE;
  char *buff = xmalloc(sizeof(char[INITIAL_BUFF_SIZE]));
  ssize_t len;

  time_out.tv_sec = time_out.tv_usec = 0;

  while (select (FD_SETSIZE, &(the_pipe->error_set), NULL, NULL,
		 &time_out) == 1)
    {
       len = getline(&buff, &buff_size, the_pipe->fperr);
       if (len == -1) {
         if (feof(the_pipe->fperr))
	    /* Ispell closed its stderr.  */
	    error (EXIT_FAILURE, 0, "premature EOF from Ispell's stderr");
        else
            error(EXIT_FAILURE, errno, "error reading errors of ispell/aspell");
      }

      /* Strip the crlf.  */
      if (len > 1  &&  buff[len-1] == '\r'  ||  buff[len-1] == '\n') {
	if (len > 2  &&  buff[len-2] == '\r'  ||  buff[len-2] == '\n')
	    len -= 2;
	else
            len -= 1;
	buff[len] = 0;
      }
	
      if (!memcmp (buff, "Can't open ", strlen ("Can't open ")))
	error (EXIT_FAILURE, 0, "%s: cannot open",
	       buff + strlen ("Can't open "));

      fprintf (stderr, "%s: %s\n", ispell_prog, buff);
    }
  free(buff);
}

/* Create *THE_PIPE, setting up the file descriptors and streams, and
   activating the SIGPIPE handler.  */

void
new_pipe (pipe_t * the_pipe)
{
  int ifd[2];
  int ofd[2];
  int efd[2];

  if (signal (SIGPIPE, sig_pipe) == SIG_ERR)
    error (EXIT_FAILURE, errno, "error creating SIGPIPE handler");
  if (signal (SIGCHLD, sig_chld) == SIG_ERR)
    error (EXIT_FAILURE, errno, "error creating SIGCHLD handler");

  if (pipe (ifd) < 0)
    error (EXIT_FAILURE, errno, "error creating pipe to Ispell");
  the_pipe->pin = ifd[0];
  the_pipe->cout = ifd[1];
  the_pipe->fpin = fdopen(the_pipe->pin, "r");
  if (the_pipe->fpin == NULL)
    error (EXIT_FAILURE, errno, "error opening the pipe to Ispell"); 

  if (pipe (ofd) < 0)
    error (EXIT_FAILURE, errno, "error creating pipe to Ispell");
  the_pipe->cin = ofd[0];
  the_pipe->pout = ofd[1];

  if (pipe (efd) < 0)
    error (EXIT_FAILURE, errno, "error creating pipe to Ispell");
  the_pipe->perr = efd[0];
  the_pipe->cerr = efd[1];
  the_pipe->fperr = fdopen(the_pipe->perr, "r");
  if (the_pipe->fperr == NULL)
    error (EXIT_FAILURE, errno, "error opening the error pipe to Ispell");

  FD_ZERO (&(the_pipe->error_set));
  FD_SET (the_pipe->perr, &(the_pipe->error_set));
}

/* Handle the SIGPIPE signal.  */

static void
sig_pipe (int signo)
{
  error (EXIT_FAILURE, 0, "broken pipe");
}

/* Handle the SIGCHLD signal.  */

static void
sig_chld (int signo)
{
  error (EXIT_FAILURE, 0, "Ispell died");
}

/* Send lines to and retrieve lines from *THE_PIPE (created by
   `new_pipe').  Accept `argc' (the number of arguments) and `argv'
   (the array of arguments), so we can search for the files we are to
   read.  Handle all communication with Ispell at a managerial level;
   must be called by the parent process.  */

void
parent (pipe_t * the_pipe, int argc, char **argv)
{
  FILE *stream;
  char *file = NULL;
  int arg_error = 0;
  int arg_index = optind;

  /* Close the child's end of the pipes.  This is very important, as I
     found out the hard way.  */
  close (the_pipe->cin);
  close (the_pipe->cout);
  close (the_pipe->cerr);

  read_ispell_errors (the_pipe);

  /* This block parses Ispell's banner and grabs its version.  It then
     prints it if the flag `--ispell-version' or `-I' was used.
     FIXME: check that the version is high enough that it is going to
     be able to interact with GNU Spell sucessfully.  */
  {
    size_t buff_size = INITIAL_BUFF_SIZE;
    char *buff = xmalloc(sizeof(char[INITIAL_BUFF_SIZE]));
    ssize_t len;

    size_t ipos = 0;
    size_t fpos;

    len = getline(&buff, &buff_size, the_pipe->fpin);
    if (len == -1) {
      if (feof(the_pipe->fpin))
          error (EXIT_FAILURE, 0, "premature EOF from Ispell's stdout");
      else
          error(EXIT_FAILURE, errno, "error reading errors of ispell/aspell");
    }

    if (show_ispell_version) {
      for (; !isdigit (buff[ipos]) && ipos < len; ipos++);
      fpos = ipos;
      for (; buff[fpos] != ' ' && fpos < len; fpos++);
      buff[fpos] = 0;

      printf ("%s: Ispell version %s\n", program_name, buff+ipos);
      exit (EXIT_SUCCESS);
    }
    free(buff);
  }

  if (argc == 1)
    read_file (the_pipe, stdin, "-");

  while (arg_index < argc)
    {
      arg_error = 0;

      file = argv[arg_index];

      if (file[0] == '-' && file[1] == 0)
	{
	    read_stdin = 1;
	    stream = stdin;
	}
      else
	{
	  struct stat stat_buf;

	  if (stat (file, &stat_buf) == -1)
	    {
	      error (0, errno, "%s: stat error", file);
	      arg_index++;
	      continue;
	    }
	  if (S_ISDIR (stat_buf.st_mode))
	    {
	      error (0, 0, "%s: is a directory", file);
	      arg_index++;
	      continue;
	    }

	  stream = fopen (file, "r");
	  if (!stream)
	    {
	      error (0, errno, "%s: open error", file);
	      arg_error = 1;
	    }
	}

      if (!arg_error)
	read_file (the_pipe, stream, file);

      arg_index++;
    }
}

/* Execute the Ispell program after the fork.  Must be in the child
   process connected to the parent by *THE_PIPE (created by
   `new_pipe').  */

void
run_ispell_in_child (pipe_t * the_pipe)
{
  /* Close the parent side of the pipe.  */
  close (the_pipe->pin);
  close (the_pipe->pout);
  close (the_pipe->perr);

  if (the_pipe->cin != STDIN_FILENO)
    if (dup2 (the_pipe->cin, STDIN_FILENO) != STDIN_FILENO)
      error (EXIT_FAILURE, errno, "error duping to stdin");

  if (the_pipe->cout != STDOUT_FILENO)
    if (dup2 (the_pipe->cout, STDOUT_FILENO) != STDOUT_FILENO)
      error (EXIT_FAILURE, errno, "error duping to stdout");

  if (the_pipe->cerr != STDERR_FILENO)
    if (dup2 (the_pipe->cerr, STDERR_FILENO) != STDERR_FILENO)
      error (EXIT_FAILURE, errno, "error duping to stderr");

  if (dictionary != NULL)
    if (execlp (ispell_prog, "ispell", "-a", "-p", dictionary, NULL) < 0)
      if (errno != ENOENT  ||
	   execlp ("aspell", "aspell", "-a", "-p", dictionary, NULL) < 0)
	error (EXIT_FAILURE, errno, "error executing ispell/aspell");

  if (british)
    if (execlp (ispell_prog, "ispell", "-a", "-d", "british", NULL) < 0)
      if (errno != ENOENT  ||
	   execlp ("aspell", "aspell", "-a", "-d", "british", NULL) < 0)
        error (EXIT_FAILURE, errno, "error executing ispell/aspell");

  if (execlp (ispell_prog, "ispell", "-a", NULL) < 0)
    if (errno != ENOENT  ||
         execlp ("aspell", "aspell", "-a", NULL) < 0)
      error (EXIT_FAILURE, errno, "error executing ispell/aspell");
}

/* Return a NUL-terminated character string, the meaning of the error
   ERRNUM.  */

#ifndef HAVE_STRERROR
static char *
strerror (int errnum)
{
  extern char *sys_errlist[];
  extern int sys_nerr;

  if (errnum > 0 && errnum <= sys_nerr)
    return sys_errlist[errnum];
  return "Unknown system error";
}
#endif /* HAVE_STRERROR */

/* Print the program name and error message MESSAGE, which is a
   printf-style format string with optional args.  If ERRNUM is
   nonzero, print its corresponding system error message.  Exit with
   status STATUS if it is nonzero.  This function was written by David
   MacKenzie <djm@gnu.ai.mit.edu>.  */

static void
error (int status, int errnum, const char *message,...)
{
  va_list args;

  fflush (stdout);
  fprintf (stderr, "%s: ", program_name);

  va_start (args, message);
  vfprintf (stderr, message, args);
  va_end (args);

  if (errnum)
    fprintf (stderr, ": %s", strerror (errnum));
  putc ('\n', stderr);
  fflush (stderr);
  if (status)
    exit (status);
}

/* Allocate SIZE bytes of memory dynamically, with error checking,
   returning a pointer to that memory.  */

static void *
xmalloc (size_t size)
{
  void *ptr = malloc (size);

  if (!ptr)
    error (EXIT_FAILURE, errno, "virtual memory exhausted");
  return ptr;
}

/* Change the size of an allocated block of memory *PTR to SIZE bytes,
   with error checking, returning the new pointer.  If PTR is NULL,
   run `xmalloc'.  */

static void *
xrealloc (void *ptr, size_t size)
{
  if (!ptr)
    return xmalloc (size);
  ptr = realloc (ptr, size);
  if (!ptr)
    error (EXIT_FAILURE, errno, "virtual memory exhausted");
  return ptr;
}

static char *
xstrdup (const char *str)
{
  char *ptr = strdup (str);
  if (!ptr)
    error (EXIT_FAILURE, errno, "virtual memory exhausted");
  return ptr;
}
