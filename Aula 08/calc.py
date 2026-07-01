import RPi.GPIO as GPIO
import time
import smbus2

# =========================================================================
# 1. DRIVER SIMPLIFICADO DO DISPLAY LCD I2C (PCF8574)
# =========================================================================
class I2CLCD1602:
    # Endereço I2C padrão do módulo PCF8574 da Freenove (geralmente 0x27 ou 0x3F)
    LCD_ADDRESS = 0x27
    
    # Comandos do LCD
    LCD_CHR = 1 # Enviando dados
    LCD_CMD = 0 # Enviando comando

    # Linhas do LCD1602
    LINHA_1 = 0x80
    LINHA_2 = 0xC0

    ENABLE = 0b00000100 # Bit de Enable

    def __init__(self):
        self.bus = smbus2.SMBus(1) # Canal 1 do Raspberry Pi
        self.lcd_byte(0x33, self.LCD_CMD) # Inicialização
        self.lcd_byte(0x32, self.LCD_CMD)
        self.lcd_byte(0x06, self.LCD_CMD) # Cursor move para a direita
        self.lcd_byte(0x0C, self.LCD_CMD) # Display Ligado, Cursor Desligado
        self.lcd_byte(0x28, self.LCD_CMD) # Modo 4-bits, 2 linhas
        self.lcd_byte(0x01, self.LCD_CMD) # Limpa display
        time.sleep(0.005)

    def lcd_byte(self, bits, mode):
        # Envia bytes para o chip PCF8574 por I2C
        bits_high = mode | (bits & 0xF0) | 0x08 # 0x08 mantém o backlight ligado
        bits_low = mode | ((bits << 4) & 0xF0) | 0x08
        
        self.bus.write_byte(self.LCD_ADDRESS, bits_high)
        self.lcd_toggle_enable(bits_high)
        
        self.bus.write_byte(self.LCD_ADDRESS, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(0.0005)
        self.bus.write_byte(self.LCD_ADDRESS, (bits | self.ENABLE))
        time.sleep(0.0005)
        self.bus.write_byte(self.LCD_ADDRESS, (bits & ~self.ENABLE))
        time.sleep(0.0005)

    def mostrar_texto(self, mensagem, linha):
        self.lcd_byte(linha, self.LCD_CMD)
        mensagem = mensaje.ljust(16, " ") # Garante preenchimento de 16 caracteres
        for i in range(16):
            self.lcd_byte(ord(mensagem[i]), self.LCD_CHR)

    def limpar(self):
        self.lcd_byte(0x01, self.LCD_CMD)
        time.sleep(0.005)

# =========================================================================
# 2. CONFIGURAÇÃO DO TECLADO MATRICIAL 4x4
# =========================================================================
# Defina os pinos GPIO do Raspberry Pi que você conectou fisicamente ao teclado
PINS_LINHAS = [18, 23, 24, 25]  # R1, R2, R3, R4
PINS_COLUNAS = [12, 16, 20, 21] # C1, C2, C3, C4

MAPA_TECLAS = [
    ['1', '2', '3', '+'], # 'A' vira '+'
    ['4', '5', '6', '-'], # 'B' vira '-'
    ['7', '8', '9', '*'], # 'C' vira '*'
    ['!', '0', '=', '/']  # '*' vira '!', '#' vira '='
]

def inicializar_teclado():
    GPIO.setmode(GPIO.BCM)
    for pin in PINS_LINHAS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
    for pin in PINS_COLUNAS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def ler_teclado():
    for i, pin_linha in enumerate(PINS_LINHAS):
        GPIO.output(pin_linha, GPIO.LOW) # Ativa a linha atual
        for j, pin_coluna in enumerate(PINS_COLUNAS):
            if GPIO.input(pin_coluna) == GPIO.LOW: # Detectou clique (pull-up foi para LOW)
                while GPIO.input(pin_coluna) == GPIO.LOW:
                    time.sleep(0.05) # Debounce simples por software
                GPIO.output(pin_linha, GPIO.HIGH)
                return MAPA_TECLAS[i][j]
        GPIO.output(pin_linha, GPIO.HIGH) # Desativa a linha
    return None

# =========================================================================
# 3. LÓGICA DA CALCULADORA (ULA)
# =========================================================================
def calcular_fatorial(n):
    if n <= 1: return 1
    res = 1
    for i in range(n, 1, -1):
        res *= i
    return res

def executar_calculo(num1, op, num2):
    # Aplica máscara de 4 bits conceitual nos operandos (0 a 15)
    num1 &= 0xF
    num2 &= 0xF
    
    if op == '+':   return (num1 + num2) & 0xF
    if op == '-':   
        if num1 < num2: return "ERR: NEGATIVO"
        return num1 - num2
    if op == '*':   return (num1 * num2) & 0xF
    if op == '/':   
        if num2 == 0: return "ERR: DIV/0" # Tratamento de exceção mandatório
        return num1 // num2
    if op == '!':   return calcular_fatorial(num1) & 0xF
    return "ERR"

# =========================================================================
# 4. FLUXO PRINCIPAL DE EXECUÇÃO
# =========================================================================
def main():
    inicializar_teclado()
    try:
        lcd = I2CLCD1602()
    except Exception as e:
        print(f"Erro ao conectar com o Display LCD I2C: {e}")
        print("Verifique se o endereço I2C (0x27/0x3F) ou as conexões SDA/SCL estão corretas.")
        return

    lcd.mostrar_texto("ULA Standalone", lcd.LINHA_1)
    lcd.mostrar_texto("Aguardando...", lcd.LINHA_2)
    time.sleep(2)
    lcd.limpar()

    expressao = ""
    num1 = None
    op = None

    print("Calculadora Standalone Pronta. Opere diretamente pelos periféricos físicos!")

    while True:
        tecla = ler_teclado()
        if tecla:
            # Caso o usuário aperte para calcular
            if tecla == '=':
                if num1 is not None and op is not None and expressao != "":
                    num2 = int(expressao)
                    resultado = executar_calculo(num1, op, num2)
                    
                    # Exibe no Display LCD
                    lcd.mostrar_texto(f"{num1}{op}{num2}=", lcd.LINHA_1)
                    lcd.mostrar_texto(f"-> {resultado}", lcd.LINHA_2)
                    
                    # Reseta estado para a próxima conta
                    expressao = ""
                    num1 = None
                    op = None
                continue

            # Se for um operador
            if tecla in ['+', '-', '*', '/', '!']:
                if expressao != "":
                    num1 = int(expressao)
                    op = tecla
                    if op == '!': # Fatorial é uma operação unária, calcula direto
                        resultado = executar_calculo(num1, op, 0)
                        lcd.mostrar_texto(f"{num1}!", lcd.LINHA_1)
                        lcd.mostrar_texto(f"-> {resultado}", lcd.LINHA_2)
                        expressao = ""
                        num1 = None
                        op = None
                    else:
                        lcd.mostrar_texto(f"{num1} {op}", lcd.LINHA_1)
                        lcd.mostrar_texto("", lcd.LINHA_2)
                        expressao = ""
                continue

            # Se for dígito numérico, vai concatenando na string
            expressao += tecla
            lcd.mostrar_texto(expressao, lcd.LINHA_2)
            
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nPrograma encerrado.")