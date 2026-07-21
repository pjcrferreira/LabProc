import RPi.GPIO as GPIO
import time

SERVO_PIN = 18   # GPIO18 (PWM Hardware)
BUZZER_PIN = 23  # GPIO23 (Buzzer)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50) # 50Hz para servomotor
servo.start(0)

def set_lock_state(locked=True):
    if locked:
        # Posição Trancado: 90 graus (~7.5% duty cycle)
        servo.ChangeDutyCycle(7.5)
        print("Atuador: Fechadura TRANCADA")
    else:
        # Posição Destrancado: 0 graus (~5.0% duty cycle)
        servo.ChangeDutyCycle(5.0)
        print("Atuador: Fechadura DESTRANCADA")
    time.sleep(0.5)
    servo.ChangeDutyCycle(0) # Elimina trepidação (jitter) no servo

def beep_success():
    for _ in range(2):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.08)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.08)

def beep_error():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.6)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

if __name__ == "__main__":
    print("Iniciando Teste Isolado: Atuador Servomotor e Buzzer...")
    try:
        set_lock_state(False)
        beep_success()
        time.sleep(2)
        set_lock_state(True)
        beep_error()
    finally:
        servo.stop()
        GPIO.cleanup()