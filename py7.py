import cv2
img = cv2.imread("hod.jpg",1)
img = cv2.arrowedLine(img,(0,255),(255,255),(255,0.0),10)
##Draw Arrowed Line
cv2.imshow("Image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
