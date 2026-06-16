#include <WiFi.h>
#include <WebServer.h>

// --- Definições de Pinos (Mapeamento de Hardware) ---
#define ADC_LDR_PIN    4
#define BUTTON_SOS_PIN 3
#define LED_BUILTIN    8

// --- Configurações de Rede (Ajustar conforme o laboratório) ---
// usar esp32 como Access Point (AP) para evitar dependência de infraestrutura Wi-Fi do laboratório
const char* ssid     = "ERROR418";
const char* password = "teapot123";

WebServer server(80);

// --- Limiares e Constantes ---
const int LIMIAR_NOTURNO = 500;             // Limiar na escala de 0 a 4095
const unsigned long DEBOUNCE_DELAY = 200;    // Janela de debounce em milissegundos
const unsigned long SOS_DURATION = 3000;    // Duração do estado de emergência (3s)

// --- Variáveis Voláteis (Modificadas na ISR) ---
volatile bool sosSolicitado = false;
volatile unsigned long ultimaInterrupcaoTime = 0;

// --- Variáveis de Controle de Tempo no Loop (Sem Delay Bloqueante) ---
unsigned long ultimaLeituraLDR = 0;
unsigned long ultimoPiscaAmarelo = 0;
bool estadoLedAmarelo = false;

// Instâncias de leitura local do ADC
int valorAdcLdr = 4095;

// ============================================================================
// ROTINA DE SERVIÇO DE INTERRUPÇÃO (ISR) - HARDWARE CRÍTICO
// ============================================================================
void IRAM_ATTR isrBotaoSOS() {
  unsigned long tempoAtual = millis();
  
  // Tratamento de Debounce por Software (Filtro de Repiques Mecânicos)
  if ((tempoAtual - ultimaInterrupcaoTime) > DEBOUNCE_DELAY) {
    sosSolicitado = true;
    ultimaInterrupcaoTime = tempoAtual;
  }
}

// ============================================================================
// HANDLERS DO SERVIDOR WEB (INTERFACE HTTP)
// ============================================================================
void handleRoot() {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'>";
  html += "<title>PCS3732 - Telemetria Smart Monitoring</title>";
  html += "<meta http-equiv='refresh' content='1'>"; // Atualização automática >= 1Hz
  html += "<style>body{font-family:Arial,sans-serif; text-align:center; padding-top:50px; background-color:#f4f4f4;}";
  html += ".container{background:white; padding:30px; display:inline-block; border-radius:10px; box-shadow:0px 0px 10px rgba(0,0,0,0.1);}";
  html += "h1{color:#333;} .value{font-size:48px; font-weight:bold; color:#0056b3;}</style></head><body>";
  html += "<div class='container'><h1>Sistema de Monitoramento Inteligente</h1>";
  html += "<p>Leitura do Conversor ADC (LDR):</p>";
  html += "<div class='value'>" + String(valorAdcLdr) + "</div>";
  html += "<p>Estado do Ambiente: " + String((valorAdcLdr >= LIMIAR_NOTURNO) ? "NOTURNO (Baixa Luz)" : "DIURNO (Ok)") + "</p>";
  html += "</div></body></html>";
  
  server.send(200, "text/html", html);
}

// ============================================================================
// CONFIGURAÇÕES INICIAIS DO SISTEMA
// ============================================================================
void setup() {
  Serial.begin(115200);
  
  // Configuração das direções das portas GPIO
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Configuração do botão com resistor interno de Pull-Up preventivo
  pinMode(BUTTON_SOS_PIN, INPUT_PULLUP);
  
  // Inicialização das saídas em nível lógico baixo
  neopixelWrite(LED_BUILTIN, 0, 0, 0);  // apaga todas as luzes
  
  // Inicialização do Módulo Wi-Fi em Modo Access Point (AP) para criar uma rede local isolada
  WiFi.softAP(ssid, password);
  Serial.println("\nWi-Fi AP Iniciado com sucesso!");
  Serial.print("Endereço IP do ESP32 (Webserver Local): ");
  Serial.println(WiFi.localIP());
  
  // Registro das rotas HTTP do servidor
  server.on("/", handleRoot);
  server.begin();
  
  // Associação da Interrupção de Hardware Externa (Gatilho na Borda de Descida)
  attachInterrupt(digitalPinToInterrupt(BUTTON_SOS_PIN), isrBotaoSOS, FALLING);
}

// ============================================================================
// LOOP PRINCIPAL DE EXECUÇÃO (POLLING DE BAIXA PRIORIDADE)
// ============================================================================
void loop() {
  // Processa requisições HTTP de maneira não-bloqueante
  server.handleClient();
  
  unsigned long tempoCorrente = millis();
  
  // --------------------------------------------------------------------------
  // FLUXO DE PRIORIDADE MÁXIMA: TRATAMENTO DA INTERRUPÇÃO DO BOTÃO SOS
  // --------------------------------------------------------------------------
  if (sosSolicitado) {
    Serial.println("[ALERTA CRÍTICO] - Botão SOS Acionado! Entrando na ISR de Software.");
    
    // Força o desligamento imediato da sinalização de fundo (Amarela)
    neopixelWrite(LED_BUILTIN, 0, 0, 0);  // apaga todas as luzes
    
    // Mantém o LED Vermelho fixo de forma prioritária por 3 segundos
    neopixelWrite(LED_BUILTIN, 50, 0, 0);  // vermelho
    delay(SOS_DURATION); // Bloqueio controlado aceitável exclusivamente no disparo de segurança
    neopixelWrite(LED_BUILTIN, 0, 0, 0);  // apaga todas as luzes
    
    // Desarma a flag de interrupção para permitir novos ciclos de emergência
    sosSolicitado = false;
    
    // Reseta temporizadores para impedir transições bruscas pós-retorno de contexto
    tempoCorrente = millis();
    ultimoPiscaAmarelo = tempoCorrente;
    ultimaLeituraLDR = tempoCorrente;
    
    Serial.println("[RETORNO DE CONTEXTO] - Retornando ao Loop Principal com segurança.");
  }
  
  // --------------------------------------------------------------------------
  // TELEMETRIA DE SEGUNDO PLANO: LEITURA DO ADC DO LDR (Frequência = 1Hz)
  // --------------------------------------------------------------------------
  if (tempoCorrente - ultimaLeituraLDR >= 1000) {
    valorAdcLdr = analogRead(ADC_LDR_PIN);
    Serial.print("[TELEMETRIA] Valor Analógico Lido do LDR (ADC 12-bit): ");
    Serial.println(valorAdcLdr);
    ultimaLeituraLDR = tempoCorrente;
  }
  
  // --------------------------------------------------------------------------
  // MÁQUINA DE ESTADOS DO LED: ALERTA DE BAIXA LUMINOSIDADE (Frequência = 0.5Hz / 2s)
  // --------------------------------------------------------------------------
  if (valorAdcLdr >= LIMIAR_NOTURNO) {
    if (tempoCorrente - ultimoPiscaAmarelo >= 2000) {
      estadoLedAmarelo = !estadoLedAmarelo;
      neopixelWrite(LED_BUILTIN, estadoLedAmarelo ? 25 : 0, estadoLedAmarelo ? 25 : 0, 0);  // amarelo piscando
      ultimoPiscaAmarelo = tempoCorrente;
    }
  } else {
    // Se a luminosidade estiver normal, garante o LED apagado
    neopixelWrite(LED_BUILTIN, 0, 0, 0);  // apaga todas as luzes
    estadoLedAmarelo = false;
  }
}
