`Some context`

``` markdown
* People liked my presentation about playing with my mom's car
* Some want to try that, but it is an expensive kind of research
* We still need to show people that car hacking is no joke
* So I joined Quarkslab to create an inexpensive car hacking CTF
```

![Image](rsc/sponsors.jpg.png)
<!-- .element: style="max-height: 400px;"-->

---

`Let's go to the car dealer`

``` markdown
* The goal: to offer a first approach at car hacking
* First we need some material to work on: a car
* A real car is expensive, and you only break it once
* Soooo... We bought an RC car!
```

![Image](rsc/naked.jpg.png)
<!-- .element: style="max-height: 400px;"-->


---

`We need some network to attack`

``` markdown
* 4 wheels don't make it a real car
* For our purpose, we need to add some attack vectors
* Let's add a CAN bus and some ECUs to our RC car
```

---

`Crash course - ECUs and CAN`

``` markdown
Electronic Control Units are any embedded system that controls
one or more of the electrical system or subsystems in a vehicle.
-- Wikipedia
```

``` markdown
Controller Area Network (CAN bus) is a robust vehicle bus
standard designed to allow microcontrollers and devices to
communicate with each other without a host computer.
-- Wikipedia
```

---

`How to create a CAN bus ?`

```markdown
* We took two physical devices, a Teensy 3.2 and a Raspberry Pi
* These two devices talk on the same physical CAN bus
* On each device are created multiple virtual ECUs
* The CTF player plugs himself on the bus through a third device
```

![Image](rsc/naked-circuit.jpg.png)
<!-- .element: style="max-height: 400px;"-->

---

`The CAN protocol: PiCANchu`

```markdown
* We needed some protocol to allow the ECUs to talk
* Some implementations of known protocols already exist, but
  it's always better to reimplement everything yourself (no,
  it is not)
* So I created a protocol from my memories of my past analysis
* This gave something like UDS with a lot less capabilities, and
  some minor changes (let's call this `UDSLite`)
```

``` markdown
Recognized message format:
* data[0]: Number of bytes of interest
* data[1]: Command or ECU specific indicator
* data[2-7]: Optional parameters

Example:
> data: [4, 1, 2, 3, 4, 5, 6, 7]
* 4 bytes of interest (5, 6 and 7 will be discarded)
* 1      : Command
* 2, 3, 4: Parameters

```


---

`Integrating the CAN bus to the RC car`

```markdown
* Nice, we have a CAN bus (quite shy, but still)
* We need to integrate it to the RC car, so that it affects
  the car's behavior
* Here enters the Teensy
```

![Image](rsc/first-impression.jpg.png)
<!-- .element: style="max-height: 400px;"-->

---

`PWM and teensy`

```markdown
* The radio controller sends data into the RC receiver
* The receiver forwards them into the direction's
  servo-motor and to the power controller through PWM.
* Let's cut the wires between the receiver and the motors,
  and add the teensy in between
```

![Image](rsc/teensy-2.jpeg)
<!-- .element: style="max-height: 400px;"-->


---

`Our first ECUs: VirtEngine and VirtSteering`

```Markdown
* Now our inputs go through the teensy, but we might want
  to control them.
* These two new ECUs can apply multipliers on the received
  signals before forwarding them.
* If you shutdown the ECU, it won't forward its signal
  anymore (==> losing your steering, for example)
* Bonus: I can control the car with my computer now
```

```bash
pi@tomoyo:~ $ candump -d -x -e -a can0
can0  RX - -  726   [5]  04 32 00 00 64    '.2..d'  # Engine
can0  RX - -  728   [5]  04 31 03 00 64    '.1..d'  # Steering
```

---

`I need to add some noise now`

``` markdown
* I have about 8 messages per second on my bus right now
* My mom's Fiat had around 575 msgs/s
* What can I add ?
```

---

`*EUROBEAT INTENSIFIES*`

``` markdown
* Let's add an MPD server on the raspberry, along with a speaker
* We can send metadata on the bus, like the song's name
* And we can even control the music from the CAN
```

``` bash
pi@tomoyo:~ $ candump -d -x -e -a can0 | grep 725
can0  TX - -  725   [8]  07 33 48 65 72 6F 20 28   '.3Hero ('
can0  TX - -  725   [7]  06 33 00 00 05 28 81      '.3...(.'
can0  TX - -  725   [8]  07 33 65 72 6F 20 28 39   '.3ero (9'
can0  TX - -  725   [8]  07 33 72 6F 20 28 39 30   '.3ro (90'
can0  TX - -  725   [8]  07 33 6F 20 28 39 30 65   '.3o (90e'
can0  TX - -  725   [8]  07 33 20 28 39 30 65 75   '.3 (90eu'
can0  TX - -  725   [8]  07 33 28 39 30 65 75 72   '.3(90eur'
can0  TX - -  725   [7]  06 33 00 00 07 28 81      '.3...(.'
can0  TX - -  725   [8]  07 33 39 30 65 75 72 6F   '.390euro'
can0  TX - -  725   [8]  07 33 30 65 75 72 6F 73   '.30euros'
can0  TX - -  725   [8]  07 33 65 75 72 6F 73 2E   '.3euros.'
can0  TX - -  725   [7]  06 33 00 00 08 28 81      '.3...(.'
can0  TX - -  725   [8]  07 33 75 72 6F 73 2E 6D   '.3uros.m'
can0  TX - -  725   [8]  07 33 72 6F 73 2E 6D 70   '.3ros.mp'
can0  TX - -  725   [7]  06 33 00 00 09 28 81      '.3...(.'
can0  TX - -  725   [8]  07 33 6F 73 2E 6D 70 33   '.3os.mp3'
can0  TX - -  725   [8]  07 33 73 2E 6D 70 33 29   '.3s.mp3)'
can0  TX - -  725   [8]  07 33 2E 6D 70 33 29 20   '.3.mp3) '
can0  TX - -  725   [7]  06 33 00 00 0A 28 81      '.3...(.'
can0  TX - -  725   [8]  07 33 6D 70 33 29 20 2D   '.3mp3) -'
```
<!-- .element: style="font-size: 0.40em;" -->
_Now playing: Chris Stanton - A Perfect Hero_
<!-- .element: style="font-size: 0.40em;" -->

---

`Putting everything together`

![Image](rsc/full-1.jpg.png)
<!-- .element: style="max-height: 300px;"-->
![Image](rsc/full-2.jpg.png)
<!-- .element: style="max-height: 300px;"-->


---


`Goodies`

```Markdown
* We added some stuff for more fun:
  * OLED screen connected to the Teensy
  * 3D printed drift wheels
  * The LEDs are on their way
```

![Image](rsc/oled-screen.jpg.png)
<!-- .element: style="max-height: 300px;"-->
![Image](rsc/3dprinted.jpg.png)
<!-- .element: style="max-height: 300px;"-->

---

`Currently, in the beast`

![Image](rsc/schema.jpg.png)
<!-- .element: style="max-height: 500px;"-->

---

`Little demo`

![Image](rsc/beautiful.png)
<!-- .element: style="max-height: 500px;"-->


---

`What's left`

```markdown
* Add the LED lights and ECUs to control them individually
* Add new ECUs to make some noise and functionalities (PR welcome)
* If I can borrow my mom's car again, then maybe...
* Tamiya sells RC Tanks too.
```

![Image](rsc/abrams.png)
<!-- .element: style="max-height: 400px;"-->
<!-- .element: class="fragment" -->

---

`Thanks`

![Image](rsc/hard.jpg.png)
<!-- .element: style="max-height: 500px;"-->


