# coding: utf-8

from __future__ import print_function, unicode_literals
import os
import sys
import random
from fabfile import env


if len(sys.argv) <= 1:
    print('Usage: parallel <command>')
    sys.exit(-1)

command = sys.argv[1]


def block_split(lista, size):
    """
    >>> block_split([1,2,3], 2)
    [[1, 2], [3]]
    """
    return [
        lista[i:i + size]
        for i in xrange(0, len(lista), size)
    ]


HOW_MANY_ROLES_BY_WINDOW = 2
windows = block_split(env.roledefs.keys(), HOW_MANY_ROLES_BY_WINDOW)

fabric_bin = os.popen('which fab').read().strip()

MAX_SCREEN_WIDTH = 800
MAX_SCREEN_HEIGHT = 800

for i in windows:
    role = ','.join(i)
    command_line = '{} -R {} {}'.format(
        fabric_bin,
        role,
        command
    )
    x = random.randint(0, MAX_SCREEN_WIDTH)
    y = random.randint(0, MAX_SCREEN_HEIGHT)

    x_term_command = 'xterm -geometry +{}+{} -hold -e "{}" &'.format(
        x, y, command_line
    )
    os.popen(x_term_command)
