import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import matplotlib.dates as md
from yattag import Doc
import base64
import numpy as np
import datetime
import time
import gc
graph_location = "/home/YOUR_USER/iot_main/http/"

INTEGRATE_PARAMETER = 0.01
HIGH_DET = 1.15
LOW_DET = 0.85
DATE_ROLLOVER = 1800

DATE_ROLLOVER_LAST = 180

def get_names_to_read():
	f = open("cwrite","r")
	n = int(f.read())
	f.close()
	flist = []
	for i in range(1, n+1):
		n2 = str(i)
		while len(n2) < 8:
			n2 = "0" + n2
		flist.append(n2)
	return flist

def get_all_data(file_name_list):
	dates = []
	currents = []
	for file_name in file_name_list:
		date_cons = 0
		avg_cons = 0
		current_average = 0
		start_date = 0
		init_line = True
		if file_name == file_name_list[-1]:
			cur_rollover = DATE_ROLLOVER_LAST
		else:
			cur_rollover = DATE_ROLLOVER
		with open(file_name,"r") as a:
			for line in a:
				tline = line.split(",")
				cur_date = int(tline[0])
				cur_current = float(tline[3])
				if init_line or cur_date >= start_date + cur_rollover or not (current_average*LOW_DET <= cur_current <= current_average*HIGH_DET):
					if cur_date >= start_date + cur_rollover:
						date_cons += 1
					elif not (current_average*LOW_DET <= cur_current <= current_average*HIGH_DET):
						avg_cons += 1
					dates.append(cur_date)
					currents.append(cur_current)
					current_average = cur_current
					start_date = cur_date
					init_line = False
				current_average += (cur_current - current_average)*INTEGRATE_PARAMETER
	return dates, currents



def process_raw_data(raw_dates, raw_currents):
	true_dates = []
	true_currents = []
	for date in raw_dates:
		true_dates.append(datetime.datetime.fromtimestamp(int(date)))
	for current in raw_currents:
		true_currents.append(float(current))
	return true_dates, true_currents

def generate_plots_and_data():
	raw_dates, raw_currents = get_all_data(get_names_to_read())
	dates, currents = process_raw_data(raw_dates, raw_currents)

	plt.figure(figsize=(16,9))
	plt.xlabel('DATE')
	plt.ylabel('CURRENT (A)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates, currents, 'r-')
	plt.savefig(graph_location+"global01.jpg", dpi=400)

	plt.clf()
	
	plt.figure(figsize=(16,9))
	plt.xlabel('DATE')
	plt.ylabel('CURRENT (A)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates[-86400:], currents[-86400:], 'r-')
	plt.savefig(graph_location+"recent01.jpg", dpi=400)
	
	plt.clf()
	
	plt.figure(figsize=(16,9))
	plt.xlabel('DATE')
	plt.ylabel('CURRENT (A)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates[-3600:], currents[-3600:], 'r-')
	plt.savefig(graph_location+"recent02.jpg", dpi=400)
	
	plt.clf()
	
	plt.figure(figsize=(16,9))
	plt.xlabel('DATE')
	plt.ylabel('CURRENT (A)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates[-1800:], currents[-1800:], 'r-')
	plt.savefig(graph_location+"recent03.jpg", dpi=400)

	plt.clf()
	
	plt.figure(figsize=(16,9))
	plt.xlabel('DATE')
	plt.ylabel('CURRENT (A)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates[-600:], currents[-600:], 'r-')
	plt.savefig(graph_location+"recent04.jpg", dpi=400)
	
	plt.clf()
	plt.close('all')

	current_average_3600 = 0
	for current_indiv in currents[-3600:]:
		current_average_3600 += current_indiv
	current_average_3600 /= 3600
	current_average_1800 = 0
	for current_indiv in currents[-1800:]:
		current_average_1800 += current_indiv
	current_average_1800 /= 1800
	current_average_600 = 0
	for current_indiv in currents[-600:]:
		current_average_600 += current_indiv
	current_average_600 /= 600
	return [current_average_600, current_average_1800, current_average_3600]
	
def generate_html(all_data):
	doc, tag, text, line = Doc().ttl()
	line('h2', 'GENERATED AT: ' + datetime.datetime.now().isoformat())
	line('h2', 'LAST 600 MEASUREMENTS AVERAGE: ' + str(all_data[0])[:5] + " A")
	line('h2', 'LAST 1800 MEASUREMENTS AVERAGE: ' + str(all_data[1])[:5] + " A")
	line('h2', 'LAST 3600 MEASUREMENTS AVERAGE: ' + str(all_data[2])[:5] + " A")
	line('h2', 'CURRENT MEASUREMENTS')
	line('h3', 'ALL TIME GRAPH')
	with open(graph_location+"global01.jpg", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/jpeg;base64,'+base64img[2:-1], width="100%")
	line('h3', 'LAST 86400 MEASUREMENTS')
	with open(graph_location+"recent01.jpg", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/jpeg;base64,'+base64img[2:-1], width="100%")
	line('h3', 'LAST 3600 MEASUREMENTS')
	with open(graph_location+"recent02.jpg", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/jpeg;base64,'+base64img[2:-1], width="100%")
	line('h3', 'LAST 1800 MEASUREMENTS')
	with open(graph_location+"recent03.jpg", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/jpeg;base64,'+base64img[2:-1], width="100%")
	line('h3', 'LAST 600 MEASUREMENTS')
	with open(graph_location+"recent04.jpg", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/jpeg;base64,'+base64img[2:-1], width="100%")
	tw = open(graph_location+"index.html","w")
	tw.write(doc.getvalue())
	tw.close()

while True:
	spit_data = generate_plots_and_data()
	generate_html(spit_data)
	gc.collect()
	time.sleep(540)
