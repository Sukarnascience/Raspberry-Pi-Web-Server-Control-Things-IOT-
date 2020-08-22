from flask import Flask,render_template,request
from gpiozero import CPUTemperature
from gpiozero import Button
from gpiozero import LED
from pygame import mixer
import requests
import socket
import sys
sys.path.append('/home/pi/Adafruit_Python_DHT/examples/')
import Adafruit_DHT
sys.path.append('/home/pi/lcd/')
import lcddriver

app=Flask(__name__,template_folder='/home/pi/Documents/WebServer')
B = Button(14)
sensor = Adafruit_DHT.DHT11
pin = 4
Sw1=LED(15)
Sw2=LED(18)

data={}
display = lcddriver.lcd()

@app.route("/")
def start():
    global data
    
    cput = CPUTemperature()
    cpt=str(cput)
    cpus=cpt[44:46]
    ServerTemp=int(cpus)
    
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    IPaddress=f"{ip_address}"
    
    Humidity, Temp = Adafruit_DHT.read_retry(sensor, pin)
    
    if(B.is_pressed):
        IRs="YES!"
    else:
        IRs="NO!"
    
    data={'RT':Temp,
          'RH':Humidity,
          'IR':IRs,
          'IP':IPaddress,
          'ST':ServerTemp}
    return render_template('MainPG.html',**data)

@app.route("/<issue>")
def IS(issue):
    if(issue=='off'):
        mixer.init()
        mixer.music.load("off.mp3")
        mixer.music.set_volume(0.5)
        mixer.music.play()
    if(issue=='notW'):
        mixer.init()
        mixer.music.load("error.mp3")
        mixer.music.set_volume(0.5)
        mixer.music.play()
        requests.get('https://maker.ifttt.com/trigger/server/with/key/fOSt9a1rzczR1p0mJ-qsbpCKUpXtxVyCsaJvRmfF4hW')
    data.update({'i':"OK! your request has been send to server side"})
    return render_template('MainPG.html',**data)

@app.route("/<switch>/<state>")
def S(switch,state):  
    if(switch=='switch1' and state=='on'):
        Sw1.on()
    if(switch=='switch2' and state=='on'):
        Sw2.on()
    if(switch=='switch1' and state=='off'):
        Sw1.off()
    if(switch=='switch2' and state=='off'):
        Sw2.off()
    data.update({'S':switch,'Se':state})
    return render_template('MainPG.html',**data)

@app.route('/display',methods = ['POST', 'GET'])
def screen():
    if request.method == 'POST':
        result = request.form
        screendata=dict(result)
        display.lcd_display_string(screendata.get("L1"),1)
        display.lcd_display_string(screendata.get("L2"),2)
    data.update({'i':"OK! your content has been send to server side"})
    return render_template('MainPG.html',**data)

if __name__=="__main__":
    app.run(host="0.0.0.0",
            port=8000,
            debug=True)