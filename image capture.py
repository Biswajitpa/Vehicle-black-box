import cv2
import os
from datetime import datetime
import time

# Create folder to store images
folder = "captured_images"
if not os.path.exists(folder):
    os.makedirs(folder)

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot access webcam")
    exit()

print("Camera started... Capturing every 1 second")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # File name
    filename = f"{folder}/image_{timestamp}.jpg"

    # Save image
    cv2.imwrite(filename, frame)
    print(f"Saved: {filename}")

    # Show preview (optional)
    cv2.imshow("Live Capture", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Capture every 1 second
    time.sleep(1)

cap.release()
cv2.destroyAllWindows()