##Basic Live Video Capture (Display on Screen)
import cv2

# Start camera (0 = default camera)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Show live video
    cv2.imshow("Live Camera", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

##Save Live Video to File (Black Box Recording)
import cv2

cap = cv2.VideoCapture(0)

# Define codec and output file
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while True:
    ret, frame = cap.read()

    if not ret:
        break

    out.write(frame)  # Save video

    cv2.imshow('Recording...', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
##Capture Image Every 1 Second (For Evidence Storage)
import cv2
import time

cap = cv2.VideoCapture(0)

count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    filename = f"image_{count}.jpg"
    cv2.imwrite(filename, frame)   # Save image
    print(f"Saved {filename}")

    count += 1

    cv2.imshow("Live", frame)

    time.sleep(1)  # 1 second delay

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()