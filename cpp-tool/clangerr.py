#!/usr/bin/env python3

import argparse
import collections
import re
import os

ErrorItem = collections.namedtuple('ErrorItem', ['path', 'line', 'col', 'msg'])


def load_error_items(file):
    # path:line:col: error: msg
    re_error = re.compile(r'(.+)\:(\d+)\:(\d+)\: error\: (.+)')
    items = []
    with open(file, 'rt') as f:
        for line in f:
            l = line.strip()
            mo = re_error.match(l)
            if mo:
                items.append(ErrorItem(mo[1], int(mo[2]), int(mo[3]), mo[4]))
    return items


def process_error_items(args, error_items):
    for e in error_items:
        # add (void) in front line to suppress `warn_unused_result` warning
        if 'warn_unused_result' in e.msg or 'unused-value' in e.msg:
            path = os.path.join(args.base, e.path)
            with open(path, 'rt') as f:
                lines = f.readlines()
                l = lines[e.line - 1]
                idx = len(l) - len(l.lstrip())
                new_l = l[:idx] + '(void)' + l[idx:]
                lines[e.line - 1] = new_l
            with open(path, 'wt') as f:
                f.write(''.join(lines))


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('file', help='Path to the error file')
parser.add_argument('--base', default='./', help='Base directory')


def main():
    args = parser.parse_args()
    error_items = load_error_items(args.file)
    process_error_items(args, error_items)


if __name__ == '__main__':
    main()