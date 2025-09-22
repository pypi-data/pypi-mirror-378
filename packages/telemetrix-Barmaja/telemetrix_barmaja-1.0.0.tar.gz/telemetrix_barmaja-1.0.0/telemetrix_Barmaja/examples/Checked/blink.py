from telemetrix_Barmaja import begin, pinMode, digitalWrite, delay, OUTPUT, HIGH, LOW

begin()
pinMode(13, OUTPUT)

while True:
    digitalWrite(13, HIGH)
    delay(500)
    digitalWrite(13, LOW)
    delay(500)
