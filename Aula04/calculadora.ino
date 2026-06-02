#include <WiFi.h>
#include <WebServer.h>
#include "index.h"
#include "aritmetica.h"

const int ledPins[4] = {2, 3, 4, 5};
WebServer server(80);

void atualizarLedsFisicos(uint8_t valor) {
    for (int i = 0; i < 4; i++) {
        digitalWrite(ledPins[i], (valor >> i) & 0x01 ? HIGH : LOW);
    }
}

void handleRoot() {
    server.send(200, "text/html", MAIN_page);
}

void handleCalcular() {
    int valA = server.arg("a").toInt();
    int valB = server.arg("b").toInt();
    String op = server.arg("op");

    int16_t a = (int16_t)valA;
    int16_t b = (int16_t)valB;
    
    int32_t resultadoFinal = 0;
    bool overflow = false;
    bool divByZero = false;

    // Alta precisão de telemetria baseada em clock interno do chip (Hardware Timer)
    uint64_t t_inicio = esp_timer_get_time();

    if (op == "soma") { 
        resultadoFinal = executarSoma(a, b, overflow);
    } else if (op == "sub") {
        resultadoFinal = executarSubtracao(a, b, overflow);
    } else if (op == "mult") {
        resultadoFinal = executarMultiplicacao(a, b);
    } else if (op == "fat") {
        resultadoFinal = executarFatorial(a, overflow);
    } else if (op == "div") {
        resultadoFinal = executarDivisao(a, b, divByZero);
    }


    uint64_t t_fim = esp_timer_get_time();
    uint32_t tempoDelta = (uint32_t)(t_fim - t_inicio);
    atualizarLedsFisicos((uint8_t)(resultadoFinal & 0x0F));

    // Formatação da string binária adaptável para até 16 bits de largura de palavra
    String binStr = "";
    int bitsLargura = (op == "fat" || op == "mult") ? 16 : 4;
    for (int i = bitsLargura - 1; i >= 0; i--) {
        binStr += String((resultadoFinal >> i) & 0x01);
    }

    String json = "{";
    json += "\"resultadoDecimal\":" + String(resultadoFinal) + ",";
    json += "\"resultadoBinario\":\"" + binStr + "\",";
    json += "\"tempoUs\":" + String(tempoDelta) + ",";
    json += "\"overflow\":" + String(overflow ? "true" : "false") + ",";
    json += "\"divByZero\":" + String(divByZero ? "true" : "false");
    json += "}";

    server.send(200, "application/json", json);
}

void setup() {
    for (int i = 0; i < 4; i++) {
        pinMode(ledPins[i], OUTPUT);
        digitalWrite(ledPins[i], LOW);
    }
    WiFi.softAP("Calculadora_Iterativa_C3_ERROR", "poli_computacao_2");
    server.on("/", handleRoot);
    server.on("/calcular", handleCalcular);
    server.begin();
}

void loop() {
    server.handleClient();
}
