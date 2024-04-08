#! /bin/bash

QUERY='declare namespace DN ="TvoChsKBkMWrJ";declare namespace mR ="AqwLyZ";declare namespace MVjLa ="IrWcpQqbLXBwf";declare namespace eXf ="gJnSxNvKfBlig";declare namespace K ="bRwdUFNzN";declare namespace UcR ="YUzAKblGljQDr";declare namespace AdS ="TvoChsKBkMWrJ";declare namespace H ="cYNYoItjr";declare namespace CuWJo ="Dwqujoqsa";declare namespace RymwF ="AqwLyZ";declare namespace jOAI ="IrWcpQqbLXBwf";declare namespace dnWz ="XKhDuT";declare namespace z ="ezBvEILsj";//*/(/B12/L1/X10/J14,/B12/L1/X10/T30)[(not(head(subsequence(node-name(), 67)) castable as xs:string) and boolean(abs(last() mod -3219548281))) and (reverse(. = <A>2</A>) or not(((head(@f14) ! starts-with(., "y@:Sc.M(r{o{ChZAkOL83_Q J@F")) = false()) = true()))]'
GOOD_VERSION="8ede045"
BAD_VERSION="d917ae0"

echo $QUERY > query.xq

# run saxon
target_saxon="saxon"
java -cp '/home/coq/cdd/benchmarks/xmlprocessorbugs/lib/saxon-he-12.4.jar:/home/coq/cdd/benchmarks/xmlprocessorbugs/lib/xmlresolver-5.2.0/lib/*' net.sf.saxon.Query -s:./input.xml -q:./query.xq > ${target_saxon}_raw_result.xml 2>&1
ret=$?

if [ $ret != 0 ]; then
  exit 1
fi

# run basex_bad
target_basex_bad="basex_bad"
java -cp "/home/coq/cdd/benchmarks/xmlprocessorbugs/lib/basex-${BAD_VERSION}.jar" org.basex.BaseX -i input.xml query.xq > ${target_basex_bad}_raw_result.xml 2>&1
ret=$?

if [ $ret != 0 ]; then
  exit 1
fi

# run basex_good
target_basex_good="basex_good"
java -cp "/home/coq/cdd/benchmarks/xmlprocessorbugs/lib/basex-${GOOD_VERSION}.jar" org.basex.BaseX -i input.xml query.xq > ${target_basex_good}_raw_result.xml 2>&1
ret=$?

if [ $ret != 0 ]; then
  exit 1
fi

# process saxon result
grep -o 'id="[^"]*"' ${target_saxon}_raw_result.xml | sed 's/id="//g' | sed 's/"//g' | grep -v '^[[:space:]]*$' > ${target_saxon}_processed_result.txt

# process basex_bad result
grep -o 'id="[^"]*"' ${target_basex_bad}_raw_result.xml | sed 's/id="//g' | sed 's/"//g' | grep -v '^[[:space:]]*$' > ${target_basex_bad}_processed_result.txt

# process basex_good result
grep -o 'id="[^"]*"' ${target_basex_good}_raw_result.xml | sed 's/id="//g' | sed 's/"//g' | grep -v '^[[:space:]]*$' > ${target_basex_good}_processed_result.txt


# diff, files should be different
if diff ${target_saxon}_processed_result.txt ${target_basex_bad}_processed_result.txt > /dev/null 2>&1; then
    exit 1
fi

# diff, files should be same
if ! diff ${target_saxon}_processed_result.txt ${target_basex_good}_processed_result.txt > /dev/null 2>&1; then
    exit 1
fi

exit 0


