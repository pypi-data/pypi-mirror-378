from telemetrix_Barmaja import begin, pinMode, digitalRead, digitalWrite, delay, INPUT, OUTPUT, HIGH, LOW

begin()
LED = 13
BUTTON = 2

pinMode(LED, OUTPUT)
pinMode(BUTTON, INPUT)  # External pull-down resistor required

while True:
    if digitalRead(BUTTON) == HIGH:
        digitalWrite(LED, HIGH)
    else:
        digitalWrite(LED, LOW)
    delay(20)
