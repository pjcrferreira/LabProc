#include <Arduino.h>

const int ledPins[4] = {2, 3, 4, 5};
uint8_t paraComplementoDeUm(int decimal) {
    if (decimal >= 0) {
        return (uint8_t)(decimal & 0x0F);
    } 
        return (uint8_t)((~abs(decimal)) & 0x0F);
}

int paraDecimalC1(uint8_t c1) {
    c1 = c1 & 0x0F;
    if (c1 & 0x08) {
        return -((~c1) & 0x0F);
    }
    return c1;
}

void limparBufferSerial() {
    while (Serial.available()) {
        Serial.read();
    }
}

void atualizarLeds(uint8_t valor) {
    for (int i = 0; i < 4; i++) {
        int estadoBit = (valor >> i) & 0x01;
        digitalWrite(ledPins[i], estadoBit ? HIGH : LOW);
    }
}

void processarCalculo() {
    Serial.println();
    Serial.println("--- Calculadora 4 Bits em Complemento de Um (C1) ---");
    Serial.println("Digite o Operando A (-7 a +7):");
    while (!Serial.available());
    int opA = Serial.parseInt();
    limparBufferSerial();

    char operacao = 0;

    Serial.println("Digite a operacao (+ ou -):");

    while (true) {
        while (!Serial.available());
        operacao = Serial.read();
        if (operacao == '+' || operacao == '-') {
            break;
        }
    }

    limparBufferSerial();

    Serial.println("Digite o Operando B (-7 a +7):");
    while (!Serial.available());
    int opB = Serial.parseInt();
    limparBufferSerial();

    uint8_t binA = paraComplementoDeUm(opA);
    uint8_t binB = paraComplementoDeUm(opB);

    if (operacao == '-') {
        binB = (~binB) & 0x0F;
    }

    uint16_t somaBruta = (uint16_t)binA + (uint16_t)binB;
    uint8_t resultadoFinal = somaBruta & 0x0F;

    if (somaBruta & 0x10) {
        Serial.println("[C1 INFO] End-around carry detectado!");
        resultadoFinal = (resultadoFinal + 1) & 0x0F;
    }

    atualizarLeds(resultadoFinal);
    Serial.print("Operando A binario: ");
    for (int i = 3; i >= 0; i--) {
        Serial.print((binA >> i) & 0x01);
    }
    Serial.println();

    Serial.print("Operando B binario: ");

    for (int i = 3; i >= 0; i--) {
        Serial.print((binB >> i) & 0x01);
    }

    Serial.println();
    Serial.print("Resultado Final Binario: ");
    for (int i = 3; i >= 0; i--) {
        Serial.print((resultadoFinal >> i) & 0x01);
    }

    Serial.println();
    Serial.print("Resultado Final Decimal Equivalente: ");
    Serial.println(paraDecimalC1(resultadoFinal));
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    for (int i = 0; i < 4; i++) {
        pinMode(ledPins[i], OUTPUT);
        digitalWrite(ledPins[i], LOW);
    }
    Serial.println("Sistema iniciado.");
}

void loop() {
    processarCalculo();
    delay(3000);
}
