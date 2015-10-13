Summary
==============================================================================

`ultrak498.py` is a python script for reading timing data from an Ultrak 498
printing stopwatch.

Usage
==============================================================================

To upload a race (or all races) from the Ultrak 498:

   * Ensure the upper left yellow switch is in the `OFF/UPLOAD` position.
   * Press `MODE` till `Upload All` is displayed.
   * Press `LAP/RESET/SELECT` to select the race number; skip to the next
     step to upload all stored races.
   * Press `S/S PRINT` to start the Upload.

Pinout
==============================================================================

The data port is located on the right side of the Ultrax 498 and is labeled
`PC`.  The data port uses an RJ11 connector.  When looking at the device, the
pins are labeled:

   1 2 3 4

The pinout is:

   * 1: GRND (Connect to ground of level converter)
   * 2: TX (Connect to RX of level converter)
   * 3: ? (No Connect)
   * 4: ? (No Connect)

Output is 4800 N81 TTL serial, no flow control.  A level converter is needed
to connect to a PC serial port.  Alternatively, a TTL Serial to USB converter
such as [FTDI Basic Break 5V](https://www.sparkfun.com/products/9716) from
[Sparkfun](http://www.sparkfun.com/) can be used to read data from the device.
See the Usage section for instructions on initiating a download.

Under Linux, the following two commands will display the raw output:

    % stty -F /dev/ttyUSB0 4800 raw
    % od -tx1 --width=5 /dev/ttyUSB0


Protocol
==============================================================================

The Ultrak 498 transmits fixed width fields in packed binary coded decimal.
Each field is five bytes wide.  Each byte represents a decimal value from 0 to
99 and is in little endian order (first nibble/digit is the ones, second
nibble/digit is the tens).

The first byte of each field indicates the field type.  The remaining bytes
represent the data for that field type.  There are six known field types.

   * 00: Race Header
   * 10: Lap Time
   * 20: Absolute Time
   * 30: Unknown
   * 40: Unknown
   * 50: Race Stop

Field Type 00: Race Header
------------------------------------------------------------------------------

This field represents the start of a race.  A race starts when the timer reads
zero, the timer is not running, and the start/stop button is pressed.

   * 0: Type
   * 1: Year
   * 2: Month
   * 3: Day
   * 4: Race ID

The date must be set within the timer for the year/month/day to be correct.
If no date has been set these fields are set to 10/1/1 respectively.

Field Type 10: Lap Time
------------------------------------------------------------------------------

This field represents the time elapsed since the last lap (the previous time
the yellow lap button was pressed).

   * 0: Type
   * 1: Minutes
   * 2: Seconds
   * 3: Hundreths
   * 4: Lap/Place

NOTE: Since the maximum value stored by a two digit binary coded decimal is
99, therefore, the maximum value for lap/place is 99.  The format can't
represent values over 100.  Thus, the lap/place rolls over to 0 each time a
multiple of 100 is reached.

Field Type 20: Absolute Time
------------------------------------------------------------------------------

This field represents the absolute time since the start of the race (the
previous time the black start/stop button was pressed).

   * 0: Type
   * 1: Minutes
   * 2: Seconds
   * 3: Hundreths
   * 4: Lap/Place

NOTE: See note above in regards to lap/place.

Field Type 30: Unknown
------------------------------------------------------------------------------

   * 0: Type
   * 1: Unknown
   * 2: Unknown
   * 3: Unknown
   * 4: Laps

Field Type 40: Unknown
------------------------------------------------------------------------------

   * 0: Type
   * 1: Unknown
   * 2: Unknown
   * 3: Unknown
   * 4: Laps

Field Type 50: Race Stop
------------------------------------------------------------------------------

This field represents the time the race ends.  A race ends when the start/stop
button is pressed while the timer is running.

   * 0: Type
   * 1: Minutes
   * 2: Seconds
   * 3: Hundreths
   * 4: Total Laps/Places

