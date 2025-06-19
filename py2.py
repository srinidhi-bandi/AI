import cv2
img = cv2.imread("DFS.jpg",1)
print(img)
cv2.imshow("output",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
