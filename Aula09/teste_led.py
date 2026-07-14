# Atividade 1: Controle de LED via PWM em diversas frequencias
# Objetivo: observar a partir de qual frequencia o olho humano deixa de
# perceber a cintilacao (persistencia da visao) e registrar os resultados.
import RPi.GPIO as GPIO
import time

LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Frequencias de teste, em Hz. Abaixo de ~50 Hz espera-se cintilacao visivel.
FREQUENCIAS = [1, 2, 5, 10, 25, 50, 100, 500, 1000]

led_pwm = GPIO.PWM(LED_PIN, FREQUENCIAS[0])
led_pwm.start(50)  # duty cycle fixo em 50% para isolar o efeito da frequencia

try:
    for f in FREQUENCIAS:
        led_pwm.ChangeFrequency(f)
        print(f"Frequencia: {f} Hz (duty 50%) - observe o LED por 5s")
        time.sleep(5)

    # Segundo experimento: com frequencia fixa (1 kHz), varrer o duty cycle
    # para observar o controle de brilho (dimmer).
    led_pwm.ChangeFrequency(1000)
    print("Varredura de duty cycle a 1 kHz (0% -> 100%)")
    for duty in range(0, 101, 5):
        led_pwm.ChangeDutyCycle(duty)
        print(f"  duty = {duty}%")
        time.sleep(0.5)

except KeyboardInterrupt:
    pass
finally:
    led_pwm.stop()
    GPIO.cleanup()
