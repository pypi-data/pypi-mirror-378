#! /usr/bin/env python3
# SPDX-License-Identifier: MIT
#
# Copyright Red Hat
# Author: David Gibson <david@gibson.dropbear.id.au>
#
# selftest/cmplist.py - Compare files ignoring line order

import sys


def cmplist(name1, name2):
    l1 = frozenset(open(name1).readlines())
    l2 = frozenset(open(name2).readlines())

    if l1 == l2:
        sys.exit(0)

    d1 = [x.strip() for x in l1 - l2]
    if d1:
        print(f"In {name1} but not in {name2}: {d1}")

    d2 = [x.strip() for x in l2 - l1]
    if d2:
        print(f"In {name2} but not in {name1}: {d2}")

    sys.exit(1)


if __name__ == '__main__':
    cmplist(sys.argv[1], sys.argv[2])
