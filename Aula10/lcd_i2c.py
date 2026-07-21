import smbus2
import time

# Endereço I2C típico do PCF8574 (0x27 ou 0x3F)
I2C_ADDR = 0x27
LCD_WIDTH = 16  # Caracteres por linha

# BITS de Controle
LCD_CHR = 1  # Modo Dados
LCD_CMD = 0  # Modo Comando
ENABLE = 0b00000100 # Bit Enable
LCD_BACKLIGHT = 0b00001000  # LUZ de Fundo ligada

bus = smbus2.SMBus(1)  # Barramento I2C 1 do Raspberry Pi 3

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.005)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

if __name__ == "__main__":
    print("Iniciando Teste Isolado: Display LCD 16x2 I2C...")
    lcd_init()
    lcd_string("Fechadura RPi 3", 0x80)  # Linha 1
    lcd_string("Status: Teste OK", 0xC0)  # Linha 2
    time.sleep(3)