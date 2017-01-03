#! /usr/bin/env python
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

import unittest
import csv
from cpi import core


class CoreTests(unittest.TestCase):
    """ Class to run tests from core """

    def test_execute(self):
        self.assertEqual(0, core.execute("cd"))
        self.assertNotEqual(0, core.execute("foo_bar"))

    def test_execute_stdout(self):
        status, output = core.execute_stdout("cd")
        self.assertEqual(0, status)
        self.assertEqual("", output)

        status, output = core.execute_stdout("ls /bla/foo")
        self.assertNotEqual(0, status)
        self.assertIn("No such file or directory", output)

    def test_cmdexist(self):
        assert True == core.cmdexists("cd")
        assert False == core.cmdexists("foo_bar")

    def test_get_processor(self):
        self.assertEqual("POWER8", core.get_processor())

    def test_supported_processor(self):
        assert False == core.supported_processor("POWER7")
        assert True == core.supported_processor("POWER8")

    def test_create_csv_file(self):
        values = [['element1', '20'], ['element2', '30']]
        file_path = core.create_csv_file("my_file", values)
        with open(file_path, 'r') as csvfile:
            file_content = []
            reader = csv.reader(csvfile)
            for row in reader:
                file_content.append(row)
            self.assertEqual(2, len(file_content))
            self.assertEqual(values[0], file_content[0])
            self.assertEqual(values[1], file_content[1])

    def test_percentage(self):
        self.assertEqual("100.00", core.percentage(10, 20))
        self.assertEqual("-50.00", core.percentage(20, 10))
        self.assertEqual("0.00", core.percentage(10, 10))

if __name__ == '__main__':
    unittest.main()
