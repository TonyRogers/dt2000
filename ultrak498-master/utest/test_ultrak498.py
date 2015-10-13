##############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Eric F Sorton
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
import ultrak498
from collections import namedtuple

class TEST_bcd_to_int(unittest.TestCase):
    def testValueOfZeroReturnsZero(self):
        value = ultrak498.bcd_to_int(chr(0x00))
        self.assertEqual(value, 0)

    def testValueOfOneReturnsOne(self):
        value = ultrak498.bcd_to_int(chr(0x10))
        self.assertEqual(value, 1)

    def testValueOfNineReturnsNine(self):
        value = ultrak498.bcd_to_int(chr(0x90))
        self.assertEqual(value, 9)

    def testValueOfTenReturnsTen(self):
        value = ultrak498.bcd_to_int(chr(0x01))
        self.assertEqual(value, 10)

    def testValueOfElevenReturnsEleven(self):
        value = ultrak498.bcd_to_int(chr(0x11))
        self.assertEqual(value, 11)

    def testValueOfFifteenReturnsFifteen(self):
        value = ultrak498.bcd_to_int(chr(0x51))
        self.assertEqual(value, 15)

    def testValueOfTwentyReturnsTwenty(self):
        value = ultrak498.bcd_to_int(chr(0x02))
        self.assertEqual(value, 20)

    def testValueOf42Returns42(self):
        value = ultrak498.bcd_to_int(chr(0x24))
        self.assertEqual(value, 42)

    def testValueOf50Returns50(self):
        value = ultrak498.bcd_to_int(chr(0x05))
        self.assertEqual(value, 50)

    def testValueOf75Returns75(self):
        value = ultrak498.bcd_to_int(chr(0x57))
        self.assertEqual(value, 75)

    def testValueOf98Returns98(self):
        value = ultrak498.bcd_to_int(chr(0x89))
        self.assertEqual(value, 98)

    def testValueOf99Returns99(self):
        value = ultrak498.bcd_to_int(chr(0x99))
        self.assertEqual(value, 99)

    def testMultiByteStringRaisesException(self):
        with self.assertRaises(ValueError):
            ultrak498.bcd_to_int("ab")

    def testOnesPlaceGreaterThanNineRaisesException(self):
        with self.assertRaises(ValueError):
            ultrak498.bcd_to_int(chr(0xA0))

    def testTensPlaceGreaterThanNineRaisesException(self):
        with self.assertRaises(ValueError):
            ultrak498.bcd_to_int(chr(0x0A))

class TEST_bcd_string_to_integer_list(unittest.TestCase):
    def testEmptyStringReturnsEmptyList(self):
        value = ultrak498.bcd_string_to_integer_list("")
        self.assertEqual(value, [])

    def testOneByteStringReturnsOneItemList(self):
        value = ultrak498.bcd_string_to_integer_list(chr(0x32))
        self.assertEqual(value, [23])

    def testTwoByteStringReturnsTwoItemList(self):
        value = ultrak498.bcd_string_to_integer_list(chr(0x52) + chr(0x21))
        self.assertEqual(value, [25,12])

    def testFiveByteStringReturnsFiveItemList(self):
        value = ultrak498.bcd_string_to_integer_list(chr(0x11) + chr(0x21) + chr(0x31) + chr(0x41) + chr(0x51))
        self.assertEqual(value, [11,12,13,14,15])

class TEST_integer_list_to_named_tuple(unittest.TestCase):
    def testInvalidInputArgument(self):
        with self.assertRaises(ValueError):
            value = ultrak498.integer_list_to_named_tuple("")

    def testInvalidLengthOfTuple(self):
        with self.assertRaises(ValueError):
            value = ultrak498.integer_list_to_named_tuple([0,0,0])

    def testInvalidType(self):
        with self.assertRaises(ValueError):
            value = ultrak498.integer_list_to_named_tuple([99,0,0,0,0])

    def testRaceHeaderTuple(self):
        value = ultrak498.integer_list_to_named_tuple([1,0,0,0,0])
        self.assertEqual(value, (1,0,0,0,0))
        self.assertEqual(value.type, 1)
        self.assertEqual(value.year, 0)
        self.assertEqual(value.month, 0)
        self.assertEqual(value.day, 0)
        self.assertEqual(value.id, 0)

        value = ultrak498.integer_list_to_named_tuple([2,1,2,3,4])
        self.assertEqual(value, (2,1,2,3,4))
        self.assertEqual(value.type, 2)
        self.assertEqual(value.year, 1)
        self.assertEqual(value.month, 2)
        self.assertEqual(value.day, 3)
        self.assertEqual(value.id, 4)

    def testLapTimeTuple(self):
        value = ultrak498.integer_list_to_named_tuple([10,0,0,0,0])
        self.assertEqual(value, (10,0,0,0,0))
        self.assertEqual(value.type, 10)
        self.assertEqual(value.minutes, 0)
        self.assertEqual(value.seconds, 0)
        self.assertEqual(value.hundreths, 0)
        self.assertEqual(value.lap, 0)

        value = ultrak498.integer_list_to_named_tuple([10,1,2,3,4])
        self.assertEqual(value, (10,1,2,3,4))
        self.assertEqual(value.type, 10)
        self.assertEqual(value.minutes, 1)
        self.assertEqual(value.seconds, 2)
        self.assertEqual(value.hundreths, 3)
        self.assertEqual(value.lap, 4)

    def testAbsTimeTuple(self):
        value = ultrak498.integer_list_to_named_tuple([20,0,0,0,0])
        self.assertEqual(value, (20,0,0,0,0))
        self.assertEqual(value.type, 20)
        self.assertEqual(value.minutes, 0)
        self.assertEqual(value.seconds, 0)
        self.assertEqual(value.hundreths, 0)
        self.assertEqual(value.lap, 0)

        value = ultrak498.integer_list_to_named_tuple([20,1,2,3,4])
        self.assertEqual(value, (20,1,2,3,4))
        self.assertEqual(value.type, 20)
        self.assertEqual(value.minutes, 1)
        self.assertEqual(value.seconds, 2)
        self.assertEqual(value.hundreths, 3)
        self.assertEqual(value.lap, 4)

    def testRaceEndTuple(self):
        value = ultrak498.integer_list_to_named_tuple([50,0,0,0,0])
        self.assertEqual(value, (50,0,0,0,0))
        self.assertEqual(value.type, 50)
        self.assertEqual(value.minutes, 0)
        self.assertEqual(value.seconds, 0)
        self.assertEqual(value.hundreths, 0)
        self.assertEqual(value.laps, 0)

        value = ultrak498.integer_list_to_named_tuple([50,1,2,3,4])
        self.assertEqual(value, (50,1,2,3,4))
        self.assertEqual(value.type, 50)
        self.assertEqual(value.minutes, 1)
        self.assertEqual(value.seconds, 2)
        self.assertEqual(value.hundreths, 3)
        self.assertEqual(value.laps, 4)

class TEST_adjust_lap_hundreds(unittest.TestCase):
    def testNoAdjustmentLap(self):
        ultrak498.adjust_lap_hundreds.lap_hundreds = 0

        LapTimeMock = namedtuple('LapTime', 'lap')
        for test_value in [1, 2, 11, 23, 45, 68, 80, 99]:
            in_record = LapTimeMock(test_value)
            out_record = ultrak498.adjust_lap_hundreds(in_record)
            self.assertEqual(in_record, out_record)

    def testNoAdjustmentAbs(self):
        ultrak498.adjust_lap_hundreds.abs_hundreds = 0

        AbsTimeMock = namedtuple('AbsTime', 'lap')
        for test_value in [1, 2, 11, 23, 45, 68, 80, 99]:
            in_record = AbsTimeMock(test_value)
            out_record = ultrak498.adjust_lap_hundreds(in_record)
            self.assertEqual(in_record, out_record)

    def testAdjustmentLapForHundreds(self):
        ultrak498.adjust_lap_hundreds.lap_hundreds = 0

        LapTimeMock = namedtuple('LapTime', 'lap')
        for test_value, expected_value in [(99, 99), (0, 100), (1, 101), (2, 102), (99, 199), (0, 200), (21, 221), (0, 300), (0, 400), (0, 500), (55, 555)]:
            in_record = LapTimeMock(test_value)
            out_record = ultrak498.adjust_lap_hundreds(in_record)
            self.assertEqual(LapTimeMock(expected_value), out_record)

    def testAdjustmentAbsForHundreds(self):
        ultrak498.adjust_lap_hundreds.abs_hundreds = 0

        AbsTimeMock = namedtuple('AbsTime', 'lap')
        for test_value, expected_value in [(99, 99), (0, 100), (1, 101), (2, 102), (99, 199), (0, 200), (21, 221), (0, 300), (0, 400), (0, 500), (55, 555)]:
            in_record = AbsTimeMock(test_value)
            out_record = ultrak498.adjust_lap_hundreds(in_record)
            self.assertEqual(AbsTimeMock(expected_value), out_record)

    def testAdjustmentForHundredsResetOnRaceStart(self):
        ultrak498.adjust_lap_hundreds.lap_hundreds = 0
        ultrak498.adjust_lap_hundreds.abs_hundreds = 0

        RaceHeaderMock = namedtuple('RaceHeader', 'ignore')
        LapTimeMock = namedtuple('LapTime', 'lap')
        AbsTimeMock = namedtuple('AbsTime', 'lap')

        in_record = LapTimeMock(1)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record, out_record)
        in_record = AbsTimeMock(1)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record, out_record)

        in_record = LapTimeMock(99)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record, out_record)
        in_record = AbsTimeMock(99)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record, out_record)

        in_record = LapTimeMock(0)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(LapTimeMock(100), out_record)
        in_record = AbsTimeMock(0)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(AbsTimeMock(100), out_record)

        in_record = LapTimeMock(99)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(LapTimeMock(199), out_record)
        in_record = AbsTimeMock(99)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(AbsTimeMock(199), out_record)

        in_record = LapTimeMock(0)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(LapTimeMock(200), out_record)
        in_record = AbsTimeMock(0)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(AbsTimeMock(200), out_record)

        in_record = RaceHeaderMock(0)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record , out_record)

        in_record = LapTimeMock(1)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record, out_record)
        in_record = AbsTimeMock(1)
        out_record = ultrak498.adjust_lap_hundreds(in_record)
        self.assertEqual(in_record, out_record)

##############################################################################
# vim: ts=4 sts=4 sw=4 tw=78 sta et
##############################################################################
