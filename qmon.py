#!/usr/bin/env python
from __future__ import division
import time
from subprocess import check_output, Popen, PIPE
from os import system
import time
import argparse
from pyparsing import *
__author__ = 'tpoterba'


class Col:
    HEADER = '\033[95m'
    BRIGHTGREEN = '\033[92m'
    OKGREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BRTRED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PINK = '\033[95m'
    LBLUE = '\033[94m'
    TEAL = '\033[96m'
    GRAY = '\033[90m'


class Array:
    def __init__(self, ID, username, name, start):
        self.ID = ID
        self.username = username
        self.name = name
        self.run = 0
        self.wait = 0
        self.error = 0
        self.zombies = 0
        self.start = start
        self.queue = ''

    def tostring(self):
        if self.queue == 'long':
            queue = Col.LBLUE + 'long ' + Col.END
        elif self.queue == 'short':
            queue = Col.PINK + 'short' + Col.END
        else:
            queue = Col.GRAY + 'unkwn' + Col.END

        process = Popen("qstat -j %s | grep job-array | awk '{print $3}'" % self.ID,
                        shell=True,
                        stdout=PIPE, stderr=PIPE)
        out = process.communicate()[0].strip()
        out = out.split(':')

        elapsed = time.time() - time.mktime(self.start)
        timestr = convert_time(elapsed)
        try:
            step = float(out[1])
        except:
            return "%11s  %-8s  %-10s  %-12s  %4s %5s  %5s  %5s  %12s  \n%12s %s" % \
                   (self.ID, self.username, self.name, queue, int(self.run), int(self.wait),
                    int(self.error), int(self.zombies), timestr, '',
                    'JOB IS CURRENTLY DYING' + '_____________________________________________')
        minmax = map(int, out[0].split('-'))
        total = (minmax[1] - minmax[0])/step + 1.
        # print 'total is %d' % total
        todo = self.run + self.wait + self.error + self.zombies
        pct = (total - todo) / total * 100
        if todo > 0 and pct > 99.9:
            pct = 99.9
        # print "pct = %s" % pct
        boxes = int(pct / 4)
        # print boxes
        box_string = '['
        if self.error + self.zombies > 0:
            errorboxes = max(int(round(100. * (self.error + self.zombies) / total / 4)), 1)
        else:
            errorboxes = 0
        if self.run > 0:
            runboxes = max(int(round(100. * self.run / total / 4)), 1)
        else:
            runboxes = 0

        if self.wait == 0 and boxes + errorboxes + runboxes < 25:
            boxes += 1

        box_string += Col.RED
        for i in xrange(errorboxes):
            box_string += 'X'
        box_string += Col.END

        # box_string += Col.BOLD
        for i in xrange(boxes):
            box_string += '#'
        # box_string += Col.END

        box_string += Col.OKGREEN
        for i in xrange(runboxes):
            box_string += '='
        box_string += Col.END

        for i in xrange(25-boxes - errorboxes - runboxes):
            box_string += '-'
        box_string += ']'


        string = "%11s  %-8s  %-10s  %-12s  %4s %5s  %5s  %5s  %12s  \n%12s %s" % \
                 (self.ID, self.username, self.name, queue, int(self.run), int(self.wait),
                  int(self.error), int(self.zombies), timestr, '%.1f%%' % pct,
                  box_string + '________________________________________')
                               #'.............................................'
                               #'_____________________________________________'
        return string


def bold(string):
    return Col.BOLD + string + Col.END


def underline(string):
    return Col.UNDERLINE + string + Col.END


def color_load(load):
    if load >= 1.75:
        return Col.RED + '%.2f' % load + Col.END
    elif 1.50 < load < 1.75:
        return Col.BRTRED + '%.2f' % load + Col.END
    elif 1.00 < load <= 1.50:
        return Col.YELLOW + '%.2f' % load + Col.END
    else:
        return '%.2f' % load


def statusline(running, pending, errors, zombies):
    string = '%11s' % ''
    if running > 0:
        string += Col.OKGREEN + 'Running: %-5d  ' % running + Col.END
    else:
        string += Col.GRAY + 'Running: %-5d  ' % running + Col.END
    if pending > 0:
        string += Col.YELLOW + 'Pending: %-5d  ' % pending + Col.END
    else:
        string += Col.GRAY + 'Pending: %-5d  ' % pending + Col.END
    if errors > 0:
        string += Col.BRTRED + 'Errors: %-5d  ' % errors + Col.END
    else:
        string += Col.GRAY + 'Errors: %-5d  ' % errors + Col.END
    if zombies > 0:
        string += Col.RED + 'ZOMBIES: %-5d  ' % zombies + Col.END
    else:
        string += Col.GRAY + 'ZOMBIES: %-5d  ' % zombies + Col.END

    return string


def convert_time(seconds, day=True):
    days = seconds // (3600 * 24)
    seconds -= (3600 * 24) * days
    hours = seconds // 3600
    seconds -= (3600) * hours
    minutes = seconds // 60
    seconds = seconds % 60
    if day:
        return '%d:%02d:%02d:%02d' % (days, hours, minutes, seconds)
    else:
        return '%d:%02d:%02d' % (24*days + hours, minutes, seconds)


def calculate_load():
    # out = check_output('qstat -q short -f').split('\n')
    process = Popen('qstat -q short -f | grep "@"',
                    shell=True,
                    stdout=PIPE)
    out = process.communicate()[0].strip().split('\n')

    total = 0
    used = 0

    for line in out[1:]:
        line = line.split()
        f3 = map(int, line[2].split('/'))
        total += f3[2]
        used += f3[1]

    print 'TOTAL: %d, USED: %d, PCT: %.1f' % (total, used, float(used) / total * 100)


def parse_taskfield(field):
    count = 0
    for i in field.split(','):
        if '-' in i:
            i = i.split(':')
            delim = int(i[1])
            start, end = int(i[0].split('-')[0]), int(i[0].split('-')[1])
            count += (end - start) / delim + 1
        else:
            count += 1
    return count


def show(user):
    towrite = []
    try:
        cols = int(check_output(['tput', 'cols']).strip())
        lines = int(check_output(['tput', 'lines']).strip())
    except:
        print 'ERROR: cannot access terminal dimensions.  Run ssh session in -X or -Y mode.  ' \
              'Exiting.'
        exit()
        cols, lines = 0,0 # stupid IDE warning
    if lines < 15:
        print 'Not enough lines to show job output, please increase terminal size.'
        return
    process = Popen('qstat -u "%s"' % user,
                    shell=True,
                    stdout=PIPE)
    out = process.communicate()[0].strip().split('\n')[2:]

    interactive = []
    tasks = {}
    jobs = []

    for line in out:
        # print line
        # print line[49:68]
        # import ipdb
        # ipdb.set_trace()
        try:
            jobid = line[:11].strip()
            project = line[19:30].strip()
            username = line[30:42].strip()
            state = line[43:49].strip()
            queue = line[69:99].split("@")[0].strip()
            if queue != '':
                host = line[69:99].split("@")[1].split('.')[0]
            else:
                host = ''
            timefield = time.strptime(line[49:68], '%m/%d/%Y %H:%M:%S')
            taskfield = line[137:].strip()
        except:
            jobid = line[:11].strip()
            project = line[20:31].strip()
            username = line[31:43].strip()
            state = line[44:50].strip()
            queue = line[70:100].split("@")[0].strip()
            if queue != '':
                host = line[70:100].split("@")[1].split('.')[0]
            else:
                host = ''
            timefield = time.strptime(line[50:69], '%m/%d/%Y %H:%M:%S')
            taskfield = line[138:].strip()

        # parse task array
        if len(taskfield) > 0:
            if not jobid in tasks:
                tasks[jobid] = Array(jobid, username, project, timefield)
            if tasks[jobid].queue == '' and queue != '':
                tasks[jobid].queue = queue
            if state == 'r' or state == 't':
                tasks[jobid].run += parse_taskfield(taskfield)
            elif state == 'qw':
                tasks[jobid].wait += parse_taskfield(taskfield)
            elif 'd' in state:
                tasks[jobid].zombies += parse_taskfield(taskfield)
            elif 'E' in state:
                tasks[jobid].error += parse_taskfield(taskfield)

        # parse interactive job
        elif queue == 'interactive':
            interactive.append([jobid, username, project, state, host, timefield])
        else:
            jobs.append([jobid, username, project, state, queue, host, timefield])

    # import ipdb
    # ipdb.set_trace()
    divider = ''
    for i in xrange(80):
        divider += '-'
    breaker = ''
    for i in xrange(len(divider)):
        if i % 3 != 0:
            breaker += '.'
        else:
            breaker += ' '

    towrite.append('================================= ' +
                   Col.UNDERLINE + "QUEUE HEALTH" + Col.END +
                   ' =================================')
    out = check_output(['qstat', '-g', 'c']).strip().split('\n')
    queues = {}
    for line in out[2:]:
        line = line.split()
        queues[line[0]] = [float(line[1]), int(line[2]), int(line[4])]
    try:
        towrite.append(Col.PINK + '%20s' % 'Short' + Col.END + ': Load = %s, %d/%d nodes in use' %
                       (color_load(queues['short'][0]), queues['short'][1],
                        queues['short'][2] + queues['short'][1]))
        towrite.append(Col.LBLUE + '%20s' % 'Long' + Col.END + ': Load = %s, %d/%d nodes in use' %
                       (color_load(queues['long'][0]), queues['long'][1],
                        queues['long'][2] + queues['long'][1]))
        towrite.append(Col.TEAL + '%20s' % 'Interactive' + Col.END +
                       ': Load = %s, %d/%d nodes in use' %
                       (color_load(queues['interactive'][0]), queues['interactive'][1],
                        queues['interactive'][2] + queues['interactive'][1]))
    except KeyError:
        towrite.append(Col.RED + 'ERROR' + Col.END + ': something went wrong in <qstat -g c>')

    if len(tasks) > 0:
        towrite.append('================================= ' +
                       Col.UNDERLINE + "TASK ARRAYS" + Col.END +
                       ' ==================================')
        running = sum([i.run for i in tasks.values()])
        pending = sum([i.wait for i in tasks.values()])
        zombies = sum([i.zombies for i in tasks.values()])
        errors = sum([i.error for i in tasks.values()])
        towrite.append(statusline(running, pending, errors, zombies))
        towrite.append(divider)
        towrite.append("%19s  %-16s  %-18s  %-13s   %11s  %s  %s   %s  %16s" % \
              (underline('Job ID'), underline('Username'), underline('Project'),
               underline('Queue'), underline('RUN'),
               underline('PEND'), underline('ERROR'), underline('ZOMB'),
               underline('Time Elapsed')))
        for task in sorted(tasks.values(),
                           key=lambda i: -1 * (10**15 * i.run + 10**10 * i.wait) + int(i.ID)):
            if len(towrite) + 15 >= lines:
                towrite.append(breaker)
                break
            towrite.append(task.tostring())
            # towrite.append('')
            # import ipdb
            # ipdb.set_trace()
        towrite.append('')
    if len(interactive) > 0:
        towrite.append('================================= ' +
                       Col.UNDERLINE + "INTERACTIVE" + Col.END +
                       ' ==================================')
        interactive = sorted(interactive, key=lambda i: -time.mktime(i[5]))
        running = sum([1 for i in interactive if i[3] == 'r'])
        pending = sum([1 for i in interactive if i[3] == 'qw' or i[3] == 't'])
        zombies = sum([1 for i in interactive if 'd' in i[3]])
        errors = sum([1 for i in interactive if 'E' in i[3]])
        towrite.append(statusline(running, pending, errors, zombies))
        towrite.append(divider)
        towrite.append("%19s  %-16s  %-18s  %s    %s           %s   %s" % \
                       (underline('Job ID'), underline('Username'), underline('Project'),
                        underline('Queue'), underline('Host'), underline('Status'),
                        underline('Time Elapsed')))
        for job in interactive:
            if len(towrite) + 9 >= lines:
                towrite.append(breaker)
                break
            if job[3] == 'r':
                status = Col.OKGREEN + 'RUN    ' + Col.END
            elif job[3] == 'qw':
                status = Col.YELLOW + 'PEND  ' + Col.END
            elif 'd' in job[3]:
                status = Col.RED + 'ZOMBIE' + Col.END
            else:
                status = Col.RED + job[3] + Col.END

            timestr = convert_time(time.time() - time.mktime(job[5]), day=False)
            if 30 < int(timestr.split(':')[0]) < 36:
                timestr = Col.BRTRED + timestr + Col.END
            elif int(timestr.split(':')[0]) > 36:
                timestr = Col.RED + timestr + Col.END
            else:
                timestr = Col.RED + Col.END + timestr

            towrite.append("%11s  %-8s  %-10s  %s    %-12s   %-17s   %19s" % \
              (job[0], job[1], job[2],
               Col.TEAL + 'inter' + Col.END, job[4], status, timestr))
        towrite.append('')

    if len(jobs) > 0:
        jobs = sorted(jobs, key=lambda i: int(i[0]))
        towrite.append('================================== ' +
                       Col.UNDERLINE + "OTHER JOBS" + Col.END +
                       ' ==================================')
        running = sum([1 for i in jobs if i[3] == 'r'])
        pending = sum([1 for i in jobs if i[3] == 'qw' or i[3] == 't'])
        zombies = sum([1 for i in jobs if 'd' in i[3]])
        errors = sum([1 for i in jobs if 'E' in i[3]])
        towrite.append(statusline(running, pending, errors, zombies))
        towrite.append(divider)
        towrite.append("%19s  %-16s  %-18s  %s    %s           %s   %s" % \
              (underline('Job ID'), underline('Username'), underline('Project'),
               underline('Queue'), underline('Host'), underline('Status'),
               underline('Time Elapsed')))
        for job in jobs:
            if len(towrite) + 2 >= lines:
                towrite.append(breaker)
                break
            if job[3] == 'r':
                status = Col.OKGREEN + 'RUN' + Col.END
            elif job[3] == 'qw':
                status = Col.YELLOW + 'PEND' + Col.END
            elif 'd' in job[3]:
                status = Col.RED + 'ZOMBIE' + Col.END
            else:
                status = Col.BRTRED + job[3] + Col.END
            timestr = convert_time(time.time() - time.mktime(job[6]), day=False)
            timestr = Col.RED + Col.END + timestr

            if job[4] == 'short':
                queue = Col.PINK + 'short' + Col.END
            elif job[4] == 'long':
                queue = Col.LBLUE + 'long ' + Col.END
            else:
                queue = Col.GRAY + 'unkwn' + Col.END

            towrite.append("%11s  %-8s  %-10s  %s    %-12s   %-17s   %19s" % \
                  (job[0], job[1], job[2],
                   queue, job[5], status, timestr))


    # return [i[:cols] for i in towrite]
    return towrite


def main(args):
    if args.user is None:
        args.user = check_output('whoami').strip()
    if args.window:
        import os
        import sys
        while True:
            towrite = show(args.user)
            os.system('clear')
            for index, i in enumerate(towrite):
                if not index + 1 == len(towrite):
                    print i
                else:
                    sys.stdout.write(i)
                    sys.stdout.flush()
            time.sleep(args.delay)
    else:
        towrite = show(args.user)
        for i in towrite:
            print i

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--window', help='Run in a self-refreshing window', action='store_true')
    parser.add_argument('-u', '--user',
                        type=str,
                        help='Look at data from another user')
    parser.add_argument('-d', '--delay', type=int,
                        help='Set refresh delay (default: 3s)', default=3)
    args = parser.parse_args()
    main(args)