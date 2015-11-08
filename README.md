# dt2000
## Purpose
Python program to read data from DT2000 logging stopwatch.

Many thanks to Eric Sorton whose [ultrak498 project](https://github.com/esorton/ultrak498) formed the basis of this work.

The program will read the watch data via a serial port or from a previously dumped binary 'dump file'. The watch data is then dumped in CSv format, for import into a spreadsheet or database.

You can dump multiple 'races', with multiple 'laps'; with a sumary of average and fastst lap at the end of each race.

For my use case, each lap is actually a finisher of a single race. Lap times are summed to give each finishers elapsed time.

## Hardware
None required! OK, that's not entirely true, except that you could just read the contents of a dump file.

You will need a [DT2000 watch](http://www.supersporty.co.uk/index.php?route=product/product&product_id=106), currently 57 GBP.

They sell a [cable and software](http://www.supersporty.co.uk/index.php?route=product/product&product_id=107) to go with this watch, but it's another 55 of your GBP.

I'm targetting Linux based solutions, specifically the Raspberry Pi, and so (up to a point) this is a waste of money.

### The Cable
This is where the fun begins. The data socket on the watch is a 3.5mm. audio cable. My current prototype uses a stereo cable with one end chopped off. I suspect that a mono cable will produce a better connection. This is after all, a receive-only operation.

Eric's project gave me the clue to try 4800 8N1 on the serial port, but curiously I had no luck. Framing errors everywhere.

In desperation I attached my logic analyser, and eventually tried it in 'invert' mode. At last there was consistent data, that could conceivably be timing data.

Working on the same basis as the 498 project, it became clear that indeed the data was sent in 5 byte chunks.

### The Inverter
Unfortunately, it's not possible to set the Pi's uart to read inverted logic. There were two ways forward: 1) Hardware inversion, 2) Software inversion.

Always preferring software over hardware(!), I tried the PIGPIO package which had an 'invert' mode. This allows the Ps's GPIO pins to work as a software serial port, and also to read inverted signals. Ideal. At only 4800 bits per sec, it should have been easy. Unfortunately, it repeatedly corrupted some of the bytes it read from the watch and I decided to bite the bullet and try a hardware solution.

**intr2.py** was my attempt at using PIGPIO.

By now you will have realised why they sell a cable and software @ £55. without wishing to risk the money, I would guess that the cable does the inversion and the USB cable provides the serial port. If you wish to use the cable with this software, I would guess that it would 'just work'.

Of course, £55 is a little over the top, but they do provide (Windows) software too, I suppose (and need to make a small profit). You might find something on ebay. You'll need USB to 3.3V TTL not RS232. It's got to **invert**, though.

My solution is to use an Arduino Pro Mini, programmed to invert an input based on change interrupts. See 'Invert' for details.

The output form the Arduino is fed to the RX uart of the Pi.

This is overkill in some ways, but in my case will drive buzzers, switches and other stuff in due course. A transister and a few resistors will do the same (inverting) job.

#Usage
Get usage help:

`$python dt2000.py -h`

Typically reading from the serial port:

`$python dt2000.py -f /dev/ttyAMA0`

Dump the data to a file called "dump" (should make this an arbitrary filename):

`$python dt2000.py -f /dev/ttyAMA0 --dump`

Replay the dump file:

`$python dt2000.py -f dump`

Save the output to a file:

`$python dt2000.py -f /dev/ttyAMA0 -o results.csv`

More verbose output:

`$python dt2000.py -f /dev/ttyAMA0 --debug`