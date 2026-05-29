#include <WiFi.h>
#include <WebServer.h>
#include "index.h"

// Definição dos pinos para o ESP32-C3 SuperMini
const int ledPins[4] = {2, 3, 4, 5}; // Bit 0 (LSB) até Bit 3 (MSB)

WebServer server(80);

// Configurações do Access Point sem internet
const char* ssid = "Calculadora_ESP32_C3";
const char* password = "poli_computacao";

// Função para atualizar o estado dos leds físicos externos
void atualizarLeds(uint8_t valorBinario) {
  for (int i = 0; i < 4; i++) {
    int bitStatus = (valorBinario >> i) & 0x01;
    digitalWrite(ledPins[i], bitStatus ? HIGH : LOW);
  }
}

void handleRoot() {
  server.send(200, "text/html", MAIN_page);
}

void handleCalcular() {
  if (!server.hasArg("a") || !server.hasArg("b") || !server.hasArg("op")) {
    server.send(400, "application/json", "{\"error\":\"Parametros invalidos\"}");
    return;
  }

  // Recebe os valores via HTTP vindos da interface web
  int valA = server.arg("a").toInt();
  int valB = server.arg("b").toInt();
  String op = server.arg("op");

  // Cast explícito para inteiros sinalizados de 8 bits para isolar manipulação
  int8_t a = (int8_t)valA;
  int8_t b = (int8_t)valB;
  int8_t resultado = 0;
  bool overflow = false;

  if (op == "soma") {
    resultado = a + b;
    // Overflow em C2: Sinais iguais geram resultado com sinal invertido
    if ((a > 0 && b > 0 && resultado < 0) || (a < 0 && b < 0 && resultado >= 0)) {
      overflow = true;
    }
  } else if (op == "sub") {
    resultado = a - b;
    // Overflow na subtração: Sinais diferentes geram estouro
    if ((a >= 0 && b < 0 && resultado < 0) || (a < 0 && b >= 0 && resultado >= 0)) {
      overflow = true;
    }
  }

  // Ajusta o resultado final para o escopo estrito de 4 bits isolando os bits baixos
  uint8_t exibicaoBinaria = (uint8_t)(resultado & 0x0F);
  
  // Tratamento do valor decimal dentro da faixa de 4 bits sinalizados [-8 a +7] para exibição na web
  int8_t resultadoExibicaoDec = (exibicaoBinaria & 0x08) ? (int8_t)(exibicaoBinaria | 0xF0) : (int8_t)exibicaoBinaria;

  // Atualiza fisicamente os pinos dos LEDs no microcontrolador
  atualizarLeds(exibicaoBinaria);

  // Monta string binária formatada para o JSON
  String binStr = "";
  for (int i = 3; i >= 0; i--) {
    binStr += String((exibicaoBinaria >> i) & 0x01);
  }

  // Responde a requisição assíncrona do Javascript
  String jsonResponse = "{";
  jsonResponse += "\"resultadoDecimal\":" + String(resultadoExibicaoDec) + ",";
  jsonResponse += "\"resultadoBinario\":\"" + binStr + "\",";
  jsonResponse += "\"overflow\":" + String(overflow ? "true" : "false");
  jsonResponse += "}";

  server.send(200, "application/json", jsonResponse);
}

void setup() {
  Serial.begin(115200);

  // Configuração dos Pinos dos LEDs
  for (int i = 0; i < 4; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  // Inicializa Rede Local Sem Fio
  WiFi.softAP(ssid, password);
  Serial.println("Access Point Iniciado.");
  Serial.print("IP do WebServer: ");
  Serial.println(WiFi.softAPIP());

  // Define as rotas controladas pelo ESP32
  server.on("/", handleRoot);
  server.on("/calcular", handleCalcular);
  
  server.begin();
  Serial.println("Servidor HTTP ativo.");
}

void loop() {
  server.handleClient();
}