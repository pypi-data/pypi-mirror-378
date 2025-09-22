from telemetrix_Barmaja import begin, pinMode, analogWrite, dhtBegin, dhtLast, OUTPUT, delay

begin()
DHT_PIN = 2
FAN = 5

dhtBegin(DHT_PIN)
pinMode(FAN, OUTPUT)

while True:
    temp, hum = dhtLast(DHT_PIN)
    if temp is not None:
        temp = max(20, min(40, temp))  # Clamp 20–40°C
        pwm = int((temp - 20) / 20 * 255)  # Map to 0–255
        analogWrite(FAN, pwm)
        print(f"T={temp:.1f}°C  H={hum:.1f}%  PWM={pwm}")
    delay(200)
