import RPi.GPIO as GPIO
import time
import smbus2

# --- CONFIGURAÇÃO DE PINOS E PERIFÉRICOS ---
ROW_PINS = [6, 13, 19, 26]
COL_PINS = [12, 16, 20, 21]
SENSOR_PIN = 17
SERVO_PIN = 18
BUZZER_PIN = 23

I2C_ADDR = 0x27
PASSWORD_CORRECT = "1234"

# LCD Config
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

# GPIO Setup
GPIO.setmode(GPIO.BCM)
for r in ROW_PINS: GPIO.setup(r, GPIO.OUT, initial=GPIO.HIGH)
for c in COL_PINS: GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

def read_keypad():
    for r_idx, r_pin in enumerate(ROW_PINS):
        GPIO.output(r_pin, GPIO.LOW)
        for c_idx, c_pin in enumerate(COL_PINS):
            if GPIO.input(c_pin) == GPIO.LOW:
                time.sleep(0.15)
                while GPIO.input(c_pin) == GPIO.LOW: pass
                GPIO.output(r_pin, GPIO.HIGH)
                return [['1','2','3','A'],['4','5','6','B'],['7','8','9','C'],['*','0','#','D']][r_idx][c_idx]
        GPIO.output(r_pin, GPIO.HIGH)
    return None

def set_servo(angle):
    dc = 5.0 + (angle / 180.0) * 5.0
    servo.ChangeDutyCycle(dc)
    time.sleep(0.4)
    servo.ChangeDutyCycle(0)

# --- MÁQUINA DE ESTADOS INTEGRADA ---
def main():
    lcd_init()
    set_servo(90) # Inicia trancado
    input_buffer = ""
    error_count = 0

    print("Sistema Integrado da Fechadura Ativo.")
    
    try:
        while True:
            door_closed = (GPIO.input(SENSOR_PIN) == GPIO.LOW) # Estado do sensor
            status_str = "Trancada" if door_closed else "Aberta!"
            lcd_display(f"Senha: {'*' * len(input_buffer)}", f"Porta: {status_str}")

            key = read_keypad()
            if key:
                if key == '#': # Confirmação
                    if input_buffer == PASSWORD_CORRECT:
                        lcd_display("Acesso Permitido", "Destravando...")
                        GPIO.output(BUZZER_PIN, GPIO.HIGH); time.sleep(0.1); GPIO.output(BUZZER_PIN, GPIO.LOW)
                        set_servo(0) # Destrava
                        time.sleep(5) # Janela de acesso
                        
                        # Aguarda a porta ser fechada pelo sensor antes de rearmar a tranca
                        while GPIO.input(SENSOR_PIN) == GPIO.HIGH:
                            lcd_display("Feche a Porta!", "Aguardando...")
                            time.sleep(0.5)
                        
                        set_servo(90) # Re-tranca
                        error_count = 0
                    else:
                        error_count += 1
                        lcd_display("Senha Incorreta!", f"Tentativas: {error_count}/3")
                        GPIO.output(BUZZER_PIN, GPIO.HIGH); time.sleep(0.5); GPIO.output(BUZZER_PIN, GPIO.LOW)
                        time.sleep(1.5)

                        if error_count >= 3:
                            for sec in range(30, 0, -1):
                                lcd_display("SISTEMA BLOQUEADO", f"Aguarde {sec}s...")
                                time.sleep(1)
                            error_count = 0
                    input_buffer = ""

                elif key == '*': # Limpa Entrada
                    input_buffer = ""
                elif len(input_buffer) < 6 and key not in ['A', 'B', 'C', 'D']:
                    input_buffer += key

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        servo.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()