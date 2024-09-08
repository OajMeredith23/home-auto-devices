import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import utime
import _thread
import secrets
import parse_query_strings

count = 0

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

  
def status_request(client):
    client.send("Hello from Pico")
    
def core0_thread():
    global count
    while True:
        print(count)
        utime.sleep(0.5)


def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    
    global count
    while True:
        client = connection.accept()[0]
        client.send('HTTP/1.1 200 OK\n')
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
        
        queries = parse_query_strings.qs_parse(request)
        print("PARSE", queries)
        
        if "toggle" in queries and "scale" in queries:
            print("Changing toggle")
            toggle = queries["toggle"]
            scale = queries["scale"]
            count = scale
            if toggle == 'on':
                pico_led.on()
            elif toggle =='off':
                pico_led.off()
            
            return_json = '{"status":"' + str(toggle) + '",' + '"scale":' + '"' + str(scale) + '"' + '}'
            client.send(return_json)
                
        client.close()


second_thread = _thread.start_new_thread(core0_thread, ())


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)

except KeyboardInterrupt:
    machine.reset()