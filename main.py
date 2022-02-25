#!/usr/bin/env python
#
# OpenTelemetry log parser, processor and formatter
# Anthony Rabiaza (anthony.rabiaza@gmail.com)
# 2022-01-21
#
# pip install jsonpath-ng
# pip install tqdm

import json
import signal
import subprocess
import datetime
import sys

from jsonpath_ng.ext import parse
from tqdm import tqdm


def process_log(logfile_input, logfile_output):
    pbar = None

    print(f'Opening {logfile_input}')
    input_file = subprocess.Popen(['tail', '-fF', logfile_input], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f'Writing to {logfile_input}')
    output_file = open(logfile_output, "a")

    now = datetime.datetime.now()
    print(str(now) + ': Receiving and processing traces...')

    if len(sys.argv) > 1 and sys.argv[1] == '-background':
        background = True
    else:
        background = False

    if len(sys.argv) > 1 and sys.argv[1] == '-debug':
        debug = True
    else:
        debug = False

    if not background:
        pbar = tqdm(total=100)

    i = 0

    while True:
        line = input_file.stdout.readline()
        new_line = process(line)
        if not background:
            pbar.update()
        new_line = new_line.strip()
        if new_line != '':
            output_file.write(new_line + '\n')
            output_file.flush()
            if debug:
                print('+++++', end='', flush=True)
        else:
            if debug:
                print('-----', end='', flush=True)
        if i < 100:
            i = i + 1
        else:
            i = 0
            if not background:
                pbar.refresh()
                pbar.reset()


def process(line):
    spans_path = '$.resourceSpans[*].instrumentationLibrarySpans[*].spans'
    contents = json.loads(line)
    jsonpath_expr = parse(spans_path + '[*].traceId')
    trace_ids = [match.value for match in jsonpath_expr.find(contents)]
    # print(trace_ids)
    trace_ids_set = set(trace_ids)
    # print(trace_ids_set)

    return_str = ''

    for trace_id in trace_ids_set:
        current_trace_operation_path = spans_path + '[?(traceId == "' + trace_id + '")].name'
        # print(current_trace_id_path)
        jsonpath_expr_local = parse(current_trace_operation_path)
        current_trace_id = [match.value for match in jsonpath_expr_local.find(contents)]
        span_number = len(current_trace_id)
        operations = ','.join(current_trace_id)
        # Filtering Boomi Atom Poller logs
        if not (span_number == 1 and (operations == 'HTTP GET' or operations == 'HTTP POST')):
            return_str += datetime.datetime.now().isoformat() + ' ' + 'traceID=' + trace_id \
                          + ' span_number=' + str(span_number) \
                          + ' operations="' + operations + '"\n'

    return return_str


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    print('----------------------------------------------------------------')
    print('OpenTelemetry Log Parser')
    print('  https://github.com/anthonyrabiaza/opentelemetry-log-parser')
    print('  Press Ctrl+C to stop the process')
    print('----------------------------------------------------------------')
    process_log('traces.log', 'traces_parsed.log')