# -*- coding: utf-8 -*-
#
# this file is part of the SDCA project (team 11)
#

from Work import RED, START_TIME, END_TIME
import sys

def main(result_file):
    with open(result_file, 'a+') as stream:
        duration = float(RED.get(END_TIME)) - float(RED.get(START_TIME))
        stream.write(str(duration) + "\n")

if __name__ == '__main__':
    main(sys.argv[1])
