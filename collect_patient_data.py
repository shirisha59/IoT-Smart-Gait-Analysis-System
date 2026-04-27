import serial
import csv
import keyboard

PORT = 'COM3'
BAUD = 115200

filename = "patient_data.csv"

ser = serial.Serial(PORT, BAUD, timeout=1)

file = open(filename, "w", newline='')
writer = csv.writer(file)

# NO LABEL HERE
writer.writerow(["Lx","Ly","Lz","Rx","Ry","Rz"])

print("\nRecording patient walking...")
print("Press 'Q' to STOP\n")

while True:
    try:
        line = ser.readline().decode(errors='ignore').strip()

        if not line:
            continue

        print(line)

        if keyboard.is_pressed('q'):
            print("\nStopping...")
            break

        # FORMAT 1
        if "L:" in line and "|" in line:
            parts = line.split("|")

            left = [int(x) for x in parts[0].replace("L:", "").split(",")]
            right = [int(x) for x in parts[1].replace("R:", "").split(",")]

            writer.writerow(left + right)
            file.flush()

        # FORMAT 2
        else:
            values = [int(x) for x in line.split(",")]

            if len(values) == 6:
                writer.writerow(values)
                file.flush()

    except Exception as e:
        print("Error:", e)

file.close()
ser.close()

print("Patient data saved as patient_data.csv")