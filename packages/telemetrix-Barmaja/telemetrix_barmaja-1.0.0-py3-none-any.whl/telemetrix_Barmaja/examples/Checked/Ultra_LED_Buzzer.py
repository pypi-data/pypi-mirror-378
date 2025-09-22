from telemetrix_Barmaja import begin, pinMode, digitalWrite, delay, sonarBegin, sonarReadCM, sonarEnableReports, OUTPUT, HIGH, LOW

begin()

TRIG = 7
ECHO = 8
LED = 13
BUZZER = 12

pinMode(LED, OUTPUT)
pinMode(BUZZER, OUTPUT)

# Initialize ultrasonic sensor
sonarBegin(TRIG, ECHO)
sonarEnableReports()

while True:
    try:
        distance = sonarReadCM(TRIG, ECHO)
        print(f"Distance: {distance} cm")
    except RuntimeError:
        distance = 999  # Waiting for first reading

    # LED on if too close
    digitalWrite(LED, HIGH if distance < 30 else LOW)

    # Buzzer beeps faster when closer
    gap = max(30, min(600, int(distance * 10)))  # 30–600 ms
    digitalWrite(BUZZER, HIGH)
    delay(40)
    digitalWrite(BUZZER, LOW)
    delay(gap)
