import cv2
img = cv2.imread("hod.jpg",1)
##Draw RecatngleLine
img = cv2.rectangle(img,(0,100),(255,255),(0,0.255),5)
cv2.imshow("Image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
