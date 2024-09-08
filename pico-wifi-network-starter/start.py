import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import secrets


def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.ssid, secrets.password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./?light=on">
            <input type="submit" value="Light on" />
            </form>
            <form action="./?light=off">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """
    return str(html)
  
def status_request(client):
    client.send("Hello from Pico")
    
def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        client.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send('Access-Control-Allow-Origin: *\n')
        client.send('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\n')
        client.send('Access-Control-Allow-Headers: Content-Type\n')
        client.send('Content-Type: text/html\n')
        client.send('\n')
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        

        if "status_request" in request:
            status_request(client)
            
        if "light" in request and '?' in request and '=' in request:
            
            requestValue = request.split('=')[1]
            if requestValue == 'on':
                pico_led.on()
                client.send('{"status": "on"}')
            elif requestValue =='off':
                pico_led.off()
                client.send('{"status": "off"}')
#             html = webpage(temperature, state)
            
#             client.send(html)
        client.close()

        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
    
except KeyboardInterrupt:
    machine.reset()