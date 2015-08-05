#!/usr/bin/env python
from __future__ import division
import subprocess
__author__ = 'tpoterba'


class Col:
    HEADER = '\033[95m'
    BRIGHTGREEN = '\033[92m'
    OKGREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class User:
    def __init__(self, name):
        self.name = name
        self.running = 0
        self.waiting = 0
        self.errors = 0
        self.mem = 0.
        self.io = 0.
        self.cpu = 0.

    def tostring(self):

        out = ""

        out += "%15s   " % self.name
        out += "%-9s" % self.running
        out += "%-9s" % self.waiting
        # if self.errors > 100 + 2*self.running + 2*self.waiting:
        #     out += "%-18s" % (Col.FAIL + str(self.errors) + Col.ENDC)
        # else:
        out += "%-9s" % self.errors

        if self.mem + self.io + self.cpu > 0:
            out += "%12s" % self.get_cpu()
            out += "%12s" % ("%.1f" % self.mem)
            out += "%12s" % ("%.1f" % self.io)
        else:
            out += "%36s" % ''

        # if self.errors > 100 + 2 * self.running + 2 * self.waiting:
        #     # out += "     poor life choices"
        #     pass
        return out

    def get_cpu(self):
        out = ''
        cpu = self.cpu
        out += '%d:' % (cpu // 3600)
        cpu = cpu % 3600.
        out += '%02d:' % (cpu // 60)
        cpu = cpu % 60.
        out += '%02d' % (cpu)
        return out

    def count(self):
        return self.running + self.waiting + self.errors

if __name__ == '__main__':
    process = subprocess.Popen("qstat -u \"*\" -ext -g d | grep broad",
                               shell=True,
                               stdout=subprocess.PIPE,
                               )
    stdout_list = process.communicate()[0].strip().split('\n')

    username = subprocess.check_output('whoami').strip()

    people = {}
    for line in stdout_list:
        if "interactive@" in line:
            continue
        line = line.split()
        user = line[4]
        state = line[7]
        if user not in people:
            people[user] = User(user)

        if state == 'r':
            nodes = int(line[18])
            people[user].running += nodes
            cpu = line[8]
            mem = line[9]
            io = line[10]
            try:
                if not cpu == 'NA':
                    cpu_split = cpu.split(":")
                    cpu_split = map(int, cpu_split)
                    people[user].cpu += cpu_split[0] * 24*3600 + cpu_split[1] * 3600 \
                                        + cpu_split[2] * 60 + cpu_split[3]

                if not mem == 'NA':
                    people[user].mem += float(mem)
                if not io == 'NA':
                    people[user].io += float(io)
            except:
                pass
        elif state == 'qw' or state == 't':
            people[user].waiting += 1
        elif 'E' in state or 'd' in state:
            people[user].errors += 1
        else:
            continue
        # if state == 'qw' or state == 'h' or state == 'E':

    # sorted_list = sorted([person for person in people.values()],
    #                      key=lambda i: -1*(i.running + i.waiting))
    sorted_list = sorted([person for person in people.values()],
                         key=lambda i: -1*(i.running))

    # header line
    print "%23s   %-18s%-18s%-18s%20s%20s%20s" % (Col.UNDERLINE + 'USERNAME' + Col.ENDC,
                                                  Col.OKGREEN + 'RUNNING' + Col.ENDC,
                                                  Col.WARNING + 'PENDING' + Col.ENDC,
                                                  Col.FAIL + 'ERRORS' + Col.ENDC,
                                                  Col.BOLD + 'CPU' + Col.ENDC,
                                                  Col.BOLD + 'MEM' + Col.ENDC,
                                                  Col.BOLD + 'IO' + Col.ENDC)
    space = ''
    for i in xrange(82):
        space += '-'
    print space
    run = 0
    pend = 0
    err = 0

    STOP_AFTER = 40

    for num, person in enumerate(sorted_list):
        run += person.running
        pend += person.waiting
        err += person.errors
        if person.count() > 1:
            if person.name == username:
                print Col.BRIGHTGREEN + person.tostring() + Col.ENDC
            else:
                if not num >= STOP_AFTER:
                    print person.tostring()
    print space
    print "%23s   %-18s%-18s%-18s" % (
        Col.UNDERLINE + 'TOTAL' + Col.ENDC,
        Col.OKGREEN + str(run) + Col.ENDC,
        Col.WARNING + str(pend) + Col.ENDC,
        Col.FAIL + str(err) + Col.ENDC)


