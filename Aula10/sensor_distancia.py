import RPi.GPIO as GPIO
import time

# Mapeamento de Pinos
TRIG_PIN = 24  # GPIO24 (Saída - Pulso de Disparo)
ECHO_PIN = 25  # GPIO25 (Entrada com Divisor de Tensão)

# Limiar para considerar a porta fechada (em cm)
DOOR_CLOSED_THRESHOLD_CM = 8.0 

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Garante disparo desativado inicialmente
GPIO.output(TRIG_PIN, GPIO.LOW)
time.sleep(0.5)

def get_distance():
    """Gera um pulso ultrassônico e calcula a distância em cm com proteção de Timeout."""
    # Envia pulso de disparo de 10 microssegundos
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    signal_start = time.time()
    signal_stop = time.time()
    timeout = signal_start + 0.04  # Timeout de 40ms (~6,8 metros)

    # Aguarda o pino ECHO ir para NÍVEL ALTO
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        signal_start = time.time()
        if signal_start > timeout:
            return None  # Leitura inválida/fora de alcance

    # Aguarda o pino ECHO retornar a NÍVEL BAIXO
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        signal_stop = time.time()
        if signal_stop > timeout:
            return None

    # Cálculo da distância (Velocidade do som = 34300 cm/s)
    time_elapsed = signal_stop - signal_start
    distance = (time_elapsed * 34300) / 2
    return round(distance, 2)

def is_door_closed():
    dist = get_distance()
    if dist is None:
        return False  # Em caso de falha de leitura, assume porta aberta por segurança
    return dist <= DOOR_CLOSED_THRESHOLD_CM

if __name__ == "__main__":
    print("Iniciando Teste Isolado: Sensor Ultrassônico HC-SR04...")
    try:
        while True:
            distancia = get_distance()
            if distancia is not None:
                status = "FECHADA" if distancia <= DOOR_CLOSED_THRESHOLD_CM else "ABERTA"
                print(f"Distância Medida: {distancia:5.1f} cm | Status: Porta {status}")
            else:
                print("Distância Medida: Fora de Alcance / Falha de Leitura")
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\nTeste encerrado pelo usuário.")
    finally:
        GPIO.cleanup()