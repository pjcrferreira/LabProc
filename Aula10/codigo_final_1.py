import RPi.GPIO as GPIO
import time
import smbus2

# --- CONFIGURAÇÃO DE PINOS E PERIFÉRICOS ---
ROW_PINS = [16, 20, 21, 26]      # Linhas do Teclado
COL_PINS = [19, 13, 6, 5]     # Colunas do Teclado
TRIG_PIN = 14                   # Trigger HC-SR04
ECHO_PIN = 15                   # Echo HC-SR04
SERVO_PIN = 18                  # Servomotor (PWM)
BUZZER_PIN = 12                 # Buzzer

I2C_ADDR = 0x27                 # Ajuste para 0x3F se necessário
PASSWORD_CORRECT = "1234"
DOOR_CLOSED_THRESHOLD_CM = 8.0  # Distância limite para porta fechada (cm)

# --- INICIALIZAÇÃO DO DISPLAY LCD I2C ---
LCD_CHR, LCD_CMD, ENABLE, LCD_BACKLIGHT = 1, 0, 0b00000100, 0b00001000
bus = smbus2.SMBus(1)

def lcd_byte(bits, mode):
    bh = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bl = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(I2C_ADDR, bh)
    bus.write_byte(I2C_ADDR, bh | ENABLE)
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bh & ~ENABLE)
    bus.write_byte(I2C_ADDR, bl)
    bus.write_byte(I2C_ADDR, bl | ENABLE)
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bl & ~ENABLE)

def lcd_init():
    for cmd in [0x33, 0x32, 0x06, 0x0C, 0x28, 0x01]:
        lcd_byte(cmd, LCD_CMD)
    time.sleep(0.005)

def lcd_display(line1, line2=""):
    lcd_byte(0x80, LCD_CMD)
    for c in line1.ljust(16): lcd_byte(ord(c), LCD_CHR)
    lcd_byte(0xC0, LCD_CMD)
    for c in line2.ljust(16): lcd_byte(ord(c), LCD_CHR)

# --- SETUP GPIO ---
GPIO.setmode(GPIO.BCM)
for r in ROW_PINS: GPIO.setup(r, GPIO.OUT, initial=GPIO.HIGH)
for c in COL_PINS: GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(TRIG_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50) # 50Hz para o servomotor
servo.start(0)

# --- FUNÇÕES DE HARDWARE ---
def get_distance():
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    signal_start = time.time()
    signal_stop = time.time()
    timeout = signal_start + 0.03  # Timeout curto (~5 metros)

    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        signal_start = time.time()
        if signal_start > timeout:
            return None

    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        signal_stop = time.time()
        if signal_stop > timeout:
            return None

    return round(((signal_stop - signal_start) * 34300) / 2, 1)

def is_door_closed():
    dist = get_distance()
    return (dist is not None) and (dist <= DOOR_CLOSED_THRESHOLD_CM)

def read_keypad():
    for r_idx, r_pin in enumerate(ROW_PINS):
        GPIO.output(r_pin, GPIO.LOW)
        for c_idx, c_pin in enumerate(COL_PINS):
            if GPIO.input(c_pin) == GPIO.LOW:
                time.sleep(0.15) # Debouncing
                while GPIO.input(c_pin) == GPIO.LOW: pass
                GPIO.output(r_pin, GPIO.HIGH)
                return [['1','2','3','A'],['4','5','6','B'],['7','8','9','C'],['*','0','#','D']][r_idx][c_idx]
        GPIO.output(r_pin, GPIO.HIGH)
    return None

def set_servo(angle):
    dc = 5.0 + (angle / 180.0) * 5.0
    servo.ChangeDutyCycle(dc)
    time.sleep(0.4)
    servo.ChangeDutyCycle(0) # Cancela jitter mecânico

# --- MÁQUINA DE ESTADOS PRINCIPAL ---
def main():
    lcd_init()
    set_servo(90) # Inicia trancada (90°)
    input_buffer = ""
    error_count = 0

    print("Sistema Integrado da Fechadura (HC-SR04) Ativo.")
    
    try:
        while True:
            # Medição ultrassônica da porta
            door_closed = is_door_closed()
            status_str = "Trancada" if door_closed else "Aberta!"
            lcd_display(f"Senha: {'*' * len(input_buffer)}", f"Porta: {status_str}")

            key = read_keypad()
            if key:
                if key == '#': # Botão de Confirmação
                    if input_buffer == PASSWORD_CORRECT:
                        lcd_display("Acesso Permitido", "Destravando...")
                        GPIO.output(BUZZER_PIN, GPIO.HIGH); time.sleep(0.1); GPIO.output(BUZZER_PIN, GPIO.LOW)
                        set_servo(0) # Destrava (0°)
                        time.sleep(3) # Janela inicial para abrir a porta
                        
                        # Aguarda o sensor ultrassônico detectar que a porta foi fechada
                        while not is_door_closed():
                            dist_atual = get_distance()
                            dist_str = f"{dist_atual}cm" if dist_atual else "---"
                            lcd_display("Feche a Porta!", f"Dist: {dist_str}")
                            time.sleep(0.3)
                        
                        lcd_display("Porta Encostada", "Re-trancando...")
                        time.sleep(1)
                        set_servo(90) # Tranca novamente (90°)
                        error_count = 0

                    else:
                        error_count += 1
                        lcd_display("Senha Incorreta!", f"Tentativas: {error_count}/3")
                        GPIO.output(BUZZER_PIN, GPIO.HIGH); time.sleep(0.5); GPIO.output(BUZZER_PIN, GPIO.LOW)
                        time.sleep(1.5)

                        # Bloqueio temporário anti-força bruta
                        if error_count >= 3:
                            for sec in range(30, 0, -1):
                                lcd_display("SISTEMA BLOQUEADO", f"Aguarde {sec}s...")
                                time.sleep(1)
                            error_count = 0
                            
                    input_buffer = ""

                elif key == '*': # Limpar dígito
                    input_buffer = ""
                elif len(input_buffer) < 6 and key not in ['A', 'B', 'C', 'D']:
                    input_buffer += key

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nEncerrando sistema...")
    finally:
        servo.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
