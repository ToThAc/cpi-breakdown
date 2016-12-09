# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 IBM Corporation

Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

    Contributors:
        * Rafael Sene <rpsene@br.ibm.com>
        * Daniel Kreling <dbkreling@br.ibm.com>
        * Roberto Oliveira <rdutra@br.ibm.com>
"""

import core
import os
import sys

import events_reader


def run_cpi(binary_path, binary_args, output_location, advance_toolchain):
    '''
    Uses the current path as destination if nothing is set
    by the user.
    '''
    ocount = "ocount"
    if advance_toolchain:
        ocount = "/opt/" + advance_toolchain + "/bin/" + ocount

    if not output_location:
        output_location = os.getcwd()
    else:
        try:
            if not (os.path.isdir(output_location)):
                os.makedirs(output_location)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
                sys.exit(1)

    timestamp = core.get_timestamp()
    ocount_out = output_location + "/output"

    if not core.cmdexists(ocount):
        sys.stderr.write(ocount + " is not installed in the system. " +
                         "Install oprofile before continue." + "\n")
        sys.exit(2)

    reader = events_reader.EventsReader(core.get_processor())
    for event in reader.get_events():
        ocount_cmd = ocount + " -b -f " + ocount_out
        for item in event:
            ocount_cmd += " -e " + item
        print "\n" + "Running: " + ocount_cmd + " " + binary_path + binary_args
        status = core.execute(ocount_cmd + ' ' + binary_path + binary_args)
        if status != 0:
            sys.stderr.write("\nFailed to run {0} command.\n".format(ocount) +
                             "For more information check the error message " +
                             "above")
            sys.exit(1)

        core.parse_file(ocount_out, timestamp, ".cpi")
    core.execute("rm " + ocount_out)
    '''
    TODO: calculate metrics here
    mc = MetricsCalculator(core.get_processor())
    events_result = defaultdict(list)
    with open("./output") as fin:
        for line in fin:
            k, v = line.strip().split(" : ")
            events_result[k].append(v)
    print mc.calculate_metrics(events_result)
    '''
    return


def compare_output(file_names):
    """ Get the contents of two ocount output files and compare their
        results, print it in a format of a table """
    print "Comparing file_names: %s and %s" % (file_names[0], file_names[1])
    dict_list = []
    for file_name in file_names:
        dict_i = core.file_to_dict(file_name)
        dict_list.append(dict_i)

    # Create one dictionary as {"events" : (val_file_1, val_file_2), ...}
    dict_vals = {}
    for key in dict_list[0]:
        dict_vals[key] = tuple(d[key] for d in dict_list)

    print "%-*s: %-*s -> %*s  :  %s" % (35, "Event Name", 7, "Value", 7,
                                        "Value", "Gain")
    print '-' * 35, '', '-' * 7, ' ' * 3, '-' * 7, '  ', '-'*10

    # Create table reading first and second values in each key
    for key in dict_vals:
        try:
            if int(dict_vals[key][0]) != 0:
                percentage = core.percentage(int(dict_vals[key][1]),
                                             int(dict_vals[key][0]))
            else:
                percentage = "-"
            print "%-*s: %-*s -> %-*s  :  %s %-*s" % (35, key, 7,
                                                      dict_vals[key][0], 7,
                                                      dict_vals[key][1],
                                                      percentage, 3, "%")
        except IndexError:
            sys.exit(1)
    return 0


def run_drilldown(event, binary_path, binary_args, advance_toolchain):
    """ Run the drilldown feature """
    tool_prefix = ''
    if advance_toolchain:
        tool_prefix = "/opt/" + advance_toolchain + "/bin/"

    if not core.cmdexists(tool_prefix + "operf"):
        sys.stderr.write(tool_prefix + "operf is not installed in the system. " +
                         "Install oprofile before continue." + "\n")
        sys.exit(0)

    reader = events_reader.EventsReader(core.get_processor())

    # Event is not supported with drilldown feature
    if not reader.valid_event(event):
        sys.stderr.write("Event {0} is not supported by drilldown feature.".format(event) +
                         "\nChoose a supported event and try again\n")
        sys.exit(0)

    # Run operf command
    event_min_count = str(reader.get_event_mincount(event))
    operf_cmd = tool_prefix + "operf -e {0}:{1} {2} {3}".format(event, event_min_count, binary_path, binary_args)
    core.execute(operf_cmd)

    # Run opreport command
    temp_file = "opreport.xml"
    opreport_cmd = tool_prefix + "opreport --debug-info --symbols --details --xml event:{0} -o {1}".format(
        event, temp_file)
    core.execute(opreport_cmd)

    # TODO: Implement the parser for the generated file
