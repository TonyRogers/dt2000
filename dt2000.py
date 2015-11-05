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

    # Get the ones place; value must be a single digit.
    ones = int((ord(bcd_byte) >> 4) & 0x0F)

    return (tens * 10 + ones)


def bcd_string_to_integer_list(bcd_string):
    """Converts a packed, little-endian, binary coded string to a list of integers.

    Returns a list of integers.  Each integer in the list is between 0 and 99.
    """
    return [bcd_to_int(byte) for byte in bcd_string]


def integer_list_to_param_dict(list_of_integers):
    valid_types = {}
    valid_types["laptime"] = range(10, 20)
    valid_types["abstime"] = range(20, 30)
    valid_types["avtime"] = range(30, 40)
    valid_types["fastesttime"] = range(40, 50)
    valid_types["raceend"] = range(50, 60)
    valid_types["raceheader"] = [90]

    params = {"ptype": 0, "p1": 0, "p2": 0, "p3": 0, "p4": 0, "p5": 0}

    # List of integers must be length of five.
    if len(list_of_integers) != 5:
        raise ValueError(
            "Unable to convert list of integers to tuple; \
             incorrect number of integers.")

    # First byte is the type; type must be known.
    params["ptype"] = 'NAK'
    msg_type = list_of_integers[0]
    for vt in valid_types.keys():
        for tc in valid_types[vt]:
            if msg_type == tc:
                # Got a match
                params["ptype"] = vt
                params['p1'] = list_of_integers[0]
                params['p2'] = list_of_integers[1]
                params['p3'] = list_of_integers[2]
                params['p4'] = list_of_integers[3]
                params['p5'] = list_of_integers[4]

    return params


@static_vars(lap_hundreds=0, abs_hundreds=0)
def adjust_lap_hundreds_p_dict(param_dict):
    """Adjusts the lap records to account for more than 99 laps/runners.

    As BCD cannot represent a value greater than 100, if there are more than
    100 laps/runners within a single race, the ultrak498 timer overflows to
    the lap to 0.
    """

    rtc = param_dict['ptype']
    if rtc != 'NAK':
        # Reset hundreds place when a new races starts.
        if rtc == 'raceheader':
            adjust_lap_hundreds_p_dict.lap_hundreds = 0
            adjust_lap_hundreds_p_dict.abs_hundreds = 0

        # Adjust lap by hundreds place; increment on overflow.
        elif rtc == 'laptime':
            # type minutes seconds hundreths laps
            if param_dict['p5'] == 0:
                adjust_lap_hundreds_p_dict.lap_hundreds += 100
            param_dict['p5'] = param_dict['p5'] \
                + adjust_lap_hundreds_p_dict.lap_hundreds

        # Adjust abs by hundreds place; increment on overflow.
        elif rtc == 'abstime':
            if param_dict['p5'] == 0:
                adjust_lap_hundreds_p_dict.lap_hundreds += 100
            param_dict['p5'] = param_dict['p5'] \
                + adjust_lap_hundreds_p_dict.lap_hundreds

    return param_dict


def readRecord(in_file):
    """Generator to read each record from the input file.

    Returns the next record as a named tuples.
    """
    while True:

        # Records are always five bytes wide; read one record.
        record_as_bcd_string = in_file.read(5)
        if not record_as_bcd_string:
            break
        if len(record_as_bcd_string) != 5:
            raise ValueError(":TODO:wrong length")

        # Now process the input
        record_as_integer_list = bcd_string_to_integer_list(
            record_as_bcd_string)
        if options.dumpmode:
            d.write(record_as_bcd_string)
        if options.debugmode:
            print record_as_integer_list
        p_dict = integer_list_to_param_dict(record_as_integer_list)

        if p_dict['ptype'] != 'NAK':
            p_dict = adjust_lap_hundreds_p_dict(p_dict)

        yield p_dict


def openFile(infile):
    """Attempts to open the given file.

    Returns a file object.
    """

    # First, use infile if it is a file object.
    if isinstance(infile, file):
        if options.debugmode:
            print "infile: " + str(infile) + " is an instance of a file"
        return infile

    # Next, check if it is a serial port we can open.  Ignore exceptions so we
    # can try to open infile as a normal file next.
    try:
        return serial.Serial(infile, baudrate=4800, timeout=10)
    except:
        pass

    # Finally, try to open it as a normal file.  Let open() throw its
    # exception normally on failure.
    if options.debugmode:
        print "Trying to open: " + str(infile) + " as a normal file"
    return open(infile, "rb")


def readRecords(infile):
    """Reads all records from the input file.

    Returns a list of named tuples, one for each record read.
    """
    infile = openFile(infile)
    return [record for record in readRecord(infile)]

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("--dump",
                      dest="dumpmode",
                      default=0,
                      action='store_const',
                      const=1,
                      help="Dump raw data")
    parser.add_option("-d", "--debug",
                      dest="debugmode",
                      default=0,
                      action='store_const',
                      const=1,
                      help="Dump internal stuff")
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

    if options.debugmode:
        print "debugmode = " + str(options.debugmode)
        print "infile = " + str(options.infile)
        print "outfile = " + str(options.outfile)
        print "dumpmode = " + str(options.dumpmode)

    if options.dumpmode:
        d = open('dump', 'w')

    current_race = 0
    elapsed_secs = 0L
    position = 0
    pos_hundredths = pos_secs = pos_mins = pos_hours = 0

    for record in readRecords(options.infile):
        rtc = record['ptype']
        if rtc != 'NAK':
            if rtc == 'raceheader':
                print "New Race Detected"
                elapsed_secs = 0L
                position = 0
                pos_hundredths = pos_secs = pos_mins = pos_hours = 0
            elif rtc == 'laptime':
                position += 1
                lap_time_hours = record['p1'] % 10
                lap_time_minutes = record['p2']
                lap_time_secs = record['p3']
                lap_time_hundredths = record['p4']
                elapsed_secs += (lap_time_hours * 3600 + lap_time_minutes * 60
                                 + lap_time_secs
                                 + lap_time_hundredths / 100.0)
                pos_hundredths += lap_time_hundredths
                if pos_hundredths >= 100:
                    pos_hundredths = pos_hundredths % 100
                    pos_secs += 1
                pos_secs += lap_time_secs
                if pos_secs >= 60:
                    pos_secs = pos_secs % 60
                    pos_mins += 1
                pos_mins += lap_time_minutes
                if pos_mins >= 60:
                    pos_mins = pos_mins % 60
                    pos_hours += 1
                pos_hours += lap_time_hours
                if position != record['p5']:
                    raise ValueError(
                        "Mismatch between lap record and internal counter")
                print "Finisher: " + str(position) + "  Finishing time: " \
                    + str(pos_hours) + " Hrs. " + str(pos_mins) + " Mins. " \
                    + str(pos_secs) + " Secs. " \
                    + str(pos_hundredths) + " Hundr. "
            elif rtc == 'raceend':
                print "Race finished"
            elif rtc == 'avtime':
                av_lap_time_hours = record['p1'] % 10
                av_lap_time_minutes = record['p2']
                av_lap_time_secs = record['p3']
                av_lap_time_hundredths = record['p4']
                print "Average Lap time: " + str(av_lap_time_hours) \
                    + " Hrs. " + str(av_lap_time_minutes) + " Mins. " \
                    + str(av_lap_time_secs) + " Secs. " \
                    + str(av_lap_time_hundredths) + " Hundr. "
            elif rtc == 'fastesttime':
                f_lap_time_hours = record['p1'] % 10
                f_lap_time_minutes = record['p2']
                f_lap_time_secs = record['p3']
                f_lap_time_hundredths = record['p4']
                print "Fastest Lap time: " + str(f_lap_time_hours) \
                    + " Hrs. " + str(f_lap_time_minutes) + " Mins. " \
                    + str(f_lap_time_secs) + " Secs. " \
                    + str(f_lap_time_hundredths) + " Hundr. "
    if options.dumpmode:
        d.close()
