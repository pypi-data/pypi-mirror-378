#! /usr/bin/env python3
# SPDX-License-Identifier: MIT
#
# Copyright Red Hat
# Author: David Gibson <david@gibson.dropbear.id.au>
#
# selftest/checklist.py - Check --list output against expected pass+fail lists

import sys


def checklist(actual, xpass, xfail):
    lactual = frozenset(open(actual).readlines())
    lxpass = frozenset(open(xpass).readlines())
    lxfail = frozenset(open(xfail).readlines())

    inter = lxpass.intersection(lxfail)
    if inter:
        print(f"{inter} in both expected pass and fail list", file=sys.stderr)
        sys.exit(99)

    lx = lxpass.union(lxfail)
    if lactual == lx:
        sys.exit(0)

    da = [x.strip() for x in lactual - lx]
    if da:
        print(f"In {actual} but not in {xpass} or {xfail}: {da}")

    dpass = [x.strip() for x in lxpass - lactual]
    if dpass:
        print(f"In {xpass} but not in {actual}: {dpass}")

    dfail = [x.strip() for x in lxfail - lactual]
    if dfail:
        print(f"In {xfail} but not in {actual}: {dfail}")
    sys.exit(1)


if __name__ == '__main__':
    checklist(sys.argv[1], sys.argv[2], sys.argv[3])
