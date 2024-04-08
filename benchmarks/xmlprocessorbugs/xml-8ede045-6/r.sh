#! /bin/bash

QUERY='declare namespace UlCh ="ElotxYnNoUTttHK";declare namespace vaE ="ElotxYnNoUTttHK";declare namespace Rsp ="emBYhiGpnpGx";declare namespace CSD ="dItqGnZvHiRfoSsLR";declare namespace m ="tPeVOcxBnlJqxDKsRoCl";declare namespace Mb ="KFbdG";declare namespace DLxOO ="GbI";declare namespace YIb ="BmtbCeGoPjsXRNc";declare namespace vK ="urlinMZsLQEDbWGO";declare namespace iS ="rCwnqaKlfoNICnmLK";//*/(G29,/X14/P4/T7/Y20/O3/M1/C15/L2/J9/Y5/J7,F10)[((boolean(tail(reverse(reverse(R16/A12/R24)))) or lower-case(lower-case(namespace-uri-from-QName(. ! reverse(.)/node-name()))) ! (translate(., "of", "n5LR \ bVUR PfoC") castable as xs:string)) or has-children()) and ((@f3 ! boolean(count(.))) != true()) != true()]'
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


