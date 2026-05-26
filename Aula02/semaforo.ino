#define LED_BUILTIN 8
void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  neopixelWrite(LED_BUILTIN, 0, 50, 0);  // verde
  delay(3000);                      // 3 seconds
  neopixelWrite(LED_BUILTIN, 50, 50, 0);   // amarelo
  delay(1000);                      // 1 second
  neopixelWrite(LED_BUILTIN, 50, 0, 0);   // vermelho
  delay(4000);                      // 4 seconds
}
