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
"""

import os
import re
import sys
from collections import defaultdict
from math import fabs
import parser
import yaml

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class MetricsCalculator(object):
    '''
    Class that calculates metrics
    '''
    metric_pattern = re.compile("^([A-Z][0-9]+)+$")
    metrics_groups = []

    def __init__(self, processor):
        metrics_file = DIR_PATH + "/metrics/" + str.lower(processor) + ".yaml"
        '''
        Get the metrics based on the processor version. They are located
        at /metrics/<processor_model>.yaml. It returns a dictionary which
        contains the NAME an the EQUATION
        '''
        with open(metrics_file, "r") as metrics:
            self.metrics_groups = yaml.load(metrics)

    def calculate_metrics(self, parsed_output_dict):
        '''
        Calculate the metrics based on the processor model and returns a list
        of list which contains:
                [
                [METRIC_NAME_1, METRIC_RESULT_1, METRIC_PERCENT_1],
                [METRIC_NAME_2, METRIC_RESULT_2, METRIC_PERCENT_2],
                ...
                ]
        It receives a dictonary with the parsed output of the execution.
        This dict content is <EVENT> : <VALUE> like:
            PM_CMPLU_STALL_THRD : 55322
            PM_CMPLU_STALL_BRU_CRU : 25701
            PM_CMPLU_STALL_COQ_FULL : 178
            PM_CMPLU_STALL_BRU : 16138
        '''
        parsed_output = defaultdict(list)
        parsed_output = parsed_output_dict
        metrics_results = []
        try:
            if int(parsed_output.get('PM_RUN_CYC')[0]) > 0:
                for group in self.metrics_groups.values():
                    result_tmp = []
                    '''
                    Split the metrics in all components to allow replacing the
                    events with the calculated values.
                    For example, the metric:
                    PM_CMPLU_STALL_DMISS_L3MISS - (PM_CMPLU_STALL_DMISS_LMEM + \
                    PM_CMPLU_STALL_DMISS_L21_L31 + PM_CMPLU_STALL_DMISS_REMOTE)
                    Becomes:
                    [PM_CMPLU_STALL_DMISS_L3MISS, -, (, PM_CMPLU_STALL_DMISS_LMEM,\
                     +, PM_CMPLU_STALL_DMISS_L21_L31, +, \
                     PM_CMPLU_STALL_DMISS_REMOTE, )]
                    '''
                    calc_function = re.split("([+-/*/(/)//])",
                                             group['METRIC'].replace(" ", ""))
                    for parameter in calc_function:
                        '''
                        If we find the event in the parsed output, it is
                        replaced by its value.
                        '''
                        if parameter in parsed_output:
                            calc_function[calc_function.index(parameter)] = parsed_output.get(parameter)[0]
                    '''
                    Once the events are replaced by its values in the metric,
                    we put it all togheter again and calculate the metric
                    '''
                    metric = parser.expr(''.join(calc_function)).compile()
                    if self.metric_pattern.match(str(metric)):
                        metric_result = eval(metric)
                        result_tmp.append(group["NAME"])
                        if metric_result > 0:
                            result_tmp.append(metric_result)
                            result_tmp.append(fabs((metric_result*100) / float(parsed_output.get('PM_RUN_CYC')[0])))
                        else:
                            result_tmp.append(0)
                            result_tmp.append(fabs(0))
                        metrics_results.append(result_tmp)
                    else:
                        sys.stderr.write("Could not calculate the metric " +
                                         metric)
                        sys.exit(0)
                return metrics_results
            else:
                sys.stderr.write("PM_RUN_CYC is 0.")
                sys.stderr.write("As it is the base divisor for all metrics \
                                 calculation it can not be 0. \
                                 Please run CPI again.")
                sys.exit(0)
        except Exception as ecx:
            sys.stderr.write(str(type(ecx)))
            sys.stderr.write(str(ecx.args))
            sys.stderr.write(str(ecx))
