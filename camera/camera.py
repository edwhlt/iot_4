import cv2
import paho.mqtt.client as mqtt
import pytesseract
import re

# Créez un objet VideoCapture pour accéder à la caméra (0 pour la première caméra, 1 pour la deuxième, etc.)
cap = cv2.VideoCapture(0)

# Vérifiez si la caméra est ouverte correctement
if not cap.isOpened():
    print("Erreur: Impossible d'accéder à la caméra.")
    exit()

# Configuration de la fenêtre d'affichage
cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Camera', 640, 480)


class MqttClient(mqtt.Client):

    def __init__(self):
        super().__init__()
        self.isClose = False

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.subscribe("Parking")

    def on_message(self, client, userdata, msg):
        if msg.topic == "Parking":
            if 500 > int(msg.payload.decode()) > 50:
                self.isClose = True
            else:
                self.isClose = False


mqtt_client = MqttClient()
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

while True:
    # Capturez un cadre vidéo
    ret, frame = cap.read()

    if not ret:
        print("Erreur: Impossible de capturer la vidéo.")
        break

    # Affichez le cadre vidéo en temps réel
    cv2.imshow('Camera', frame)

    if mqtt_client.isClose:
        cv2.imwrite("Parking.jpg", frame)

        if frame is not None:
            text = pytesseract.image_to_string(frame, lang='eng')
            print(text)
            plate_pattern = r'\b[A-Z0-9]{7}\b'
            matches = re.findall(plate_pattern, text)
            for match in matches:
                print(match)

    # Appuyez sur la touche 'q' pour quitter la boucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérez la ressource de la caméra et fermez la fenêtre d'affichage
cap.release()
cv2.destroyAllWindows()
