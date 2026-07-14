# Atividade 2: Controle isolado do servomotor (SG90) via PWM
# Servo padrao: periodo de 20 ms (50 Hz); largura de pulso de 1,0 ms (0 grau)
# a 2,0 ms (180 graus), com 1,5 ms correspondendo a 90 graus (posicao neutra).
import RPi.GPIO as GPIO
import time

SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz obrigatorio para servos padrao
servo_pwm.start(7.5)                 # 7,5% de 20 ms = 1,5 ms -> 90 graus

def set_servo_angle(angle):
    """Converte angulo (0 a 180) em duty cycle (5,0% a 10,0%)."""
    duty_cycle = 5.0 + (angle / 180.0) * 5.0
    servo_pwm.ChangeDutyCycle(duty_cycle)

try:
    # Teste 1: posicoes discretas (registrar se o angulo real corresponde)
    for angulo in [0, 45, 90, 135, 180]:
        print(f"Posicionando em {angulo} graus")
        set_servo_angle(angulo)
        time.sleep(1.5)  # SG90 leva ~0,3 s para percorrer 180 graus sem carga

    # Teste 2: varredura continua (avaliar suavidade e jitter do PWM por
    # software - com RPi.GPIO e esperado algum tremor na posicao parada)
    print("Varredura continua 0 -> 180 -> 0")
    for angulo in list(range(0, 181, 5)) + list(range(180, -1, -5)):
        set_servo_angle(angulo)
        time.sleep(0.05)

    # Teste 3: parar de enviar pulsos (duty 0) - o servo relaxa e o
    # tremor causado pelo jitter do PWM por software desaparece.
    print("Duty 0: servo sem pulsos (relaxado)")
    servo_pwm.ChangeDutyCycle(0)
    time.sleep(3)

except KeyboardInterrupt:
    pass
finally:
    servo_pwm.stop()
    GPIO.cleanup()
