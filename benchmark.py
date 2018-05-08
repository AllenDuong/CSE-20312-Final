#!/usr/bin/env python3

from subprocess import call

call(['time valgrind --leak-check-full ./final']
