# -*- coding: utf-8 -*-
#
# this file is part of the SDCA project (team 11)
#

"""
This module allows a user to fetch the last execution time of a
makefile

Please make sure the execution actually ended before running this
"""

from work import RED, START_TIME, END_TIME
import sys

def main(result_file):
    """
    Appends the last execution time of a makefile to ``result_file``

    Please make sure the execution actually ended before running this
    """
    with open(result_file, 'a+') as stream:
        duration = float(RED.get(END_TIME)) - float(RED.get(START_TIME))
        stream.write(str(duration) + "\n")

if __name__ == '__main__':
    main(sys.argv[1])
