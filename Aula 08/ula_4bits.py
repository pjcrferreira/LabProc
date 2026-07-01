import sys

def ula_4bits():
    print("--- Simulador de ULA Binária de 4 Bits (Python) ---")
    print("Operações: + (Soma), - (Subtração), * (Multiplicação), / (Divisão), ! (Fatorial)")
    print("Digite no formato: [op] [num1] [num2] (Exemplo: + 5 3)")
    print("Para o Fatorial, o num2 é ignorado (Exemplo: ! 4 0)")
    print("-" * 50)

    try:
        entrada = input("> ").strip().split()
        if not entrada:
            return
        
        operador = entrada[0]
        # Aplica uma máscara de bits (& 0xF) para garantir que as entradas fiquem estritamente no escopo de 4 bits (0 a 15)
        num1 = int(entrada[1]) & 0xF
        num2 = int(entrada[2]) & 0xF if len(entrada) > 2 else 0

        print(f"Inputs convertidos para 4-bits -> Num1: {num1} (bin: {num1:04b}) | Num2: {num2} (bin: {num2:04b})")

        # ---------------------------------------------------------------------
        # DECODIFICADOR DE OPCODE E PROCESSAMENTO DA ULA
        # ---------------------------------------------------------------------
        if operador == '+':
            resultado_bruto = num1 + num2
            # Em hardware de 4 bits, o resultado máximo é 15 (1111). Se passar, há overflow.
            resultado_final = resultado_bruto & 0xF
            print(f"Resultado da Soma: {resultado_final} (bin: {resultado_final:04b})")
            if resultado_bruto > 15:
                print("AVISO: Houve estouro de capacidade (Overflow do 5º bit descartado)!")

        elif operador == '-':
            # Validação de sinal/underflow na ULA
            if num1 < num2:
                print("ERR: VALOR NEGATIVO (Flag de sinal ativada. Subtração de 4 bits sem sinal inválida).")
                return
            resultado_final = num1 - num2
            print(f"Resultado da Subtração: {resultado_final} (bin: {resultado_final:04b})")

        elif operador == '*':
            resultado_bruto = num1 * num2
            resultado_final = resultado_bruto & 0xF
            print(f"Resultado da Multiplicação: {resultado_final} (bin: {resultado_final:04b})")
            if resultado_bruto > 15:
                print(f"AVISO: Houve OVERFLOW! O resultado real seria {resultado_bruto}, mas foi truncado para 4 bits.")

        elif operador == '/':
            # Tratamento mandatório de exceção contra divisão por zero para evitar quebra do fluxo
            if num2 == 0:
                print("ERR: DIV BY 0! Operação abortada para preservar a estabilidade da ULA.")
                return
            resultado_final = num1 // num2  # Divisão inteira
            print(f"Resultado da Divisão: {resultado_final} (bin: {resultado_final:04b})")

        elif operador == '!':
            # Cálculo iterativo do Fatorial
            resultado_bruto = 1
            for i in range(num1, 1, -1):
                resultado_bruto *= i
            
            resultado_final = resultado_bruto & 0xF
            print(f"Resultado do Fatorial de {num1}: {resultado_final} (bin: {resultado_final:04b})")
            if resultado_bruto > 15:
                print(f"AVISO: OVERFLOW CRÍTICO! {num1}! equivale a {resultado_bruto}, excedendo os 4 bits.")

        else:
            print("ERR: Operador inválido ou não reconhecido pelo decodificador.")

    except (ValueError, IndexError):
        print("ERR: Formato de entrada incorreto. Use: [operador] [num1] [num2]")

if __name__ == "__main__":
    while True:
        ula_4bits()
        print("\nDeseja realizar outro cálculo? (s/n)")
        if input("> ").lower().strip() != 's':
            print("Encerrando simulador.")
            sys.exit(0)
        print("\n" + "="*50 + "\n")