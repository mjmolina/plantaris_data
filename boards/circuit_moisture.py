import time
from adafruit_crickit import crickit

ss = crickit.seesaw
moisture_sensor = crickit.SIGNAL1

while True:
    moisture_sensor_out = ss.analog_read(moisture_sensor)
    print("MOISTURE;{}".format(moisture_sensor_out))
    time.sleep(60)
