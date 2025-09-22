from telemetrix_Barmaja import begin, pinMode, analogWrite, delay, OUTPUT

begin()
LED = 5  # PWM pin
pinMode(LED, OUTPUT)

while True:
    for v in range(0, 256, 5):
        analogWrite(LED, v)
        delay(20)
    for v in range(255, -1, -5):
        analogWrite(LED, v)
        delay(20)
