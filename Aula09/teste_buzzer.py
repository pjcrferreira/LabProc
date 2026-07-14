# Atividade 3: Controle isolado do buzzer
# IMPORTANTE: identificar o tipo de buzzer do kit antes do teste.
#  - Buzzer ATIVO: possui oscilador interno; basta nivel logico alto (GPIO.output).
#  - Buzzer PASSIVO: e um transdutor; precisa receber uma onda quadrada (PWM)
#    na frequencia do tom desejado, senao produz apenas um "clique".
import RPi.GPIO as GPIO
import time

BUZZER_PIN = 23      # BCM 23 (pino fisico 16)
BUZZER_PASSIVO = True  # ajustar conforme o hardware disponivel no laboratorio

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    if BUZZER_PASSIVO:
        # Gera tons de diferentes frequencias via PWM (duty 50%)
        buzzer_pwm = GPIO.PWM(BUZZER_PIN, 440)
        buzzer_pwm.start(0)
        for freq in [262, 440, 880, 1000, 2000, 4000]:
            print(f"Tom de {freq} Hz por 1s")
            buzzer_pwm.ChangeFrequency(freq)
            buzzer_pwm.ChangeDutyCycle(50)
            time.sleep(1.0)
            buzzer_pwm.ChangeDutyCycle(0)  # silencio entre tons
            time.sleep(0.5)
        buzzer_pwm.stop()
    else:
        # Buzzer ativo: liga/desliga com nivel logico, variando a duracao
        for duracao in [0.05, 0.1, 0.2, 0.5]:
            print(f"Bip de {int(duracao * 1000)} ms")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(duracao)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(1.0)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
