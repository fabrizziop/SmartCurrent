import time
import usocket
from machine import Pin, ADC
from utime import sleep, ticks_ms
from nodemcu_gpio_lcd import GpioLcd

CALIB_CONST_MUL = 0.08076
LIST_MAX_LENGTH = 60
IP_RECEIVER = "YOUR_SERVER_IP"
PORT_RECEIVER = 8000
IOT_RECEIVER = usocket.getaddrinfo(IP_RECEIVER, PORT_RECEIVER)[0][-1]
PROGRAM_NAME = "SMARTCURRENTv0.1"
WARMUP_TIME = 60
current_warmup = 0
pin_ctrl = Pin(15, Pin.OUT, value=0)
pin_adc = ADC(0)
lcd = GpioLcd(rs_pin=Pin(16),enable_pin=Pin(5),d4_pin=Pin(4),d5_pin=Pin(0),d6_pin=Pin(2),d7_pin=Pin(14),num_lines=2, num_columns=20)
lcd.putstr(PROGRAM_NAME+"\n"+"  DO NOT TOUCH  ")
time.sleep(10)
lcd.clear()
while current_warmup < WARMUP_TIME:
	lcd.putstr("TIME REMAINING:\n        "+str(WARMUP_TIME-current_warmup))
	current_warmup += 1
	time.sleep(1)
	lcd.clear()
lcd.putstr(IP_RECEIVER + "\nPORT:" + str(PORT_RECEIVER))
time.sleep(15)
lcd.clear()
def clear_and_print(string_to_print):
	lcd.clear()
	lcd.putstr(string_to_print)
	
def obtain_zero():
	clear_and_print("   OBTAINING\n      ZEROS")
	pin_ctrl.value(1)
	time.sleep(0.25)
	a = 0
	for i in range(50):
		time.sleep(0.02)
		a += pin_adc.read()
	pin_ctrl.value(0)
	time.sleep(0.25)
	return a//50
	
def obtain_raw_rms(zero):
	ct = time.ticks_ms()
	rms_sum = rms_amount = 0
	while time.ticks_ms() < (ct+1000):
		rms_sum += (zero - pin_adc.read()) ** 2
		rms_amount += 1
	calculated_rms = (rms_sum / rms_amount)**0.5
	return max(calculated_rms-2,0)

def convert_to_real_rms(calculated_rms):
	return calculated_rms * CALIB_CONST_MUL

def print_current(real_rms, zero, extra):
	lcd.clear()
	lcd.putstr(str(real_rms)[:5] + " A; Z: "+ str(zero)+ "\n"+extra)

def convert_to_bytearray_4socket(nonce, zero, val_list):
	tb = bytearray()
	tb.append(nonce[0])
	tb.append(nonce[1])
	tb.append(zero)
	for i in range(0, LIST_MAX_LENGTH):
		tb.append(val_list[i])
	return tb

def send_socket(bytearray_to_send):
	s = usocket.socket()
	s.settimeout(0.5)
	try:
		s.connect(IOT_RECEIVER)
		sdat = s.send(bytearray_to_send)
		s.close()
		return "  DATA SEND OK  "
	except:
		return " DATA SEND FAIL "

def main_loop():
	needs_calibration = True
	list_nonce = [0,0]
	actual_list = []
	for i in range(0, LIST_MAX_LENGTH):
		actual_list.append(0)
	while True:
		if needs_calibration:
			zero = obtain_zero()
			needs_calibration = False
		a = obtain_raw_rms(zero)
		b = convert_to_real_rms(a)
		actual_list.append(int(min(a//2,255)))
		actual_list.pop(0)
		list_nonce[0] += 1
		if list_nonce[0] == 255:
			list_nonce[0] = 0
			list_nonce[1] += 1
		if list_nonce[1] == 255:
			list_nonce = [0,0]
			needs_calibration = True
		for i in range(0,10):
			time.sleep(0.05)
		#print(a)
		#print(actual_list)
		#print(list_nonce)
		#print(convert_to_bytearray_4socket(list_nonce, actual_list))
		status_to_print = send_socket(convert_to_bytearray_4socket(list_nonce, int(min(zero//4,255)), actual_list))
		print_current(b, zero, status_to_print)
		gc.collect()

main_loop()
