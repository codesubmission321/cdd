#name: microMIPS BAL/JALX addend calculation (n64)
#source: ../../../gas/testsuite/gas/mips/branch-addend-micromips.s
#as: -EB -64 -march=from-abi
#ld: -EB -Ttext 0x1c000000 -e 0x1c000000
#objdump: -dr --prefix-addresses --show-raw-insn
#dump: bal-jalx-addend-micromips.d
