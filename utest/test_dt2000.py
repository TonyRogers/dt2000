##############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Anthony Rogers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
##############################################################################

import unittest
import dt2000


class test_bcd_to_int(unittest.TestCase):
    def testValueOfZeroReturnsZero(self):
        value = dt2000.bcd_to_int(chr(0x00))
        self.assertEqual(value, 0)

    def testValueOfOneReturnsOne(self):
        value = dt2000.bcd_to_int(chr(0x10))
        self.assertEqual(value, 1)

    def testValueOfNineReturnsNine(self):
        value = dt2000.bcd_to_int(chr(0x90))
        self.assertEqual(value, 9)

    def testValueOfTenReturnsTen(self):
        value = dt2000.bcd_to_int(chr(0x01))
        self.assertEqual(value, 10)

    def testValueOfElevenReturnsEleven(self):
        value = dt2000.bcd_to_int(chr(0x11))
        self.assertEqual(value, 11)

    def testValueOfFifteenReturnsFifteen(self):
        value = dt2000.bcd_to_int(chr(0x51))
        self.assertEqual(value, 15)

    def testValueOfTwentyReturnsTwenty(self):
        value = dt2000.bcd_to_int(chr(0x02))
        self.assertEqual(value, 20)

    def testValueOf42Returns42(self):
        value = dt2000.bcd_to_int(chr(0x24))
        self.assertEqual(value, 42)

    def testValueOf50Returns50(self):
        value = dt2000.bcd_to_int(chr(0x05))
        self.assertEqual(value, 50)

    def testValueOf75Returns75(self):
        value = dt2000.bcd_to_int(chr(0x57))
        self.assertEqual(value, 75)

    def testValueOf98Returns98(self):
        value = dt2000.bcd_to_int(chr(0x89))
        self.assertEqual(value, 98)

    def testValueOf99Returns99(self):
        value = dt2000.bcd_to_int(chr(0x99))
        self.assertEqual(value, 99)

    def testMultiByteStringRaisesException(self):
        with self.assertRaises(ValueError):
            dt2000.bcd_to_int("ab")


class TEST_bcd_string_to_integer_list(unittest.TestCase):
    def testEmptyStringReturnsEmptyList(self):
        value = dt2000.bcd_string_to_integer_list("")
        self.assertEqual(value, [])

    def testOneByteStringReturnsOneItemList(self):
        value = dt2000.bcd_string_to_integer_list(chr(0x32))
        self.assertEqual(value, [23])

    def testTwoByteStringReturnsTwoItemList(self):
        value = dt2000.bcd_string_to_integer_list(chr(0x52) + chr(0x21))
        self.assertEqual(value, [25,12])

    def testFiveByteStringReturnsFiveItemList(self):
        value = dt2000.bcd_string_to_integer_list(chr(0x11) + chr(0x21) + chr(0x31) + chr(0x41) + chr(0x51))
        self.assertEqual(value, [11,12,13,14,15])

class TEST_integer_list_to_param_dict(unittest.TestCase):
    def testInvalidInputArgument(self):
        with self.assertRaises(ValueError):
            value = dt2000.integer_list_to_param_dict("")

    def testInvalidLengthOfTuple(self):
        with self.assertRaises(ValueError):
            value = dt2000.integer_list_to_param_dict([0,0,0])


    def testRaceHeaderTuple(self):
        value = dt2000.integer_list_to_param_dict([90,0,0,0,0])
        self.assertEqual(value, {'p2': 0, 'p3': 0, 'p1': 90, 'p4': 0, 'p5': 0, 'ptype': 'raceheader'})
        self.assertEqual(value['ptype'], 'raceheader')
        self.assertEqual(value['p1'], 90)

    def testLapTimeTuple(self):
        value = dt2000.integer_list_to_param_dict([10,0,0,0,0])
        self.assertEqual(value, {'p2': 0, 'p3': 0, 'p1': 10, 'p4': 0, 'p5': 0, 'ptype': 'laptime'})
        self.assertEqual(value['ptype'], 'laptime')
        self.assertEqual(value['p1'], 10)

    def testAbsTimeTuple(self):
        value = dt2000.integer_list_to_param_dict([20,0,0,0,0])
        self.assertEqual(value, {'p2': 0, 'p3': 0, 'p1': 20, 'p4': 0, 'p5': 0, 'ptype': 'abstime'})
        self.assertEqual(value['ptype'], 'abstime')
        self.assertEqual(value['p1'], 20)

    def testRaceEndTuple(self):
        value = dt2000.integer_list_to_param_dict([50,0,0,0,0])
        self.assertEqual(value, {'p2': 0, 'p3': 0, 'p1': 50, 'p4': 0, 'p5': 0, 'ptype': 'raceend'})
        self.assertEqual(value['ptype'], 'raceend')
        self.assertEqual(value['p1'], 50)

        value = dt2000.integer_list_to_param_dict([50,1,2,3,4])
        self.assertEqual(value, {'p2': 1, 'p3': 2, 'p1': 50, 'p4': 3, 'p5': 4, 'ptype': 'raceend'})
        self.assertEqual(value['ptype'], 'raceend')
        self.assertEqual(value['p1'], 50)
        self.assertEqual(value['p2'], 1)
        self.assertEqual(value['p3'], 2)
        self.assertEqual(value['p4'], 3)
        self.assertEqual(value['p5'], 4)

class TEST_adjust_lap_hundreds_p_dict(unittest.TestCase):

    def testAdjustmentAbsForHundreds(self):
        dt2000.adjust_lap_hundreds_p_dict.abs_hundreds = 0

        params = {"ptype": 'abstime',
                  "p1": 0, "p2": 0, "p3": 0, "p4": 0, "p5": 0}

        for test_value, expected_value in [(99, 99), (0, 100),
                                           (1, 101), (2, 102),
                                           (99, 199), (0, 200), (21, 221),
                                           (0, 300), (0, 400), (0, 500),
                                           (55, 555)]:
            params['p5'] = test_value
            out_record = dt2000.adjust_lap_hundreds_p_dict(params)
            self.assertEqual(expected_value, out_record['p5'])
