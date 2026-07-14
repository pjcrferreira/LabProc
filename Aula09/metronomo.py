# Atividades 4 e 6: Metronomo integrado (servo + buzzer + LED) com ajuste
# de BPM por botoes fisicos e persistencia do estado em disco.
#
# Correcoes em relacao a versao anterior:
#  1. Agendamento por tempo ABSOLUTO (proxima_batida += periodo) em vez de
#     medir e descontar o tempo de execucao: o overshoot do time.sleep()
#     deixa de se acumular como drift.
#  2. time.monotonic() no lugar de time.time(): relogio monotonico nao sofre
#     saltos por ajuste de NTP/RTC, adequado para medir intervalos.
#  3. Servo alterna de lado a cada batida (tique-taque), com o periodo
#     inteiro disponivel para o deslocamento. Antes o codigo exigia 180 graus
#     de curso em 100 ms, fisicamente impossivel para um SG90 (~0,3 s/180).
#  4. Suporte a buzzer passivo (tom via PWM) alem do ativo.
#  5. BPM persistido em arquivo a cada alteracao (tolerancia a falha de
#     energia: ao religar, o metronomo retoma o ultimo andamento).
#  6. Comentarios corrigidos: bouncetime e debounce EM SOFTWARE, feito pela
#     biblioteca RPi.GPIO, e nao um recurso de hardware do SoC.

import RPi.GPIO as GPIO
import time
import threading
import os

# --- Configuracao de pinos (BCM) ---
SERVO_PIN = 12   # Saida PWM 50 Hz para o servo SG90
BUZZER_PIN = 23  # Buzzer (ativo ou passivo, ver flag abaixo)
LED_PIN = 18     # LED de status
BTN_INC = 16     # Botao incrementa BPM (pull-up interno, aciona para GND)
BTN_DEC = 20     # Botao decrementa BPM

BUZZER_PASSIVO = True          # True: gera tom via PWM; False: nivel logico
ARQUIVO_ESTADO = "/home/pi/metronomo_bpm.txt"
BPM_MIN, BPM_MAX, BPM_PASSO = 30, 240, 5
DURACAO_PULSO = 0.1            # duracao do bip e do flash do LED (100 ms)

# --- Estado global ---
bpm = 60
lock = threading.Lock()

def carregar_bpm():
    """Recupera o ultimo BPM salvo (tolerancia a falha de energia)."""
    global bpm
    try:
        with open(ARQUIVO_ESTADO) as f:
            valor = int(f.read().strip())
        if BPM_MIN <= valor <= BPM_MAX:
            bpm = valor
            print(f"BPM restaurado do disco: {bpm}")
    except (OSError, ValueError):
        pass  # primeiro uso ou arquivo corrompido: mantem o padrao

def salvar_bpm(valor):
    """Grava o BPM de forma atomica (escreve em .tmp e renomeia)."""
    try:
        with open(ARQUIVO_ESTADO + ".tmp", "w") as f:
            f.write(str(valor))
        os.replace(ARQUIVO_ESTADO + ".tmp", ARQUIVO_ESTADO)
    except OSError as e:
        print(f"Aviso: falha ao persistir BPM: {e}")

# --- Configuracao de perifericos ---
GPIO.setmode(GPIO.BCM)
GPIO.setup([SERVO_PIN, BUZZER_PIN, LED_PIN], GPIO.OUT)
GPIO.setup([BTN_INC, BTN_DEC], GPIO.IN, pull_up_down=GPIO.PUD_UP)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)   # servos padrao exigem 50 Hz (T = 20 ms)
led_pwm = GPIO.PWM(LED_PIN, 1000)     # 1 kHz: acima da persistencia da visao
servo_pwm.start(7.5)                  # 7,5% = pulso de 1,5 ms = 90 graus
led_pwm.start(0)

if BUZZER_PASSIVO:
    buzzer_pwm = GPIO.PWM(BUZZER_PIN, 1000)  # tom de 1 kHz
    buzzer_pwm.start(0)

def set_servo_angle(angle):
    """Mapeia 0-180 graus em duty cycle de 5,0% (1,0 ms) a 10,0% (2,0 ms)."""
    duty_cycle = 5.0 + (angle / 180.0) * 5.0
    servo_pwm.ChangeDutyCycle(duty_cycle)

def buzzer_on():
    if BUZZER_PASSIVO:
        buzzer_pwm.ChangeDutyCycle(50)
    else:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzzer_off():
    if BUZZER_PASSIVO:
        buzzer_pwm.ChangeDutyCycle(0)
    else:
        GPIO.output(BUZZER_PIN, GPIO.LOW)

def batida(lado_esquerdo):
    """Uma batida: move o pendulo para o lado da vez e pulsa som + luz.

    O servo recebe o comando no instante da batida e tem o periodo inteiro
    (ate a proxima batida) para completar o deslocamento de 90 graus.
    Angulos 45/135 reduzem o curso e permitem acompanhar andamentos altos.
    """
    set_servo_angle(45 if lado_esquerdo else 135)
    buzzer_on()
    led_pwm.ChangeDutyCycle(100)
    time.sleep(DURACAO_PULSO)
    buzzer_off()
    led_pwm.ChangeDutyCycle(0)

# --- Botoes: callbacks executam em thread propria da RPi.GPIO ---
# bouncetime=250 ms e um debounce EM SOFTWARE (a biblioteca descarta eventos
# subsequentes dentro da janela); nao ha filtro de hardware envolvido.
def increment_bpm(channel):
    global bpm
    with lock:
        if bpm < BPM_MAX:
            bpm += BPM_PASSO
            salvar_bpm(bpm)
            print(f"BPM incrementado para: {bpm}")

def decrement_bpm(channel):
    global bpm
    with lock:
        if bpm > BPM_MIN:
            bpm -= BPM_PASSO
            salvar_bpm(bpm)
            print(f"BPM decrementado para: {bpm}")

GPIO.add_event_detect(BTN_INC, GPIO.FALLING, callback=increment_bpm, bouncetime=250)
GPIO.add_event_detect(BTN_DEC, GPIO.FALLING, callback=decrement_bpm, bouncetime=250)

# --- Laco principal com agendamento por tempo absoluto ---
carregar_bpm()
print("Metronomo ativo. Ajuste o andamento pelos botoes fisicos.")

try:
    lado = True
    proxima_batida = time.monotonic()
    while True:
        with lock:
            periodo = 60.0 / bpm

        batida(lado)
        lado = not lado

        # Ancora no instante agendado, nao no instante em que acordou:
        # erros de sleep nao se acumulam de um ciclo para o outro.
        proxima_batida += periodo
        atraso = proxima_batida - time.monotonic()
        if atraso > 0:
            time.sleep(atraso)
        else:
            # Sistema atrasou mais que um periodo (carga da CPU ou BPM
            # reduzido drasticamente): reancora para nao disparar em rajada.
            proxima_batida = time.monotonic()

except KeyboardInterrupt:
    print("\nEncerrando metronomo...")

finally:
    servo_pwm.stop()
    led_pwm.stop()
    if BUZZER_PASSIVO:
        buzzer_pwm.stop()
    GPIO.cleanup()
    print("Recursos de hardware liberados.")
