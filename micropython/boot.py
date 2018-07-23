# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import webrepl
import network
import time
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
	sta_if.active(True)
	sta_if.connect('WLAN_SSID','WLAN_PSK')
	while not sta_if.isconnected():
		pass
sta_if.ifconfig(('IP', 'NETMASK', 'GATEWAY', 'DNS'))
webrepl.start()
gc.collect()
