
import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Erreur : impossible d'ouvrir la camera.")
else:
    print("Camera ouverte avec succes !")
    
    while True:
        success, frame = camera.read()

        if not success:
            print("Impossible de lire l'image.")
            break

        cv2.imshow("Test Camera - Appuie sur Q pour quitter", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()
