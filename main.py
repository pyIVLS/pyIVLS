import cv2


def main():
    cap = cv2.VideoCapture()
    cap.open(0)

    _, frame = cap.read()
    cv2.imshow("frame", frame)
    cv2.waitKey(0)
    cap.release()


if __name__ == "__main__":
    main()
