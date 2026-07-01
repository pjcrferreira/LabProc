import time
import math
import statistics

# Número de iterações para obter relevância estatística (mitiga desvios do SO)
OP_ITERATIONS = 1000

def executar_benchmark():
    # Definição dos valores conceituais de entrada (4 bits)
    num1 = 15
    num2 = 3
    
    # -------------------------------------------------------------------------
    # 1. BENCHMARK DA SOMA
    # -------------------------------------------------------------------------
    tempos_soma = []
    for _ in range(OP_ITERATIONS):
        t_inicio = time.perf_counter_ns()
        _ = num1 + num2
        t_fim = time.perf_counter_ns()
        tempos_soma.append(t_fim - t_inicio)
        
    media_soma = statistics.mean(tempos_soma)
    std_soma = statistics.stdev(tempos_soma)
    print(f"Soma:          {media_soma:.2f} ns +/- {std_soma:.2f} ns")

    # -------------------------------------------------------------------------
    # 2. BENCHMARK DA SUBTRAÇÃO
    # -------------------------------------------------------------------------
    tempos_sub = []
    for _ in range(OP_ITERATIONS):
        # Proteção e validação lógica de underflow na ULA
        if num1 < num2:
            continue
        t_inicio = time.perf_counter_ns()
        _ = num1 - num2
        t_fim = time.perf_counter_ns()
        tempos_sub.append(t_fim - t_inicio)
        
    media_sub = statistics.mean(tempos_sub)
    std_sub = statistics.stdev(tempos_sub)
    print(f"Subtracao:     {media_sub:.2f} ns +/- {std_sub:.2f} ns")

    # -------------------------------------------------------------------------
    # 3. BENCHMARK DA MULTIPLICAÇÃO
    # -------------------------------------------------------------------------
    tempos_mul = []
    for _ in range(OP_ITERATIONS):
        t_inicio = time.perf_counter_ns()
        _ = num1 * num2
        t_fim = time.perf_counter_ns()
        tempos_mul.append(t_fim - t_inicio)
        
    media_mul = statistics.mean(tempos_mul)
    std_mul = statistics.stdev(tempos_mul)
    print(f"Multiplicacao: {media_mul:.2f} ns +/- {std_mul:.2f} ns")

    # -------------------------------------------------------------------------
    # 4. BENCHMARK DO FATORIAL
    # -------------------------------------------------------------------------
    tempos_fat = []
    for _ in range(OP_ITERATIONS):
        t_inicio = time.perf_counter_ns()
        _ = math.factorial(num1)
        t_fim = time.perf_counter_ns()
        tempos_fat.append(t_fim - t_inicio)
        
    media_fat = statistics.mean(tempos_fat)
    std_fat = statistics.stdev(tempos_fat)
    print(f"Fatorial ({num1}!): {media_fat:.2f} ns +/- {std_fat:.2f} ns")

if __name__ == "__main__":
    print(f"Iniciando Coleta Estatistica ({OP_ITERATIONS} amostras por operador)...")
    executar_benchmark()