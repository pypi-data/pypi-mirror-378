import sys
import signal
from random import randint
from .compiler import Compiler
from .cpu import CPU

def usage ():
    print('Usage: seselab [-i] <code.asm> [power.log]')
    print(' * -i:        enable fault injection during execution if present')
    print(' * code.asm:  file with seselab assembly code to execute')
    print(' * power.log: file where to output simulated power consumption '
          + '(default to /dev/null)')
    sys.exit(1)

def main ():
    if len(sys.argv) < 2:
        usage()
    fault = sys.argv[1] == '-i'
    if fault:
        sys.argv.pop(1)
        if len(sys.argv) < 2:
            usage()
    asmcode = sys.argv[1]
    powerlog = '/dev/null' if len(sys.argv) < 3 else sys.argv[2]
    program = Compiler().run(asmcode)
    cpu = CPU(1048576, 32, program, powerlog)

    def inject (sig, frame):
        where = input('\n> Inject fault? (r = fault register, s = skip instruction, q = quit) ')
        if where == 'q':
            sys.exit(0)
        elif where == 's':
            skip = int(input('> How many instruction to skip? '))
            cpu._ip += skip
            print('! ' + str(skip) + ' instructions skipped')
        elif where == 'r':
            reg = int(input('> Which register? (0-'+str(cpu._reg._size - 1)+') '))
            what = input('> Zero or random? (z = zero, r = random) ')
            if what == 'z':
                cpu._reg._mem[reg] = 0
                print('! r' + str(reg) + ' zeroized')
            elif what == 'r':
                cpu._reg._mem[reg] = randint(0, cpu._ram._size)
                print('! r' + str(reg) + ' randomized')
        print('> Resuming…')

    if fault:
        signal.signal(signal.SIGINT, inject)
    else:
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    cpu.run()
