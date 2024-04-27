import typing
import threading
import serial
import nmea_encode_c_ext.nmea_encode as nmea_encode
import time
import serial.tools.list_ports
import socket

HOST = '192.168.68.43'
PORT = 10110 # standard NMEA port

METRO_M4_PIPE: str = '/dev/ttyACM0'

GAMEPAD_NUM_INPUTS: int = 18

for p in serial.tools.list_ports.comports():
    print(p)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket created")
try:
    s.connect((HOST, PORT))
    print("socket connected")
except:
    print("socket connection failed")
    exit(1)

logitech_f310_map = {
    "ABS_X": 0, # i16, LSX
    "ABS_Y": 1, # i16, LSY
    "ABS_RX": 2, # i16, RSX
    "ABS_RY": 3, # i16, RSY
    "BTN_THUMBL": 4, # 0, 1, LSB
    "BTN_THUMBR": 5, # 0, 1, RSB
    "ABS_HAT0X": 6, # -1, 0, 1, DPadX
    "ABS_HAT0Y": 7, # -1, 0, 1, DPadY
    "BTN_SOUTH": 8, # 0, 1, A
    "BTN_EAST": 9, # 0, 1, B
    "BTN_NORTH": 10, # 0, 1, X
    "BTN_WEST": 11, # 0, 1, Y
    "BTN_TL": 12, # 0, 1, LB
    "BTN_TR": 13, # 0, 1, RB
    "ABS_Z": 14, # u8, LT
    "ABS_RZ": 15, # u8, RT
    "BTN_START": 16, # 0, 1, Start
    "BTN_SELECT": 17 # 0, 1, Back
}

gamepad_map = logitech_f310_map

gamepad_inputs: list[int] = [0] * GAMEPAD_NUM_INPUTS
gamepad_input_tuple: tuple[int, ...] = tuple(gamepad_inputs)

ser = serial.Serial(METRO_M4_PIPE, 9600, write_timeout = 2)
ser.flush()

def monitor_socket_input():
    datalen: int = int(s.recv(4).decode('ASCII'))
    data: str = s.recv(datalen).decode('ASCII')
    #print("Data received: ", data)
    chunks: list[str] = data.split(",")
    if(chunks[0] != "$CTCTL"):
        print("Invalid NMEA header")
        return
    for event in chunks[1:]:
        code, state = event.split(":")
        gamepad_inputs[gamepad_map[code]] = int(state)

def main():
    while True:
        monitor_socket_input()
        if(ser.in_waiting > 0):
            try:
                line = ser.readline().decode('ASCII').rstrip()
                print(line)
            except UnicodeDecodeError:
                print("check transmission code")
        gamepad_input_tuple = tuple(gamepad_inputs)
        #print(gamepad_input_tuple)
        nmea_bytes: bytes = nmea_encode.nmea_encode(gamepad_input_tuple)
        #print(nmea_bytes)
        #print(ser.write(nmea_bytes))
        ser.write(nmea_bytes)

main()