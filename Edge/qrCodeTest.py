import cv2
from pyzbar.pyzbar import decode
from PIL import Image




#img = cv2.imread('qr.png')
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("http://10.0.0.4:8000/stream.mjpg")

cap.set(3,960)
cap.set(4,720)

while True:
    success, img = cap.read()

    for barcode in decode(img):
        print(barcode.data.decode())
        color = (0, 255, 0)
        stroke = 2
        cv2.rectangle(img, (barcode.rect.left, barcode.rect.top), (barcode.rect.left + barcode.rect.width, barcode.rect.top + barcode.rect.height), color, stroke)
        cv2.putText(img,barcode.data.decode(),(barcode.rect.left, barcode.rect.top),cv2.FONT_HERSHEY_SIMPLEX,0.9,color,stroke)

    cv2.imshow('Result',img)
    cv2.waitKey(1)


    if (cv2.waitKey(20) & 0xFF == ord('q')):
        break

cap.release()
cv2.destroyAllWindows()
