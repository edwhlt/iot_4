#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char* ssid = "Redmi Note 10S";
const char* password = "commetoifrerot";

// const char* ssid = "Wifiot";
// const char* password = "julesfaitletp";

const char* MQTT_username = "";
const char* MQTT_password = "";

const char* mqtt_server = "192.168.142.22";

WiFiClient espClient;
PubSubClient client(espClient);

// #define DHTPIN 4 // Pin connected to the DHT sensor
// #define DHTTYPE DHT11 // DHT11 or DHT22, depending on your sensor

#define PIR 5 // detecteur de mouvement
#define REL 2 // relais
#define BUZ 12 // buzzer

#define TrigPin 4  // Trigger pin of the ultrasonic sensor

/* Constantes pour le timeout */
const unsigned long MEASURE_TIMEOUT = 25000UL; // 25ms = ~8m à 340m/s

/* Vitesse du son dans l'air en mm/us */
const float SOUND_SPEED = 340.0 / 1000;

// This functions connects your ESP8266 to your router
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messages;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messages += (char)message[i];
  }

  if(topic == "Room/rel"){
    digitalWrite(REL, messages == "True" ? HIGH : LOW);
  }
  Serial.println();
}

// This functions reconnects your ESP8266 to your MQTT broker
// Change the function below if you want to subscribe to more topics with your ESP8266 
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    /*
     YOU MIGHT NEED TO CHANGE THIS LINE, IF YOU'RE HAVING PROBLEMS WITH MQTT MULTIPLE CONNECTIONS
     To change the ESP device ID, you will have to give a new name to the ESP8266.
     Here's how it looks:
       if (client.connect("ESP8266Client")) {
     You can do it like this:
       if (client.connect("ESP1_Office")) {
     Then, for the other ESP:
       if (client.connect("ESP2_Garage")) {
      That should solve your MQTT multiple connections problem
    */
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");  
      // Subscribe or resubscribe to a topic
      // You can subscribe to more topics (to control more LEDs in this example)
      client.subscribe("Room/rel");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// DHT dht(DHTPIN, DHTTYPE);

void setup() {
  pinMode(PIR, INPUT);
  pinMode(REL, OUTPUT);
  pinMode(BUZ, OUTPUT);

  pinMode(TrigPin, OUTPUT);
  pinMode(TrigPin, INPUT);

  Serial.begin(115200);

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  // dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop()) client.connect("ESP8266Client", MQTT_username, MQTT_password);


  int pirVal = digitalRead(PIR);
  client.publish("Room/mouv", String(pirVal == HIGH).c_str());
  
  if(pirVal == HIGH) tone(BUZ, 1000);
  else digitalWrite(BUZ, HIGH);


  /* float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  client.publish("Room/temp", String(temperature).c_str());
  client.publish("Room/hum", String(humidity).c_str());*/

  pinMode(TrigPin, OUTPUT);
  digitalWrite(TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(TrigPin, LOW);
  pinMode(TrigPin, INPUT);

  // Measure the time it takes for the echo to return
  long duration = pulseIn(TrigPin, HIGH, MEASURE_TIMEOUT);

  // Calculate the distance in centimeters
  int distance_mm = duration / 2.0 * SOUND_SPEED; // Speed of sound is 343 m/s, or 0.0343 cm/us

  // Display the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance_mm);
  Serial.println(" mm");
  client.publish("Parking", String(distance_mm).c_str());

  delay(100);

}