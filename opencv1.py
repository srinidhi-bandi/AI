import cv2
from PIL import Image, ImageOps 

img=cv2.imread("hod.jpg",0)
# print(img)
# cv2.imshow("tab",img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


img.show() 
cv2.waitKey(0)