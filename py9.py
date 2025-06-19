import cv2
img =cv2.imread("hod.jpg",1)
##Draw Rectangle Line
img = cv2.rectangle(img,(384,0),(255,100),(0,0,255),-1)
cv2.imshow("Image",img)
cv2.waitkey(0)
cv2.destroyAllWindows()
