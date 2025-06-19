import cv2
img = cv2.imread("lom.jpg",1)
img1 = cv2.line(img,(0,0),(510,510),(255,0,0),5)
#cv2.line(Image,Starting point,Ending point,color Line,Line thickness)
#Color is loaded in BGR ormat
cv2.imshow("Image",img1)
cv2.waitKey(0)
cv2.destroyAllWindows()
