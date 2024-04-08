all: dep bzip2 chown date grep gzip mkdir rm sort tar uniq

dep:
	# build the dependencies
	make -C /home/coq/cdd/benchmarks/debloating/lib

bzip2:
	clang-7 -w bzip2-1.0.5/bzip2-1.0.5.c -o bzip2-1.0.5/bzip2-1.0.5.origin

chown:
	clang-7 -w chown-8.2/chown-8.2.c -o chown-8.2/chown-8.2.origin

date:
	clang-7 -w date-8.21/date-8.21.c -o date-8.21/date-8.21.origin

grep:
	clang-7 -w grep-2.19/grep-2.19.c -o grep-2.19/grep-2.19.origin "-D __msan_unpoison(s,z)" -lpcre

gzip:
	clang-7 -w gzip-1.2.4/gzip-1.2.4.c -o gzip-1.2.4/gzip-1.2.4.origin

mkdir:
	clang-7 -w mkdir-5.2.1/mkdir-5.2.1.c -o mkdir-5.2.1/mkdir-5.2.1.origin

rm:
	clang-7 -w rm-8.4/rm-8.4.c -o rm-8.4/rm-8.4.origin

sort:
	clang-7 -w sort-8.16/sort-8.16.c -o sort-8.16/sort-8.16.origin -pthread

tar:
	clang-7 -w tar-1.14/tar-1.14.c -o tar-1.14/tar-1.14.origin

uniq:
	clang-7 -w uniq-8.16/uniq-8.16.c -o uniq-8.16/uniq-8.16.origin

clean:
	find . -type f -name '*.origin' -delete
	find . -type f -name '*.a' -delete
