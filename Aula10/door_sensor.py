import RPi.GPIO as GPIO
import time

SENSOR_PIN = 17  # GPIO17 para leitura do Reed Switch ou Sensor Óptico

GPIO.setmode(GPIO.BCM)
# Pull-up interno: pino em nível ALTO quando o contato mecânico/magnético está aberto
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_door_closed():
    # Retorna True se a porta estiver fechada (contato encostado no GND)
    return GPIO.input(SENSOR_PIN) == GPIO.LOW

if __name__ == "__main__":
    print("Iniciando Teste Isolado: Sensor de Estado da Porta...")
    try:
        while True:
            if is_door_closed():
                print("Status da Porta: FECHADA")
            else:
                print("Status da Porta: ABERTA [ALERTA]")
            time.sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()