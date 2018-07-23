import socket
import time

CALIB_CONST_MUL = 0.08076
s = socket.socket()
s.bind(("SERVER_IP",8000))
s.listen(100)

def simple_data(ba):
	nonce = ba[0] + (ba[1] * 256)
	zero = ba[2] * 4
	last_current = ba[62] * 2 * CALIB_CONST_MUL
	return [nonce, zero, last_current]

def get_name_to_write():
	f = open("cwrite","r")
	n = str(int(f.read()) + 1)
	f.close()
	f = open("cwrite","w")
	f.write(n)
	f.close()
	while len(n) < 8:
		n = "0" + n
	return str(n)
	
def get_data():
	conn, addr = s.accept()
	sdat = conn.recv(63)
	conn.close()
	# ~ print(sdat)
	return simple_data(sdat)
#creating file

obj_to_write = open(get_name_to_write(), "w")

while True:
	temp_data = get_data()
	print(temp_data)
	obj_to_write.write(str(int(time.time())) + "," + str(temp_data[0]) + "," + str(temp_data[1]) + "," + str(temp_data[2]) + "\n")
	obj_to_write.flush()

