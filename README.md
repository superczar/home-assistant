# Home Assistant

A running summary of my system migration from Domoticz to Home-Assistant.

The long term plan is to have HA do all of the heavy lifting but to keep domoticz running primarily for sensors and logging.

# Table of Contents

**[Home Assistant 1](#_Toc44342239)**

**[Equipment 1](#_Toc44342240)**

**[1)](#_Toc44342241)****Servers 1**

**[2)](#_Toc44342242)****Network 1**

[a)Router 1](#_Toc44342243)

[b)Access Points 1](#_Toc44342244)

[c)Switches 1](#_Toc44342245)

**[3)](#_Toc44342246)****Voice Control/ Smart Speaker 1**

**[4)](#_Toc44342247)****Lights 1**

**[5)](#_Toc44342248)****Switches 1**

**[6)](#_Toc44342249)****Hubs 1**

**[7)](#_Toc44342250)****Media Players and multi-room audio 1**

**[8)](#_Toc44342251)****Sensors 1**

# Equipment

1.
## Servers

- Proxmox hypervisor running 4 VMs (i5-4130 , 12GB RAM, 120GB SSD, 4TB HDD)
  - Home-Assistant
  - HAbridge running on an existing openmediavault VM
- Domoticz running on a RPi2

1.
## Network

The network setup is slightly convoluted as my primary ISP uses CGNAT. The primary is a 100mbps fiber connection while the secondary is a Point-to-point wifi link with my housing community wireless distribution system (50mbps fiber)

While my primary ISP is fairly reliable , they unfortunately use CGNAT. For external access, I have setup an Amazon Lightsail VPN that I openvpn to. Details here.

1.
### Router

Edgerouter X (ER-X) in load balancing mode

1.
### Access Points

Orbi RBR50, Orbi RBK 50, Orbi RBS20. The former 2 cover 1 floor each and the RBS20 covers the frontyard.

My house gets frequent short brownouts and the Orbi system does not take handle power outage very well. They are all powered by 12V 7AH batteries charging with a constant float of 12.4V

1.
### Switches

A mix of multiple partially daisy-chained switches. The loadbalanced WAN from ER-X goes to the switch br0 on the RBR50 that then goes to 4 switches in different parts of the house (switch 3 and 4 are daisychained)

Someday I will clean this up, for now, the re-cabling does not seem to be worth the effort

1.
## Voice Control/ Smart Speaker

1. **Echo** – 6 devices, 2 X Echo Original, 2X Echo Dot, 1 X Echo Show, 1 X Echo Spot – Linked via habridge
2. **Homepod** – 2 devices – Linked via HA native homekit integration
3. **Google Nest hub** – I had picked this on whim but turns out I don&#39;t like the cloud only model used by Google . It&#39;s unreliable and slow. Not integrated and left stand-alone

1.
## Lights

1. **LIFX** : 5 entities that use the HA native LIFX integration
2. **Hue** : 10 entities that use the HA native LIFX integration
3. **ESP8266** – 1 ESP8266 based light bulb that was flashed to Tasmota and uses the mqtt integration. Plan to get 6 more of these
4. **Yeelight** : 1 bulb that uses the yeelight LAN control integration

Notes:

1. The LIFX bulbs are very bright and color control is very accurate. Unfortunately their wi-fi connection is flakey and requires a restart every now &amp; then.Cannot recommend them anymore
2. The Hue bulbs are amazingly stable. They have been running stable for years with no flakiness whatsoever. Maybe it&#39;s because they use zigbee. Unfortunately they are not bright enough (at most comparable to a 60W incandescent) and I would have hoped for brighter output given the price
3. **ESP8266 Tasmota** : My current favorite. The only issue is that finding the right one is a bit of a hit&amp; miss. Most lights available on Amazon India (or elsewhere) are based on generic Tuya/ Smartlife firmware .
  - Now one can use the Tuya/smartlife integration directly on HA but using the MQTT integration is a lot more reliable
  - Unfortunately the internal hardware on these bulbs could be anything. Since you can&#39;t really open these lightbulbs to get access to the serial ports, you need to make sure that you are getting one which is based on the ESP8266
  - Amazon India sells ESP8266 bulbs under their housebrand Solimo. They are easily flashed to Tasmota with tuya-convert
  - The 12W variant is plenty bright – equivalent to a 100W incandescent
4. Yeelight: Good &amp; reliable with LAN control. Slightly pricier than the Tuya

1.
## Switches

1. Wemo: The device that got this hobby started. I had picked a Wemo gen1 motion sensor/ switch combo sometime back in 2013 on a trip to the UK. I don&#39;t think IoT or smart devices were available back home at that point in time  . The plug still works and is setup with my garden floodlight using the HA native Wemo integration
2. Sonoff/ Smartlife devices flashed to ESP8266 TASMOTA: 7 devices. 5 work as normal switches while 2 need a special mention
  - 1 X 2 wired to cooling fans for my 2 AV Receiver. They are linked to automation to switch them on if the respective AV receiver changes state to On and vice-versa

1.
## Hubs

1. **Smartthings** : Was used extensively at one point in time. Currently in use for 5X Z-wave smoke alarms . Not integrated into HA as no real need for integration
2. **Hue Hub**
3. **Yale wifi bridge** : Used for the main door lock (YDM7116) . Unfortunately no documentation on API available. Wireshark capture didn&#39;t yield anything of value in the first pass. Currently in use as a standalone bridge with its own phone app. Need to get down to solving for this integration at some point in time.

1.
## Media Players and multi-room audio

1. Denon X3500 – Shows up in HA with no fuss. Also used for driving the exhaust automation .
2. Marantz SR6010 - Shows up in HA with no fuss. Also used for driving the exhaust automation . On a side note, the cooling automation is quite important for me as both the AVRs are housed in closets and the closet temperatures shoot up drastically if the exhaust fan is not activated (more details in sensors)
3. DTS Play-fi – Not integrated into HA , need to figure this out
  1. 2 X Klipsch Gate – Frontyard and Guest room speakers
  2. 1 X Paradigm PW Link – Kitchen Speakers
  3. 1X Paradign PW Amp – Bedroom Speakers
4. Homepods

1.
## Sensors

### Temperature and Humidity

1. DS18B20 – 3 units with a One wire link to Domoticz RPi GPIO. Integrated to HA with Rest calls to domoticz
2. BMP085 – 1 unit connected to Domoticz GPIO. Integrated to HA with Rest calls to domoticz
3. ESP8266 Tasmota – 2 unit with a DHT sensor sending MQTT data to domoticz – This is used to monitor AV Receiver closets

### Smoke / Fire/ Carbon Monoxide

1. 5X Z-wave First Alert CO/ Smoke Sensors – Linked to Smartthings and not integrated with HA or domoticz. May do it someday but not a priority

### Power Monitoring

1. [Mysensors](https://www.mysensors.org/build/connect_radio) SCT013, Arduino and nrf – Retired last week. While it worked for almost 5 years, the wireless connection was unreliable and the SCT-013 is not very precise
2. PZEM004T and ESP8266 – Uses [arendst/tasmota](https://tasmota.github.io/docs/PZEM-0XX/)

Notes : I have a 3 phase supply and the older SCT013 used a CT sensor on the neutral phase at the distribution box to return a consolidated reading for all phases.

My plan was to wire the PZEM004T in the same way but realized that the readings were off because the PZEM004T power factor calculation would be off due to the phase difference .

Now I have ordered 2 more pairs to have 3 separate sensor reading for each phase that can be combined later on in Grafana

1.
## Remote Control

1. 2X Harmony hub – 1 for living room TV, audio and HVAC, 1 for Home Theater projector, Audio and HVAC
2. 1 X ESP8266 Tasmota IR – Based on a Oakter remote flashed to run Tasmota IR. The HVAC control required a custom called [tasmota\_ihvac](https://www.home-assistant.io/integrations/tasmota_irhvac)
