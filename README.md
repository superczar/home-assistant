# Home Assistant

A running summary of my system migration from Domoticz to Home-Assistant

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

### Router –

Edgerouter X (ER-X) in load balancing mode

### Access Points

Orbi RBR50, Orbi RBK 50, Orbi RBS20. The former 2 cover 1 floor each and the RBS20 covers the frontyard.

My house gets frequent short brownouts and the Orbi system does not take handle power outage very well. They are all powered by 12V 7AH batteries charging with a constant float of 12.4V

### Switches

A mix of multiple partially daisy-chained switches. The loadbalanced WAN from ER-X goes to the switch br0 on the RBR50 that then goes to 4 switches in different parts of the house (switch 3 and 4 are daisychained)

Someday I will clean this up, for now, the re-cabling does not seem to be worth the effort

1.
## Lights

- LIFX : 5 entities that use the HA native LIFX integration
- Hue : 10 entities that use the HA native LIFX integration
- ESP8266 – 1 ESP8266 based light bulb that was flashed to Tasmota and uses the mqtt integration. Plan to get 6 more of these
- Yeelight: 1 bulb that uses the yeelight LAN control integration

Notes:

- The LIFX bulbs are very bright and color control is very accurate. Unfortunately their wi-fi connection is flakey and requires a restart every now &amp; then.Cannot recommend them anymore
- The Hue bulbs are amazingly stable. They have been running stable for years with no flakiness whatsoever. Maybe it&#39;s because they use zigbee. Unfortunately they are not bright enough (at most comparable to a 60W incandescent) and I would have hoped for brighter output given the price
- **ESP8266 Tasmota** : My current favorite. The only issue is that finding the right one is a bit of a hit&amp; miss. Most lights available on Amazon India (or elsewhere) are based on generic Tuya/ Smartlife firmware .
  - Now one can use the Tuya/smartlife integration directly on HA but using the MQTT integration is a lot more reliable
  - Unfortunately the internal hardware on these bulbs could be anything. Since you can&#39;t really open these lightbulbs to get access to the serial ports, you need to make sure that you are getting one which is based on the ESP8266
  - Amazon India sells ESP8266 bulbs under their housebrand Solimo. They are easily flashed to Tasmota with tuya-convert
  - The 12W variant is plenty bright – equivalent to a 100W incandescent
- Yeelight: Good &amp; reliable with LAN control. Slightly pricier than the Tuya

1.
## Switches
