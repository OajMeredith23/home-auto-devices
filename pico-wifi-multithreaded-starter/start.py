import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import _thread
import secrets
import parse_query_strings

reset_counter = 0

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
    global reset_counter
    counter = 1
    while True:
        if(reset_counter == 1):
            counter = 0
            reset_counter = 0
        if counter >= 100:
            counter = 0
#         print(counter, "Reset: ", reset_counter)
        counter += 2
        sleep(0.5)


def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    num = 0
    global reset_counter
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
        
        
#         print("Parsed:" parsed)
        
        queries = parse_query_strings.qs_parse(request)
        print("PARSE", queries)
        
        if "light" in queries and "brightness" in queries:
            print("Changing light")
            light = queries["light"]
            brightness = queries["brightness"]
            
            if light == 'on':
                pico_led.on()
                reset_counter = 1
                num += 1
            elif light =='off':
                pico_led.off()
            
            return_json = '{"status":"' + str(light) + '",' + '"brightness":' + '"' + str(brightness) + '"' + '}'
            print(return_json)
            client.send(return_json)
                
        print("num", num)
        client.close()


second_thread = _thread.start_new_thread(core0_thread, ())


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)

except KeyboardInterrupt:
    machine.reset()