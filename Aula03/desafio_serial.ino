#include <Arduino.h>

// Converte um número decimal comum para representação de 4 bits em Complemento de Um
uint8_t paraComplementoDeUm(int decimal) {
    if (decimal >= 0) {
        return (uint8_t)(decimal & 0x0F);
    } else {
        // Inverte todos os bits do valor absoluto em 4 bits
        return (uint8_t)((~abs(decimal)) & 0x0F);
    }
}

// Converte uma representação binária de 4 bits em Complemento de Um para decimal comum
int paraDecimalC1(uint8_t c1) {
    c1 = c1 & 0x0F;
    if (c1 & 0x08) { // Bit mais significativo (sinal) é 1
        return -((~c1) & 0x0F);
    }
    return c1;
}

void processarCalculo() {
    Serial.println("\n--- Calculadora 4 Bits em Complemento de Um (C1) ---");
    Serial.println("Digite o Operando A (-7 a +7):");
    while (!Serial.available());
    int opA = Serial.parseInt();
    
    Serial.println("Digite a operacao (+ ou -):");
    while (!Serial.available());
    char operacao = Serial.read();
    while (Serial.available()) Serial.read(); // Limpa buffer residual
    
    Serial.println("Digite o Operando B (-7 a +7):");
    while (!Serial.available());
    int opB = Serial.parseInt();

    uint8_t binA = paraComplementoDeUm(opA);
    uint8_t binB = paraComplementoDeUm(opB);

    if (operacao == '-') {
        // Subtrair em C1 é somar com o inverso binário (complemento) de B
        binB = (~binB) & 0x0F;
    }

    // Executa a soma básica de 4 bits
    uint16_t somaBruta = (uint16_t)binA + (uint16_t)binB;
    uint8_t resultadoFinal = somaBruta & 0x0F;

    // Lógica do End-Around Carry (Vai-um cíclico obrigatório do C1)
    if (somaBruta & 0x10) { 
        Serial.println("[C1 INFO] End-around carry detectado! Somando 1 ao LSB.");
        resultadoFinal = (resultadoFinal + 1) & 0x0F;
    }

    // Impressão dos resultados estruturados
    Serial.print("Operando A binario: "); Serial.println(binA, BIN);
    Serial.print("Operando B binario: "); Serial.println(binB, BIN);
    Serial.print("Resultado Final Binario: ");
    for (int i = 3; i >= 0; i--) Serial.print((resultadoFinal >> i) & 0x01);
    Serial.println();
    
    Serial.print("Resultado Final Decimal Equivalente: ");
    Serial.println(paraDecimalC1(resultadoFinal));
}

void setup() {
    Serial.begin(115200);
    delay(1000);
}

void loop() {
    processarCalculo();
    delay(3000);
}