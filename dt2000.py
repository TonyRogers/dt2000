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
        raise ValueError(
            "Invalid length; bcdToInt() assumes single byte input.")

    # Get the tens place; value must be a single digit.
    tens = int((ord(bcd_byte) >> 0) & 0x0F)
    # if (tens < 0) or (tens > 9):
    #     print("Invalid BCD digit; tens place is not 0-9.")

    # Get the ones place; value must be a single digit.
    ones = int((ord(bcd_byte) >> 4) & 0x0F)
    # if (ones < 0) or (ones > 9):
    #     raise ValueError("Invalid BCD digit; ones place is not 0-9.")

    return (tens * 10 + ones)


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
        990: namedtuple("RaceHeader", "type year month day id"),
        991: namedtuple("RaceHeader", "type year month day id"),
        992: namedtuple("RaceHeader", "type year month day id"),
        993: namedtuple("RaceHeader", "type year month day id"),
        994: namedtuple("RaceHeader", "type year month day id"),
        995: namedtuple("RaceHeader", "type year month day id"),
        996: namedtuple("RaceHeader", "type year month day id"),
        997: namedtuple("RaceHeader", "type year month day id"),
        998: namedtuple("RaceHeader", "type year month day id"),
        999: namedtuple("RaceHeader", "type year month day id"),
        10: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        11: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        12: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        13: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        14: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        15: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        16: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        17: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        18: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        19: namedtuple("LapTime",    "type minutes seconds hundredths lap"),
        20: namedtuple("AbsTime",    "type minutes seconds hundreths lap"),
        30: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        31: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        32: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        33: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        34: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        35: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        36: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        37: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        38: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        39: namedtuple("AvLapTime",   "type minutes seconds hundredths laps"),
        40: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        41: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        42: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        43: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        44: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        45: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        46: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        47: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        48: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        49: namedtuple("FastestLapTime",
                       "type minutes seconds hundredths laps"),
        50: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        51: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        52: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        53: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        54: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        55: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        56: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        57: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        58: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        59: namedtuple("RaceEnd",    "type minutes seconds hundreths laps"),
        9961: namedtuple("Type61",     "type a b c laps"),
        9966: namedtuple("Type66",     "type a b c laps"),
        9967: namedtuple("Type67",     "type a b c laps"),
        9968: namedtuple("Type68",     "type a b c laps"),
        9937: namedtuple("Type73",     "type a b c laps"),
        9974: namedtuple("Type74",     "type a b c laps"),
        9986: namedtuple("Type86",     "type a b c laps"),
        9988: namedtuple("Type88",     "type a b c laps"),
        90: namedtuple("RaceHeader", "type year month day id"),
    }
    # List of integers must be length of five.
    # print "list_of_integers = " + str(list_of_integers)
    if len(list_of_integers) != 5:
        raise ValueError(
            "Unable to convert list of integers to tuple; \
             incorrect number of integers.")

    # First byte is the type; type must be known.
    tuple_type = list_of_integers[0]
    if tuple_type not in valid_types:
        # raise ValueError("Unable to convert list of integers to tuple; \
        # unknown record type [%d]." % tuple_type)
        return
    else:
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
        record = record._replace(
            lap=(record.lap + adjust_lap_hundreds.lap_hundreds))

    # Adjust abs by hundreds place; increment on overflow.
    elif record_type_name == 'AbsTime':
        if record.lap == 0:
            adjust_lap_hundreds.abs_hundreds += 100
        record = record._replace(
            lap=(record.lap + adjust_lap_hundreds.abs_hundreds))

    return record


def readRecord(in_file):
    """Generator to read each record from the input file.

    Returns the next record as a named tuples.
    """
    while True:

        if not options.hexmode:
            # Records are always five bytes wide; read one record.
            record_as_bcd_string = in_file.read(5)
            if not record_as_bcd_string:
                break
            if len(record_as_bcd_string) != 5:
                raise ValueError(":TODO:wrong length")
        else:
            # Read from Bit Banged Serial
            record_as_bcd_string = ''
            # Read 5 bytes of 2 chars
            for x in range(5):
                raw_chars = in_file.read(2)
                print "Read " + raw_chars
                if not raw_chars:
                    return
                if len(raw_chars) != 2:
                    raise ValueError(":TODO:wrong length")

                # Swap chars
                swapped_chars = raw_chars[0] + raw_chars[1]
                # Append to record_as_bcd_string
                record_as_bcd_string += chr(int(swapped_chars, 16))

        # Now process the input
        record_as_integer_list = bcd_string_to_integer_list(
            record_as_bcd_string)
        if options.dumpmode:
            d.write(record_as_bcd_string)
        # print record_as_integer_list
        record_as_namedtuple = integer_list_to_named_tuple(
            record_as_integer_list)
        adjusted_record_as_namedtuple = adjust_lap_hundreds(
            record_as_namedtuple)

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
    parser.add_option("--hex",
                      dest="hexmode",
                      default=0,
                      action='store_const',
                      const=1,
                      help="if reading HEX file")
    parser.add_option("--dump",
                      dest="dumpmode",
                      default=0,
                      action='store_const',
                      const=1,
                      help="Dump raw data")
    parser.add_option("-f", "--infile",
                      dest="infile",
                      metavar="FILE",
                      default=sys.stdin,
                      help="Input file, stdin if not specified.")
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      metavar="FILE",
                      default=sys.stdout,
                      help="Output file, stdout if not specified.")
    parser.add_option("-r", "--raceid",
                      dest="raceid",
                      metavar="NUM",
                      type=int,
                      default=1,
                      help="Race ID to display.")
    (options, args) = parser.parse_args()

    print "infile = " + str(options.infile)
    print "hexmode = " + str(options.hexmode)
    print "dumpmode = " + str(options.dumpmode)
    if options.dumpmode:
        d=open('dump', 'w')

    current_race = 0
    elapsed_secs = 0L
    position = 0
    pos_hundredths = pos_secs = pos_mins = pos_hours = 0

    for record in readRecords(options.infile):
        if record is not None:
            # print record
            record_type_name = type(record).__name__
            if record_type_name == 'RaceHeader':
                print "New Race Detected"
                elapsed_secs = 0L
                position = 0
                pos_hundredths = pos_secs = pos_mins = pos_hours = 0
            elif record_type_name == 'LapTime':
                # print "Process a finisher"
                position += 1
                lap_time_hours = record.type % 10
                lap_time_minutes = record.minutes
                lap_time_secs = record.seconds
                lap_time_hundredths = record.hundredths
                elapsed_secs += (lap_time_hours * 3600 + lap_time_minutes * 60
                                 + lap_time_secs
                                 + lap_time_hundredths / 100.0)
                # int((elapsed_secs - pos_secs) * 100)
                pos_hundredths += lap_time_hundredths
                if pos_hundredths >= 100:
                    pos_hundredths = pos_hundredths % 100
                    pos_secs += 1
                # int(elapsed_secs - pos_hours * 3600 - pos_mins * 60)
                pos_secs += lap_time_secs
                if pos_secs >= 60:
                    pos_secs = pos_secs % 60
                    pos_mins += 1
                # int((elapsed_secs - pos_hours * 3600) / 60)
                pos_mins += lap_time_minutes
                if pos_mins >= 60:
                    pos_mins = pos_mins % 60
                    pos_hours += 1
                pos_hours += lap_time_hours  # int(elapsed_secs/3600)
                if position != record.lap:
                    raise ValueError(
                        "Mismatch between lap record and internal counter")
                print "Finisher: " + str(position) + "  Finishing time: " \
                    + str(pos_hours) + " Hrs. " + str(pos_mins) + " Mins. " \
                    + str(pos_secs) + " Secs. " \
                    + str(pos_hundredths) + " Hundr. "
            elif record_type_name == 'RaceEnd':
                print "Race finished"
            elif record_type_name == 'AvLapTime':
                av_lap_time_hours = record.type % 10
                av_lap_time_minutes = record.minutes
                av_lap_time_secs = record.seconds
                av_lap_time_hundredths = record.hundredths
                print "Average Lap time: " + str(av_lap_time_hours) \
                    + " Hrs. " + str(av_lap_time_minutes) + " Mins. " \
                    + str(av_lap_time_secs) + " Secs. " \
                    + str(av_lap_time_hundredths) + " Hundr. "
            elif record_type_name == 'FastestLapTime':
                f_lap_time_hours = record.type % 10
                f_lap_time_minutes = record.minutes
                f_lap_time_secs = record.seconds
                f_lap_time_hundredths = record.hundredths
                print "Fastest Lap time: " + str(f_lap_time_hours) \
                    + " Hrs. " + str(f_lap_time_minutes) + " Mins. " \
                    + str(f_lap_time_secs) + " Secs. " \
                    + str(f_lap_time_hundredths) + " Hundr. "
    if options.dumpmode:
        d.close()
