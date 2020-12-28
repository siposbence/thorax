import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

from __future__ import division
from numpy.fft import rfft
from numpy import argmax, mean, diff, log, nonzero
from scipy.signal import blackmanharris, correlate
from time import time
import sys
from kafka import KafkaProducer
from kafka.errors import KafkaError
import numpy as np
import statsmodels.api as sm
lowess = sm.nonparametric.lowess


data2fft = []
sp = 0
freq = 0
nout = 1000
f = np.linspace(0.01, 5, nout)


topic = "breath"
#producer = KafkaProducer(bootstrap_servers=['kafka.thorax:9092'])
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

def freq(f, pgram, device, t):
    integ_full  = np.sum(f*pgram)
    integ_part  = np.sum(f[(150+np.argmax(pgram[150:])-10):(150+np.argmax(pgram[150:])+10)]*pgram[(150+np.argmax(pgram[150:])-10):(150+np.argmax(pgram[150:])+10)])
    print(integ_full, integ_part, integ_part/integ_full)
    print(f[150+np.argmax(pgram[150:])]/2/3.1415*60)

    if len(device)>2:
        if integ_part/integ_full<0.1:
            publish.single(device, '-', hostname="localhost")
        else:
            publish.single(device, str(int(f[150+np.argmax(pgram[150:])]/2/3.1415*60)), hostname="localhost")
            producer.send(topic, (','.join(map(str,[device, t, str(int(f[150+np.argmax(pgram[150:])]/2/3.1415*60)), 0]))).encode())
            
def on_message(client, userdata, message):
    global data2fft
    print(client)
    string = message.payload.decode("utf-8")
    device, data = string.split('#')
    print(device)
    adat = np.array(np.matrix(data))
    adat = adat[abs(adat[:,1] - np.mean(adat[:,1])) < 4 * np.std(adat[:,1])]
    pgram = signal.lombscargle((adat[:,3]-adat[0,3])/1000, adat[:,1]-adat[0,1], f, normalize=True)
    print(np.max(adat[:,1])-np.min(adat[:,1]))
    if ((np.max(adat[:,1]))-(np.min(adat[:,1])))>0.01:
        print("ok")
        freq(f, pgram, device, adat[-1,3])

    
#subscribe.callback(on_message_print, "breathing", hostname="192.168.0.104")
subscribe.callback(on_message, "breathing", hostname="localhost")
