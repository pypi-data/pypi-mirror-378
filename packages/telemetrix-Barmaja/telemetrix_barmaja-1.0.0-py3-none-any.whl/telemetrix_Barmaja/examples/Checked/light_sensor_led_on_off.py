from telemetrix_Barmaja import begin, pinMode, digitalWrite, analogRead, delay, OUTPUT, HIGH, LOW, A0

begin()
LED = 13
THRESHOLD = 600  # Adjust to your room brightness

pinMode(LED, OUTPUT)

while True:
    value = analogRead(A0)
    if value < THRESHOLD:
        digitalWrite(LED, HIGH)
    else:
        digitalWrite(LED, LOW)
    delay(50)
