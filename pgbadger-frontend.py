#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import logging
import datetime
from dateutil import parser

argp = \
    argparse.ArgumentParser(description='Gets logs from a machine, parses with pgbadger and opens in browser. Basic usage: python pgbadger-frontend.py -h export -i export -b 2d'
                            , add_help=False)
argp.add_argument('-h', '--host', dest='host', required=True)
argp.add_argument('-i', '--instance', dest='instance', required=True)
argp.add_argument('-v', '--version', dest='version', default='9.?')  # by default all versions are parsed
argp.add_argument('-b', '--begin', dest='begin_date', default=datetime.datetime.now().strftime('%Y-%m-%d 00:00:00'))  # 2d, 2h or 2014-02-28 14:57:47
argp.add_argument('-e', '--end', dest='end_date', default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
argp.add_argument('-l', '--log-dir', dest='log_dir', action='store_true',
                  default='/data/postgres/pgsql_{instance}/{version}/data/pg_log/')
# argp.add_argument('-l', '--log-dir', dest='log_dir', action='store_true', default='/var/lib/postgresql/{version}/{instance}/pg_log/')
argp.add_argument('-d', '--debug', dest='verbose', action='store_true', default=False)
args = argp.parse_args()

BROWSERS = ['firefox', 'chromium-browser']

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger()
logger.setLevel((logging.INFO if args.verbose else logging.WARNING))


def shell_exec(shell_command):
    exitcode = subprocess.call(shell_command, shell=True)
    if exitcode != 0:
        logger.error('error executing: %s', shell_command)
    return exitcode


def shell_exec_with_output(shell_command):
    process = subprocess.Popen(shell_command.split(), stdout=subprocess.PIPE)
    exitcode = process.wait()
    if exitcode != 0:
        logger.error('error executing: %s', shell_command)
    return exitcode, process.stdout.read().strip()


def interval_to_date(time_interval):
    now = datetime.datetime.now()
    interval_unit = time_interval[-1].lower()
    interval_value = int(time_interval[0:-1])
    delta = None
    if interval_unit == 'h':
        delta = datetime.timedelta(hours=interval_value)
    elif interval_unit == 'd':
        delta = datetime.timedelta(days=interval_value)
    elif interval_unit == 'm':
        delta = datetime.timedelta(minutes=interval_value)
    return (now - delta).strftime('%Y-%m-%d %H:%M:%S')


def copy_remote_files_to_local_dir(from_date, until_date, local_folder):
    # TODO getting full days only for now. one could use "find -ctime x -type f"
    files = []
    remote_log_folder = args.log_dir.format(version=args.version, instance=args.instance)  # /var/lib/postgresql/{}/{}/pg_log/
    ls_cmd = '''ssh postgres@{host} ls {remotedir}postgresql-{date}_*.csv'''
    copy_cmd = '''rsync -az postgres@{host}:{logfile} {local_folder}'''
    logger.info('scanning for log files from %s to %s in %s', from_date, until_date, remote_log_folder)
    from_day = parser.parse(from_date)
    from_day.replace(hour=0, minute=0, second=0)
    until_day = parser.parse(until_date)  # + datetime.timedelta(days=1)
    while from_day <= until_day:
        logger.info('fetching logs for %s', from_day)
        cmd = ls_cmd.format(remotedir=remote_log_folder, date=from_day.strftime('%Y-%m-%d'), host=args.host)
        ret, msg = shell_exec_with_output(cmd)
        if ret != 0:
            logger.error('listing of logs failed. cmd : %s', cmd)
            exit()
        days_files = msg.split()
        for file in days_files:
            files.append(os.path.join(local_folder, os.path.split(file)[1]))
            logger.warning('fetching %s', file)
            cmd = copy_cmd.format(logfile=file, local_folder=local_folder, host=args.host)
            ret, msg = shell_exec_with_output(cmd)
            if ret != 0:
                logger.error('fetching logs failed. cmd : %s', cmd)
                exit()
        from_day = from_day + datetime.timedelta(days=1)
    return files


if __name__ == '__main__':
    logger.info('connecting to %s...', args.host)
    ret, msg = shell_exec_with_output('ssh postgres@{} date'.format(args.host))
    if ret != 0:
        logger.error('connect failed: {}', msg)
        exit()

    ret, pgbadger_path = shell_exec_with_output('which pgbadger')
    if ret != 0:
        logger.error('pgbadger not found on $PATH')
        exit()
    local_folder = os.path.split(pgbadger_path)[0] + '/downloads/' + args.host

    logger.info('ensuring download folder existance : %s', local_folder)
    ret, msg = shell_exec_with_output('mkdir -p ' + local_folder)
    if ret != 0:
        logger.error('failed to create path %s : %s', local_folder, msg)
        exit()

    from_date = args.begin_date
    if from_date[-1] in ('d', 'm', 'h'):
        from_date = interval_to_date(args.begin_date)
    elif len(from_date) == 10:
        from_date += ' 00:00:00'
    until_date = args.end_date
    if len(until_date) == 10:
        until_date += ' 00:00:00'
    if len(from_date) not in (10, 19) or len(until_date) not in (10, 19):  # input must be in format of 2014-03-02 or 2014-03-03 09:28:11
        logger.error('invalid input datetimes: %s, %s', from_date, until_date)
        exit()

    files = copy_remote_files_to_local_dir(from_date, until_date, local_folder)

    # call pgbadger
    outfile = 'pgbadger_{}_{}_{}-{}.html'.format(args.host, args.instance, from_date[5:7] + from_date[8:10],
                                                 until_date[5:7] + until_date[8:10])
    call_cmd = pgbadger_path + ' -o ' + outfile + ' -f csv -b "' + from_date + '" -e "' + until_date + '" '
    call_cmd += ' '.join(files)
    logger.info('executing: %s', call_cmd)
    ret = shell_exec(call_cmd)
    if ret != 0:
        logger.error('pgbadger call failed: %s', msg)
        exit()

    # open brower
    for b in BROWSERS:
        ret, browser_path = shell_exec_with_output('which ' + b)
        if ret == 0:
            logger.warning('starting the browser: %s', browser_path + ' ' + outfile)
            ret = shell_exec(browser_path + ' ' + outfile)
            if ret == 0:
                exit()
    logger.error('could not determine/start the browser')
