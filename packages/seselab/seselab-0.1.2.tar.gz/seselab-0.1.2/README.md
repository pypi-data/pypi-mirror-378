SeseLab: a software platform for teaching physical attacks
==========================================================

Anyone following computer security related news will agree that it is important to teach a minimum of security to computer science students,
and that at least the existence of side channel attacks is part of this strict minimum that they should be aware of.

The toolset required for carrying out a side channel attack is costly and bulky,
and its usage requires specific training that most computer science students do not have.

SeseLab is a software platform that can be used in any computer room where Python 3 is installed.
It allows students to simulate physical attacks (e.g., Simple Power Analysis and BellCoRe) on cryptographic implementations.

To achieve this goal, SeseLab simulates a simple CPU (e.g., there is no cache) that uses a simplified assembly language which can be learned and used over the course of a lab session.

SeseLab is distributed with a bignum library written in this assembly language which can be used to implement cryptographic primitive such as a square-and-multiply algorithm for modular exponentiation.

## Installation

You can either install SeseLab from [PyPI](https://pypi.org/project/seselab/) using pip with the following command:

    $ pip3 install seselab

Or you can download its [source code](https://code.up8.edu/pablo/seselab) and run the following command in the root directory of the repository:

    $ pip3 install .

## Usage

You can call the `seselab` tool either directly or with `python3 -m seselab`.

## SeseLab assembly language

An 8-bits Harvard architecture is simulated.

There are 32 registers and 1M memory cells.

Register 31 is used for return address, and register 30 is used for stack pointer.

There are 25 instructions:

* `nop`: does nothing;
* `mov dst val`: copies the value of `val` in `dst`;
* `not dst val`: writes the bitwise negation of `val` in `dst`;
* `and dst val1 val2`: writes the bitwise logical and of `val1` and `val2` in `dst`;
* `orr dst val1 val2`: writes the bitwise logical or of `val1` and `val2` in `dst`;
* `xor dst val1 val2`: writes the bitwise exclusive or of `val1` and `val2` in `dst`;
* `lsl dst val1 val2`: writes `val1` shifted by `val2` bits to the left in `dst`;
* `lsr dst val1 val2`: writes `val1` shifted by `val2` bits to the right in `dst`;
* `min dst val1 val2`: writes the smallest of `val1` and `val2` in `dst`;
* `max dst val1 val2`: writes the bigest of `val1` and `val2` in `dst`;
* `add dst val1 val2`: writes the sum of `val1` and `val2` in `dst`;
* `sub dst val1 val2`: writes the difference of `val1` and `val2` in `dst`;
* `mul dst val1 val2`: writes the product of `val1` and `val2` in `dst`;
* `div dst val1 val2`: writes the quotient of `val1` devided by `val2` in `dst`;
* `mod dst val1 val2`: writes the remainder of `val1` devided by `val2` in `dst`;
* `ret`: jumps to the instruction pointed to by register `r31`;
* `cal addr`: write next instruction index in `r31` then jumps to `addr`;
* `cmp dst val1 val2`: writes 1 in `dst` if `val1` < `val2`, -1 if `val1` > `val2`, 0 otherwise;
* `jmp addr`: jumps to `addr`
* `beq addr val1 val2`: jumps to `addr` if `val1` = `val2`;
* `bne addr val1 val2`: jumps to `addr` if `val1` ≠ `val2`;
* `prn val`: prints the decimal value of `val`;
* `prx val`: prints the hexadecimal value of `val`;
* `prc val`: prints the ASCII character of value `val`;
* `prs addr val`: prints the string starting at address `addr` and of length `val`.

The values (`val`, `val1`, `val2`) are either :

* an immediate value, written `#N`: `#13`, `#42`, `#51`, etc. ;
* a register, written `rN`: `r0`, `r1`, …, `r31` ;
* a memory cell, written `@N`: `@0`, `@1`, etc. ;
* a dereferenced pointer, written `!val`: `!r2`, `!@100`, etc. (note that `!#93` is the same as `@93`) ;
* this last notation also accept an offset, written after a comma: `!r12,#-3`, `!r12,r2`, etc.

Valid destinations (`dst`) are writable values, i.e., any of the above except for immediate values.

An adress (`addr`) is either a value, in which case it corresponds to the instruction index in the code, or as a label.
Labels can be defined anywhere using the `label:` syntax and their value is the index of the instruction that immediately follows the label definition.

There are two additional instructions:

* `.use bignum` which loads the packaged bignum library;
* `.include file.asm` which loads `file.asm`.
