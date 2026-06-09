#include <WiFi.h>
#include <WebServer.h>

const char* ap_ssid = "404_NotFound";    
const char* ap_password = "mtseguromano24"; 

WebServer server(80);

const int PIN_LED = 2;   
const int PIN_SERVO = 3; 

int freqLED = 1000;             
const int resLED = 8;           

const int freqServo = 50;       
const int resServo = 12;        

const int SERVO_MIN_DUTY = 205; 
const int SERVO_MAX_DUTY = 410; 

int brilhoAtual = 0; 
int anguloAtual = 90; 

const char CODE_DASHBOARD_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 AP PWM Control Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 20px; background-color: #f4f6f9; }
        .card { background: white; padding: 20px; margin: 15px auto; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; }
        h1 { color: #333; }
        .slider { width: 90%; margin: 15px 0; height: 25px; }
        .btn-group { display: flex; justify-content: space-around; margin-top: 10px; }
        button { padding: 10px 20px; font-size: 16px; border: none; border-radius: 6px; background-color: #28a745; color: white; cursor: pointer; }
        button:active { background-color: #1e7e34; }
        span { font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <h1>ESP32 AP Control Dashboard</h1>
    
    <div class="card">
        <h3>1. Intensidade do LED</h3>
        <input type="range" min="0" max="100" value="0" class="slider" id="ledSlider" onchange="updateLED(this.value)">
        <p>Brilho: <span id="ledVal">0</span>%</p>
        
        <h4>Frequência do LED (Teste de Cintilação)</h4>
        <div class="btn-group">
            <button onclick="updateFreq(1000)">1 kHz</button>
            <button onclick="updateFreq(5000)">5 kHz</button>
        </div>
        <p>Frequência Atual: <span id="freqVal">1000</span> Hz</p>
    </div>

    <div class="card">
        <h3>2. Posição do Servo</h3>
        <input type="range" min="0" max="180" value="90" class="slider" id="servoSlider" onchange="updateServo(this.value)">
        <p>Ângulo: <span id="servoVal">90</span>°</p>
    </div>

    <script>
        function updateLED(val) {
            document.getElementById('ledVal').innerText = val;
            fetch('/setled?val=' + val);
        }
        function updateFreq(hz) {
            document.getElementById('freqVal').innerText = hz;
            fetch('/setfreq?hz=' + hz);
        }
        function updateServo(ang) {
            document.getElementById('servoVal').innerText = ang;
            fetch('/setservo?ang=' + ang);
        }
    </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", CODE_DASHBOARD_HTML);
}

void handleSetLED() {
  if (server.hasArg("val")) {
    brilhoAtual = server.arg("val").toInt();
    int dutyTarget = map(brilhoAtual, 0, 100, 0, 255);
    ledcWrite(PIN_LED, dutyTarget);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void handleSetFreq() {
  if (server.hasArg("hz")) {
    freqLED = server.arg("hz").toInt();
    ledcChangeFrequency(PIN_LED, freqLED, resLED);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void handleSetServo() {
  if (server.hasArg("ang")) {
    anguloAtual = server.arg("ang").toInt();
    int dutyServo = map(anguloAtual, 0, 180, SERVO_MIN_DUTY, SERVO_MAX_DUTY);
    ledcWrite(PIN_SERVO, dutyServo);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void setup() {
  Serial.begin(115200);
  
  ledcAttach(PIN_LED, freqLED, resLED);
  ledcAttach(PIN_SERVO, freqServo, resServo);
  
  int dutyInicial = map(anguloAtual, 0, 180, SERVO_MIN_DUTY, SERVO_MAX_DUTY);
  ledcWrite(PIN_SERVO, dutyInicial);

  WiFi.softAP(ap_ssid, ap_password);
  IPAddress IP = WiFi.softAPIP();
  
  Serial.println(IP); 

  server.on("/", handleRoot);
  server.on("/setled", handleSetLED);
  server.on("/setfreq", handleSetFreq);
  server.on("/setservo", handleSetServo);

  server.begin();
}

void loop() {
  server.handleClient();
}
