from telemetrix_Barmaja import begin, analogRead, delay, A0

# Start the board
begin()

print("Reading LDR values from A0... Press CTRL+C to stop.")

while True:
    value = analogRead(A0)   # Read raw value (0–1023)
    print("LDR Value =", value)
    delay(200)  # Read every 200 ms
