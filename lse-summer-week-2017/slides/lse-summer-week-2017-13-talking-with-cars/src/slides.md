`Err... oh right, the plan.`

``` markdown
* The official goal: look at how a car works
* What arised: what can one do with modern car systems?
* Restrictions: I am not allowed to remove any part of the cars :(
```

---

## Test subjects

> Let's play with expensive toys

---

`VW Polo IV Facelift 1.4i 16V 80cv (~2006)`

![Image](rsc/poloIV.png)
<!-- .element: style="max-height: 500px;"-->

---


`VW Polo V 1.2i 12V 60cv (~2013)`

![Image](rsc/poloV.png)
<!-- .element: style="max-height: 500px;"-->

---


`Fiat Nuova 500C 1.2MPi 69cv (~2010)`

![Image](rsc/fiat500.png)
<!-- .element: style="max-height: 500px;"-->

---

## Talking with the cars

---

`ECUs`

``` markdown
* There can be as much as 70 Electronic Control Units (ECUs) in
  a modern car:
  * Engine
  * Transmission
  * Airbags
  * ABS
  * Cruise control
  * etc.
* ECUs talk to each other over the CAN Bus
* Every car after 2008 is supposed to support CAN (at different
  extent)
* Usually, CAN refers to both layer 1 (Physical) and 2 (Link) of
  the OSI Model. What about the top layers...?
```

---

`On Board Diagnostics`

``` markdown
## OBD-II
* On-board diagnostics (OBD) refers to "a vehicle's self-diagnostic
  and reporting capability"
* Allows devices to query informations about a car by plugging
  themselves to the automative network through OBD-II ports
* Provides Parameter IDs (PIDs) and Diagnostic Trouble
  Codes (DTCs). Some are standardized, others are manufacturer
  specifics (quick guess, which ones are the fun ones?)
```
<!-- .element: style="font-size: 0.40em;" -->

![Image](rsc/pi.png)
<!-- .element: style="max-height: 200px;"-->
![Image](rsc/obd2.png)
<!-- .element: style="max-height: 200px;"-->


---

`Controller Area Network`

``` markdown
## CAN
* The Controller Area Network (CAN) is a message-based protocol,
  using broadcast to communicate
* Messages are mostly composed of:
  * an arbitration ID (corresponding to the emitter) (11 or 29 bits)
  * data (8 bytes maximum in its classic implementation)
  * the other fields are already handled for us by socket-can
* Lots of protocols come on top of CAN (KWP, ISO-TP, UDS, ...)
```
<!-- .element: style="font-size: 0.40em;" -->

![Image](rsc/canmessage.png)

---

`SocketCAN`

```markdown
* On Linux, SocketCAN handles most of it for us.
* SocketCAN ties into the Linux networking stack.
* Applications can use standard C socket calls with a custom
  network protocol family, PF_CAN.
* This allows the kernel to handle CAN device drivers and to
  interface with existing networking hardware.
* The can-utils package provides several applications and tools
  to interact with CAN.
```
<!-- .element: style="font-size: 0.40em;" -->

![Image](rsc/socketcan.png)
<!-- .element: style="max-height: 300px;"-->

---

`In python`

```python
import can

is_11_bits = True

bus = can.interface.Bus(channel='can0', bustype='socketcan_native')

# Can be read as "2 bytes indicating the request for
# the field 0x0c (rpm), in mode 0x1"
data = [2, 0x1, 0x0c, 0, 0, 0, 0, 0]

if is_11_bits:
    msg = can.Message(arbitration_id=0x7df, data=data, extended_id=False)
else:
    msg = can.Message(arbitration_id=0x18DB33F1, data=data, extended_id=True)

bus.send(msg)
answer = bus.recv()
rpm = (answer.data[3] * 256 + answer.data[4]) / 4
```
<!-- .element: style="font-size: 0.45em;" -->

---



## Chronological analysis

Theory: Ok. Now, in practice...

![Image](rsc/topgear.gif)


---

`First dialogue`

```markdown
* My 2006 Polo was too old, so I took my grandmother's car
* I was thus able to get an OBD answer on the 2013 Volkswagen Polo
* We are behind a gateway, so the only messages we receive are
  answers from our queries.
* By using the 11 bits default arbitration ID (0x7DF), I could
  get various information
```
<!-- .element: style="font-size: 0.50em;" -->
``` bash
pi@canard:src$ candump -a -d -e -x can0
  can0  TX - -       7DF   [8]  02 01 0C 00 00 00 00 00   '........'
  can0  RX - -       7E8   [8]  04 41 0C 0D 2C AA AA AA   '.A..,...'
pi@canard:src$ candump -a -d -e -x can0
  can0  TX - -       7DF   [8]  02 01 05 00 00 00 00 00   '........'
  can0  RX - -       7E8   [8]  02 41 83 AA AA AA AA AA   '.A......'
```
<!-- .element: style="font-size: 0.50em;" -->
```markdown
Temperature T can be -40 < T < 215.
So T = 0x83 - 40 = 91ºC
```

---


`Getting more info`

```markdown
* Communicating via OBD allows one to query lots of standard
  data (see wikipedia page for OBD-II PIDs) - ~140 of them
```
```markdown
* There are the classic ones you would want to find on
  your dashboard:
  * RPM
  * Speed
  * Fuel Level
  * etc.
```
```markdown
* Sadly, some other interesting ones are constructor specific:
  * Steering wheel position
  * Brake and clutch pedals position
  * Gearbox state
  * Lights and blinkers
```

---

`Displaying everything`

![Image](rsc/polo1.gif)
<!-- .element: style="max-height: 250px;"-->
![Image](rsc/polo2.gif)
<!-- .element: style="max-height: 250px;"-->

---

`O_RDONLY`

```markdown
* Nice, we are able to read. Can we do anything else ?
* First issue: what protocol am I talking too ?
  * KWP2000 ?
  * UDS ?
  * ISO-TP ?
  * VW-TP 2.0 (like, really?)
  * etc.
* Let's try sending classic messages and see if we get
  any answer on the 2013 Polo
```

---

`UDS`

```markdown
* I was able to initiate a UDS diagnostic session on it
* Allows various operation, like reset or query a specific ECU,
  read DTC information...
```
``` bash
pi@canard:~/src $ candump -a -d -e -x can0 # Diagnostic session
  can0  TX - -  7E0   [8]  02 10 03 00 00 00 00 00   '........'
  can0  RX - -  7E8   [8]  06 50 03 00 32 01 F4 AA   '.P..2...'
```
```markdown
* However, nice stuff (like "dump the firmware") are available
  through security sessions only.
* This requires authentication through a challenge.
```


---

`Well done, Volkswagen`

```markdown
* And sadly, the job has been correctly done:
  * 4 bytes seed, different at each try
  * more than 3 seconds required between each try
  * Freezes for more than 10 minutes after a few failed attempts
```
<!-- .element: style="font-size: 0.45em;" -->
``` bash
# Timestamps have been removed for clarity
pi@canard:~/src $ ./polo-can/scripts/kwp2000.py
TX: ID: 07e0    000    DLC: 8    02 10 03 00 00 00 00 00
RX: ID: 07e8    000    DLC: 8    06 50 03 00 32 01 f4 aa
Diagnostic session susccessfuly opened
TX: ID: 07e0    000    DLC: 8    02 27 03 00 00 00 00 00
RX: ID: 07e8    000    DLC: 8    06 67 03 fe 44 7f 0c aa
Security session seed: [254, 68, 127, 12]
TX: ID: 07e0    000    DLC: 8    06 27 04 fe 44 7f 0c 00
RX: ID: 07e8    000    DLC: 8    03 7f 27 35 aa aa aa aa
Bad key in security session init
```
<!-- .element: style="font-size: 0.45em;" -->
``` markdown
* Break this:
  * Bruteforce ? Nope.
  * Timing attacks ? Nope.
  * Disassemble the car and– NOPE.
  * Find a way to get pieces from a repair shop (tedious)
```
<!-- .element: style="font-size: 0.45em;" -->

---

## Hum, too old or too recent...
```markdown
So, let's recap:
- My car: too old
- Grandmother's car: too recent
- Family's car: Lancia Voyager 2014, too recent
  (but has UConnect, maybe for another time *wink wink*)

What's left... Oh.
```
```markdown
Moooooom?
```
<!-- .element: class="fragment" -->

---

`Italy, 2010`

```markdown
* I wanted another car, which would be a bit more talkative
  (AKA no gateway)
* I thus asked my mother which year her convertible Fiat 500 was
  released on
* I smiled at the answer. She, however, did not.
```
```markdown
* I stole the keys one night (joke)
* Plugged my computer to the OBD-II port
* Ignition
* And– oh damn, yes, it talks.
```

```bash
pi@canard:~/src 21:47:10 $ candump -a -d -e -x can0 > test
^Cpi@canard:~/src 21:47:14 $ cat test | wc -l
2225
```

---

`A bit of RE`

```markdown
* Lots of messages are broadcast, but from few different
  arbitration IDs (uses extended CAN).
* Surely enough, some data evolves when performing actions
  in the car
* Fun thing to do: discover what each message means!
* Tricky with candump, but canmonitor helps a lot by grouping
  messages by arbitration IDs
```

---

`python-can-monitor`

![Image](rsc/canmonitor.gif)
<!-- .element: style="max-height: 500px;"-->

---


`./canmonitor.py can0`

```bash
# Line 1: At stop, handbrake up, contact off, clutch and brake pedals released
# Line 2: Driving, handbrake down, contact on, downshifting, braking

# Speed (4 times) - Each wheel sensor ? Different but close times ?
0218a006     00 2C 00 2C 00 2C 00 2C       # 00 2C => Default value if speed < 3 km/h
0218a006     03 D3 03 CF 03 DO 03 CF       # 03 D3 => 0x3 * 16 + 0xd3 / 16 = 61 km/h

# Clutch pedal wrt accelerator (byte 5)
0628a001     00 0F 00 80 0A 00 00 21       # 00: Clutch pedal released
0628a001     00 0F 00 80 07 20 00 21       # 20: Depressing clutch pedal without accelerating

# Brake pedal (byte 3 - bits 4-7)
0810a000     01 FF 18 00                   # 1x: Brakes pedal released (brake lights off)
0810a000     01 FF 78 00                   # 7x: Brakes pedal normal/high depression

# Doors (byte 2), contact (byte 2), handbrake (bytes 0 and 6), ...
0a18a000     20 09 10 79 00 47 20 D4       # Handbrake up, contact off
0a18a000     00 09 40 77 00 5F 00 05       # Handbrake down, contact on

# Guess :)
0c28a000     21 02 24 05 20 17
0c28a000     15 17 03 06 20 17

```
<!-- .element: style="font-size: 0.40em;" -->

_Yup, the last one is the time and date, readable in hex (9:02PM - 05/24/17)_
<!-- .element: class="fragment" -->
<!-- .element: style="font-size: 0.40em;" -->


---

![Image](rsc/interface.gif)

---

`What can we do with that ?`

```markdown
* Something useful for humanity
* Something challenging
* Something I will be able to put on a resume
```

---

`Ooooor... `

---

`Introducting CANPad`

```markdown
With a steering wheel, a brake pedal and a gas pedal, we
can drive any car in any video game. So that's what I did :)
```
```markdown
CANPad creates a virtual XBox-like gamepad through uinput
and converts CAN data to gamepad inputs.
```

---

`How CANPad works`
![Image](rsc/canpadv1.png)


---

`"features" and limitations`

```markdown
* Available commands:
  * Gas pedal [0 -> 255]
  * Brakes pedal [0 -> 2]
  * Clutch pedal [0 | 1] (unused atm)
  * Steering wheel [-0x450 -> 0x450] (approximately)
  * Handbrake [0 | 1]
* Not as accurate as a real gamepad (processing time a bit long),
  but fair enough
```
```markdown
* On/Off switch
  * Data sent only when the car is in "City mode"
  * Button available on the dashboard
  * Enable or disable the gamepad easily
```
```markdown
* However:
  * Gas pedal range brought back to [0 | 1] (gas is expensive!)
  * I discovered how usefull ESP was.
  * Controller's simplicity limits it to VDrift
```

---

`Demonstation - VDrift`

![Image](rsc/vdrift.png)

(Full version on YouTube [here](https://www.youtube.com/watch?v=-q2togYPXas))

---

`But I really wanted to drift...`

`Oh wait. I made another version!`
<!-- .element: class="fragment" -->

---


`How CANPad2 works`

![Image](rsc/canpadv2.png)


---

`What really changes`

```markdown
* Nicer game requires specific controllers, so I just
  plug a XBox controller in it, and hijack the inputs
* No need for a virtual controller anymore (but need
  the real one)
```
```markdown
* Changes in command:
  - Gas pedal can be adjusted
  - Boost available when pressing harder on gas
  - Steering wheel rotation can be (and was) adjusted.
  - Found direct command to query handbrake, so no more delay
```

---

`Demonstation - Dirt Showdown`

![Image](rsc/dirt.png)
<!-- .element: style="max-height: 400px;"-->

(Full version on YouTube [here](https://www.youtube.com/watch?v=bB7m7J3ioQw))

---

`What's left ?`

```markdown
* Get the gearbox status to put the game in manual (and reverse)
* Create a better gamepad to be able to race on Mac or Windows
* Try new stuff (security session on the Fiat, find other
  proprietary commands, etc)
```

![Image](rsc/end.gif)

---

`Thanks and references`

```markdown
Thanks to:
* Alexey Chernikov, Julio Baena and Robert 'G8RPi' for
  helping me finding the steering wheel proprietary PID
* Alexandre Blin for python-can-monitor
* All the random guy asking the right questions on forums
  accross the internet!
```
```markdown
References (way too much, but here are some interesting ones):
* The Car Hacker's handbook
* http://illmatics.com/carhacking.html
* https://en.wikipedia.org/wiki/OBD-II_PIDs
* http://www.fiatforum.com/
* http://jazdw.net/tp20
* http://marco.guardigli.it/2010/10/hacking-your-car.html
* Lot more here: https://github.com/P1kachu/talking-with-cars
* Contact: `https://twitter.com/0xP1kachu`
```

---

`And, thank you`

![Image](rsc/fans.png)
<!-- .element: style="max-height: 400px;"-->

