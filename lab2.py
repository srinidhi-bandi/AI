import cv2
img = cv2.imread("hod.jpg",1)
grey=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
cv2.imshow("op",grey)
cv2.waitKey(0)
cv2.destroyAllWindows()

import cv2
img = cv2.imread("hod.jpg",)
grey=cv2.cvtColor(gimg,cv2.COLOR_GRAY2BGR)
cv2.imshow("op",grey)
BGR1 =cv2.cvtColor(grey,cv2.COLOR_GRAY2RGB)
cv2.imshow("op",BGR1)
cv2.waitKey(0)
cv2.destroyAllWindows()
