#!/usr/bin/env python3
import sys
import threading


def pipe(a, b):
    append_quote_sign = True

    if isinstance(a, str):
        a = open(a, 'r')

    if isinstance(b, str):
        b = open(b, 'w')
        append_quote_sign = False

    for line in a:
        b.write('> ' + line if append_quote_sign else line)
        b.flush()


if __name__ == '__main__':
    assert len(sys.argv) == 3
    threading.Thread(target=pipe, args=(sys.argv[1], sys.stdout), daemon=False).start()
    pipe(sys.stdin, sys.argv[2])
