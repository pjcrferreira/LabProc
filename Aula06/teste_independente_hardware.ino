// --- Definições de Pinos para Teste Isolado em Bancada ---
#define LED_TEST_PIN   27  // Pino conectado ao LED Externo (Requer Resistor de ~220 Ohms em série)
#define BUTTON_TEST_PIN 25  // Pino conectado ao Botão Externo

void setup() {
  Serial.begin(115200);
  
  pinMode(LED_TEST_PIN, OUTPUT);
  // Uso explícito de INPUT_PULLUP caso a protoboard não utilize resistor físico externo de pull-up
  pinMode(BUTTON_TEST_PIN, INPUT_PULLUP); 
  
  Serial.println("[STATUS DE ENG] Inicializando Validação de Hardware Isolada.");
  Serial.println("Pressione o botão externo na protoboard para verificar se o circuito acende o LED.");
}

void loop() {
  // Leitura direta por varredura contínua (Polling Simples)
  int estadoBotao = digitalRead(BUTTON_TEST_PIN);
  
  // Com lógica INPUT_PULLUP, o pino em repouso lê HIGH. Ao pressionar, vai para LOW.
  if (estadoBotao == LOW) {
    digitalWrite(LED_TEST_PIN, HIGH);
    Serial.println("[HARDWARE OK] Botão detectado em nível lógico BAIXO (Pressionado) -> LED ABERTO.");
  } else {
    digitalWrite(LED_TEST_PIN, LOW);
  }
  
  delay(50); // Delay curto para estabilização rudimentar do console serial
}