#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

import sys, traceback
from subprocess import Popen, PIPE

PASS = 'aT2n9EZdZm7fZ8p5'

def connect():
    command = ['net', 'use', 'z:', '\\\\dc-01.vimec.priv\\data', '/USER:build_server', PASS]
    p = Popen(command,
              stdout=PIPE,
              stderr=None,
              stdin=PIPE,
              universal_newlines=True)
    stdout, _ = p.communicate()
    print("output of " + "(ret_val:" + str(p.returncode) + "):\n " + stdout)
    if p.returncode != 0:
        sys.exit(p.returncode)

def main():
    connect()

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(1)
