import os
import sys
import cv2
import time
import datetime
import Adafruit_DHT

# Time in seconds
#SLEEP_TIME = 1800
SLEEP_TIME = 120
sensor = Adafruit_DHT.DHT22
pin = 4
data_filename = "temp_hum.csv"

import serial
import datetime

class ReadLine():
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

def get_date():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

def take_picture(filename):
    try:
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite(filename, image)
        return True
    except:
        return False

if __name__ == "__main__":

    # Setup directory
    if not os.path.isdir("photos"):
        os.mkdir("photos")

    # Setup file
    if not os.path.isfile(data_filename):
        print("writing header for the file")
        with open(data_filename, "w") as f:
            f.write("date;temperature;humidity;moisture\n")

    print("connecting to serial port")
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0.5)

    print("starting readline...")
    reader = ReadLine(ser)
    print("waiting for a valid line")
    x = reader.readline()
    while "MOISTURE" not in x.decode("utf-8"):
        print('retrying...')
        x = reader.readline()

    # Process
    while True:
        print("while...")

        moisture = None
        try:
            #x = reader.readline()
            #print(line)
            measure = 0
            print("starting measuremens...")
            while "MOISTURE" in x.decode("utf-8") and measure < 20:
                x = reader.readline()
                measure += 1
                print(f"Measure {measure} | {x.decode('utf-8')} | {get_date()}")

            line = f"{x.decode('utf-8')}"

            try:
                moisture = int(line.split(";")[-1])
                print(moisture)
            except BaseException as e:
                print("Error parsing line", line)
        except KeyboardInterrupt:
            print("Closing connection")
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            print(ser.is_open)
            time.sleep(5)
            print(ser.is_open)
            break
        if moisture:
            # Getting photo
            snap_date = get_date()
            filename = f"photos/{snap_date}.png"
            if take_picture(filename):
                print("Number of photos", len(os.listdir("photos")))
            else:
                print("Error with photo", filename)

            # Getting measurements
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            print(temperature)
            with open(data_filename, "a") as f:
                f.write(f"{snap_date};{temperature:.1f};{humidity:.1f};{moisture}\n")
