##############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Eric F Sorton
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

from collections import namedtuple
import optparse
import sys
import serial

def static_vars(**kwargs):
    """Python decorator to declare static variables on a method.

    NOTE: Relies on the Python feature that allows attributes to be added to a
    function.  See:

        http://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function

    for source of decorator code and additional information.
    """
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

def bcd_to_int(bcd_byte):
    """Converts a packed, little-endian, binary coded decimal to an int.

    NOTE: byte must be a string (length of 1).  A ValueException is generated
    if the length is greater than 1 or if the decoded value is less than 0 or
    greater than 99.

    Returns a decimal value between 0 and 99.
    """

    # Method only works on single bytes.
    if len(bcd_byte) > 1:
        raise ValueError("Invalid length; bcdToInt() assumes single byte input.")

    # Get the tens place; value must be a single digit.
    tens = int((ord(bcd_byte) >> 0) & 0x0F)
    if (tens < 0) or (tens > 9):
        raise ValueError("Invalid BCD digit; tens place is not 0-9.")

    # Get the ones place; value must be a single digit.
    ones = int((ord(bcd_byte) >> 4) & 0x0F)
    if (ones < 0) or (ones > 9):
        raise ValueError("Invalid BCD digit; ones place is not 0-9.")

    return (tens*10 + ones)


def bcd_string_to_integer_list(bcd_string):
    """Converts a packed, little-endian, binary coded string to a list of integers.

    Returns a list of integers.  Each integer in the list is between 0 and 99.
    """
    return [bcd_to_int(byte) for byte in bcd_string]


def integer_list_to_named_tuple(list_of_integers):
    """
    Converts a list of integers read from the ultrak498 into a named tuple
    based upon the type.  The type is determiend by the first integer in the
    list.  Since all tuples contain five fields, the list of integers must
    have a length of five.

    Returns a named tuple based on the type,
    """

    # Dictionary mapping type id to record named tuples.
    valid_types = {
         0: namedtuple("RaceHeader", "type year month day id"),
         1: namedtuple("RaceHeader", "type year month day id"),
         2: namedtuple("RaceHeader", "type year month day id"),
         3: namedtuple("RaceHeader", "type year month day id"),
         4: namedtuple("RaceHeader", "type year month day id"),
         5: namedtuple("RaceHeader", "type year month day id"),
         6: namedtuple("RaceHeader", "type year month day id"),
         7: namedtuple("RaceHeader", "type year month day id"),
         8: namedtuple("RaceHeader", "type year month day id"),
         9: namedtuple("RaceHeader", "type year month day id"),
        10: namedtuple("LapTime",    "type minutes seconds hundreths lap"),
        20: namedtuple("AbsTime",    "type minutes seconds hundreths lap"),
        30: namedtuple("Type30",     "type a b c laps"),
        40: namedtuple("Type40",     "type a b c laps"),
        50: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        }

    # List of integers must be length of five.
    if len(list_of_integers) != 5:
        raise ValueError("Unable to convert list of integers to tuple; incorrect number of integers.")

    # First byte is the type; type must be known.
    tuple_type = list_of_integers[0]
    if tuple_type not in valid_types:
        raise ValueError("Unable to convert list of integers to tuple; unknown record type [%d]." % tuple_type)

    # Create a namedtuple based upon the tuple_type.
    named_tuple = valid_types[tuple_type]._make(list_of_integers)

    return named_tuple

@static_vars(lap_hundreds=0, abs_hundreds=0)
def adjust_lap_hundreds(record):
    """Adjusts the lap records to account for more than 99 laps/runners.

    As BCD cannot represent a value greater than 100, if there are more than
    100 laps/runners within a single race, the ultrak498 timer overflows to
    the lap to 0.
    """
    record_type_name = type(record).__name__

    # Reset hundreds place when a new races starts.
    if record_type_name == 'RaceHeader':
        adjust_lap_hundreds.lap_hundreds = 0
        adjust_lap_hundreds.abs_hundreds = 0

    # Adjust lap by hundreds place; increment on overflow.
    elif record_type_name == 'LapTime':
        if record.lap == 0:
            adjust_lap_hundreds.lap_hundreds += 100
        record = record._replace(lap=(record.lap + adjust_lap_hundreds.lap_hundreds))

    # Adjust abs by hundreds place; increment on overflow.
    elif record_type_name == 'AbsTime':
        if record.lap == 0:
            adjust_lap_hundreds.abs_hundreds += 100
        record = record._replace(lap=(record.lap + adjust_lap_hundreds.abs_hundreds))

    return record

def readRecord(in_file):
    """Generator to read each record from the input file.

    Returns the next record as a named tuples.
    """

    while True:

        # Records are always five bytes wide; read one record.
        record_as_bsd_string = in_file.read(5)
        if not record_as_bsd_string:
            break
        if len(record_as_bsd_string) != 5:
            raise ValueError(":TODO:wrong length")

        record_as_integer_list = bcd_string_to_integer_list(record_as_bsd_string)
        record_as_namedtuple = integer_list_to_named_tuple(record_as_integer_list)
        adjusted_record_as_namedtuple = adjust_lap_hundreds(record_as_namedtuple)

        yield adjusted_record_as_namedtuple


def openFile(infile):
    """Attempts to open the given file.

    Returns a file object.
    """

    # First, use infile if it is a file object.
    if isinstance(infile, file):
        return infile

    # Next, check if it is a serial port we can open.  Ignore exceptions so we
    # can try to open infile as a normal file next.
    try:
        return serial.Serial(infile, baudrate=4800, timeout=10)
    except:
        pass

    # Finally, try to open it as a normal file.  Let open() throw its
    # exception normally on failure.
    return open(infile, "rb")


def readRecords(infile):
    """Reads all records from the input file.

    Returns a list of named tuples, one for each record read.
    """
    infile = openFile(infile)
    return [record for record in readRecord(infile)]


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", "--infile",   dest="infile",   metavar="FILE",           default=sys.stdin,  help="Input file, stdin if not specified.")
    parser.add_option("-o", "--outfile",  dest="outfile",  metavar="FILE",           default=sys.stdout, help="Output file, stdout if not specified.")
    parser.add_option("-r", "--raceid",   dest="raceid",   metavar="NUM",  type=int, default=1,          help="Race ID to display.")
    (options, args) = parser.parse_args()

    current_race = 0
    for record in readRecords(options.infile):
        if record.type < 10:
            current_race = record.id
        if (record.type == 20) and (current_race == options.raceid):
            total_in_hundreths = record.minutes*60*100 + record.seconds*100 + record.hundreths
            print "{},{}:{:02}.{:02},{}".format(record.lap,record.minutes,record.seconds,record.hundreths,total_in_hundreths)

##############################################################################
# vim: ts=4 sts=4 sw=4 tw=78 sta et
##############################################################################
