#!/usr/bin/python3

"""
Usage: find-deps.py <binary> [<binary> ...]

Finds (pacman/ALPM) dependencies for a binary or set of binaries based
on dynamically linked libraries.

"""

import sys
import os
import subprocess
import re

def subprocess_get_lines(args, fail_okay=False):
    try:
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        if fail_okay:
            output = e.output
        else:
            raise
    return output.decode().splitlines()

# Get the filenames of the libs we need
del os.environ['LD_LIBRARY_PATH'], os.environ['LD_PRELOAD'] # otherwise fakeroot will interfere
ldd_output = subprocess_get_lines(['ldd'] + sys.argv[1:])
regex = re.compile(r' => (.*) \(0x[0-9a-f]+\)$')
libs = set(match.group(1) for match in map(regex.search, ldd_output) if match)

# Figure out which packages own them
deps = set(subprocess_get_lines(
    ['pacman', '--query', '--owns', '--quiet'] + list(libs),
    fail_okay=True
))

# 替換具體的包名為虛擬提供者（Virtual Provides）
# 將 jack2 替換為 jack，這樣本地不論是用 pipewire-jack 還是 jack2 都可滿足依賴
if 'jack2' in deps:
    deps.remove('jack2')
    deps.add('jack')

# Remove redundant dependencies
needed = set(deps)
for pkg in deps:
    if pkg not in needed:
        continue # this subtree has already been pruned

    # 如果是虛擬依賴 (如 jack)，pactree 無法直接展開，跳過遞歸修剪
    if subprocess.run(['pacman', '-Si', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        continue

    redundant = subprocess_get_lines(
        ['pactree', '--unique', pkg]
    )[1:] # first line is pkg itself
    needed.difference_update(redundant)

print(' '.join(sorted(needed)))
