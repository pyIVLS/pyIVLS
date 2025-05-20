import cv2 as cv

cap = cv.VideoCapture("/dev/video0")
if not cap.isOpened():
    raise Exception("Could not open video device")


# read something so that the camera is intialized and not sad
cap.read()
# set exposure
exposure = 1
cap.set(cv.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Disable auto exposure
cap.set(cv.CAP_PROP_EXPOSURE, exposure)
print(f"Set exposure to {exposure}")
exp = cap.get(cv.CAP_PROP_EXPOSURE)
print(f"Current exposure: {exp}")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv.imshow("frame", frame)
    if cv.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
