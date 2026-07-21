import RPi.GPIO as GPIO
import time

class Keypad4x4:
    def __init__(self, row_pins=[6, 13, 19, 26], col_pins=[12, 16, 20, 21]):
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.keymap = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]
        GPIO.setmode(GPIO.BCM)
        # Configura linhas como saída e nível alto
        for r in self.row_pins:
            GPIO.setup(r, GPIO.OUT)
            GPIO.output(r, GPIO.HIGH)
        # Configura colunas como entrada com Pull-Up interno
        for c in self.col_pins:
            GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_key(self):
        key_pressed = None
        for r_idx, r_pin in enumerate(self.row_pins):
            GPIO.output(r_pin, GPIO.LOW)  # Ativa a linha atual
            for c_idx, c_pin in enumerate(self.col_pins):
                if GPIO.input(c_pin) == GPIO.LOW:  # Tecla pressionada encosta no GND
                    key_pressed = self.keymap[r_idx][c_idx]
                    # Debouncing básico via software
                    time.sleep(0.2)
                    while GPIO.input(c_pin) == GPIO.LOW:
                        time.sleep(0.01)
            GPIO.output(r_pin, GPIO.HIGH)  # Desativa a linha
        return key_pressed

if __name__ == "__main__":
    print("Iniciando Teste Isolado: Teclado Matricial 4x4...")
    keypad = Keypad4x4()
    try:
        while True:
            k = keypad.read_key()
            if k:
                print(f"Tecla Pressionada: {k}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        GPIO.cleanup()