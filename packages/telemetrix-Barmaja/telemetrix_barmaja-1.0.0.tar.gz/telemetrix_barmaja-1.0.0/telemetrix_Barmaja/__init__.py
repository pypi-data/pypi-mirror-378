from . import telemetrixsync
from .telemetrixsync import HIGH, LOW, OUTPUT, INPUT, INPUT_PULLUP, A0, A1, A2, A3, A4, A5

# ---- Re-export Arduino-like singletons ----
begin               = telemetrixsync.begin
pinMode             = telemetrixsync.pinMode
digitalWrite        = telemetrixsync.digitalWrite
digitalRead         = telemetrixsync.digitalRead
analogRead          = telemetrixsync.analogRead
analogWrite         = telemetrixsync.analogWrite
delay               = telemetrixsync.delay
millis              = telemetrixsync.millis
servoWrite          = telemetrixsync.servoWrite
sonarBegin          = telemetrixsync.sonarBegin
sonarReadCM         = telemetrixsync.sonarReadCM
sonarEnableReports  = telemetrixsync.sonarEnableReports
sonarDisableReports = telemetrixsync.sonarDisableReports
dhtBegin            = telemetrixsync.dhtBegin
dhtLast             = telemetrixsync.dhtLast
i2cBegin            = telemetrixsync.i2cBegin
i2cRead             = telemetrixsync.i2cRead
i2cWrite            = telemetrixsync.i2cWrite
shutdown            = telemetrixsync.shutdown

# Optional: compatibility alias if some examples used the misspelled name
def begain(*args, **kwargs):
    return begin(*args, **kwargs)

__all__ = [
    # class
    "TelemetrixSync",

    # constants
    "HIGH", "LOW", "OUTPUT", "INPUT", "INPUT_PULLUP",
    "A0", "A1", "A2", "A3", "A4", "A5",

    # Arduino-like singletons
    "begin", "begain", "pinMode", "digitalWrite", "digitalRead",
    "analogRead", "analogWrite",
    "delay", "millis",
    "servoWrite",
    "sonarBegin", "sonarReadCM", "sonarEnableReports", "sonarDisableReports",
    "dhtBegin", "dhtLast",
    "i2cBegin", "i2cRead", "i2cWrite",
    "shutdown",
]

class TelemetrixSync:
    def __init__(self, com_port=None, **kwargs):
        telemetrixsync.begin(com_port=com_port, **kwargs)

    # Core IO
    def pinMode(self, pin, mode):        telemetrixsync.pinMode(pin, mode)
    def digitalWrite(self, pin, val):    telemetrixsync.digitalWrite(pin, val)
    def digitalRead(self, pin):          return telemetrixsync.digitalRead(pin)
    def analogRead(self, apin):          return telemetrixsync.analogRead(apin)
    def analogWrite(self, pin, val):     telemetrixsync.analogWrite(pin, val)
    def delay(self, ms):                 telemetrixsync.delay(ms)
    def millis(self):                    return telemetrixsync.millis()
    def shutdown(self):                  telemetrixsync.shutdown()

    # Servo
    def servoWrite(self, pin, angle):    telemetrixsync.servoWrite(pin, angle)

    # Ultrasonic
    def sonarBegin(self, trig, echo):        telemetrixsync.sonarBegin(trig, echo)
    def sonarReadCM(self, trig, echo):       return telemetrixsync.sonarReadCM(trig, echo)
    def sonarEnableReports(self):            telemetrixsync.sonarEnableReports()
    def sonarDisableReports(self):           telemetrixsync.sonarDisableReports()

    # DHT
    def dhtBegin(self, pin, dht_type=11):    telemetrixsync.dhtBegin(pin, dht_type)
    def dhtLast(self, pin):                  return telemetrixsync.dhtLast(pin)

    # I2C
    def i2cBegin(self, i2c_port=0):              telemetrixsync.i2cBegin(i2c_port)
    def i2cRead(self, address, register, nbytes, **kw):  return telemetrixsync.i2cRead(address, register, nbytes, **kw)
    def i2cWrite(self, address, data, **kw):     telemetrixsync.i2cWrite(address, data, **kw)
