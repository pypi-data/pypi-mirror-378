from telemetrix_Barmaja import begin, pinMode, analogRead, analogWrite, delay, OUTPUT, A0

begin()
LED = 5
pinMode(LED, OUTPUT)

while True:
    raw = analogRead(A0)          # 0..1023
    pwm = int(255 - (raw / 1023) * 255)  # Inverted mapping
    analogWrite(LED, pwm)
    delay(40)
