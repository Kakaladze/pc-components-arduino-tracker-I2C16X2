import clr
import os
import serial
import json
import signal
from dotenv import load_dotenv

ARDUINO_INIT_MESSAGE = 'init'
ARDUINO_HANDLED_MESSAGE = 'handled'
serial_port_connection = None

load_dotenv()

try: 
    arduino_port = os.getenv("PORT")
    arduino_baud_rate = int(os.getenv("BAUD_RATE"))
    interval = os.getenv("INTERVAL")
except:
    print('There was an issue loading env variables, program might be unstable')

def initialize_openhardwaremonitor():
    file = os.path.dirname(__file__) + '\\OpenHardwareMonitorLib.dll'
   
    clr.AddReference(file)
   
    from OpenHardwareMonitor import Hardware

    handle = Hardware.Computer()
    handle.CPUEnabled = True
    handle.RAMEnabled = True
    handle.GPUEnabled = True
    handle.HDDEnabled = True

    handle.Open()
    return handle

def fetch_stats(handle):
    stats = {
        "action": "update",
        "cpuTemp": 0,
        "cpuUsage": 0,
        "gpuTemp": 0,
        "gpuUsage": 0,
        "ramMax": 0,
        "ramUsage": 0
    }

    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            if str(sensor.SensorType) == 'Temperature':
                if (str(sensor.Hardware.HardwareType) == 'CPU' and str(sensor.Name) == 'CPU Package'):
                    stats["cpuTemp"] = round(sensor.Value)
                if ('GPU' in str(sensor.Hardware.HardwareType).upper()):
                    stats["gpuTemp"] = round(sensor.Value)
            if str(sensor.SensorType) == 'Load':
                if (str(sensor.Hardware.HardwareType) == 'CPU' and str(sensor.Name) == 'CPU Total'):
                    stats["cpuUsage"] = round(sensor.Value)
                if ('GPU' in str(sensor.Hardware.HardwareType).upper() and str(sensor.Name) == 'GPU Core'):
                    stats["gpuUsage"] = round(sensor.Value)
            if str(sensor.SensorType) == 'Data':
                if (str(sensor.Name) == 'Used Memory'):
                    stats["ramUsage"] = round(sensor.Value * 1024)
                    stats["ramMax"] += round(sensor.Value * 1024)
                if (str(sensor.Name) == 'Available Memory'):
                    stats["ramMax"] += round(sensor.Value * 1024)
    return stats

def signal_handler(sig, frame):
    json_data = json.dumps({ "action": "stop" })
    serial_port_connection.write(json_data.encode())
    exit()


if __name__ == "__main__":
    HardwareHandle = initialize_openhardwaremonitor()

    if arduino_port == None:
        print('You need to provide arduino port to start application')
        exit()
    if arduino_baud_rate == None:
        print('You need to provide baud rate to start application')
        exit()
    
    try: 
        serial_port_connection = serial.Serial(arduino_port, arduino_baud_rate)
    except:
        print('Cannot connect to arduino on port', arduino_port)
        exit()
    
    initData = serial_port_connection.readline().decode().strip()
    print('Connection with arduino established')
    if initData != ARDUINO_INIT_MESSAGE:
        print('Unexpected behaviour of arduino')
        exit()

    if interval != None:
        print('Changing interval to', interval)
        json_data = json.dumps({ "action": "changeInterval", "interval": int(interval)})
        serial_port_connection.write(json_data.encode())
        response = serial_port_connection.readline().decode().strip()
        if (response == ARDUINO_HANDLED_MESSAGE):
            print('Successfully changed the interval')
        else:
            print('Unexpected behaviour of arduino')
            exit()

    print('Starting main loop of application, to turn off the application hit ctrl+c')

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        stats = fetch_stats(HardwareHandle)
        json_data = json.dumps(stats)
        serial_port_connection.write(json_data.encode())
        response = serial_port_connection.readline().decode().strip()
        if (response != ARDUINO_HANDLED_MESSAGE):
            print('Unexpected behaviour of arduino')
