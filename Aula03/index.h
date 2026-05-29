#ifndef INDEX_H
#define INDEX_H

const char MAIN_page[] PROGMEM = R"=====(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora 4-Bits RISC-V (C3)</title>
    <style>
        body { font-family: 'Arial', sans-serif; background-color: #f4f6f9; color: #333; text-align: center; padding: 20px; }
        .container { max-width: 450px; background: white; margin: 0 auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h2 { color: #1e3a8a; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; text-align: left; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        select, button { width: 100%; padding: 10px; font-size: 16px; border-radius: 6px; border: 1px solid #ccc; box-sizing: border-box; }
        button { background-color: #1e3a8a; color: white; border: none; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { background-color: #3b82f6; }
        .result-box { margin-top: 25px; padding: 15px; border-radius: 8px; background-color: #eff6ff; border: 1px solid #bfdbfe; font-size: 18px; }
        .overflow-badge { display: none; margin-top: 15px; padding: 10px; background-color: #ef4444; color: white; font-weight: bold; border-radius: 6px; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>

<div class="container">
    <h2>Calculadora Binária de 4 Bits</h2>
    
    <div class="form-group">
        <label for="paramA">Operando A (Sinalizado C2):</label>
        <select id="paramA">
            <option value="7">+7 (0111)</option>
            <option value="6">+6 (0110)</option>
            <option value="5">+5 (0101)</option>
            <option value="4">+4 (0100)</option>
            <option value="3">+3 (0011)</option>
            <option value="2">+2 (0010)</option>
            <option value="1">+1 (0001)</option>
            <option value="0" selected>0 (0000)</option>
            <option value="-1">-1 (1111)</option>
            <option value="-2">-2 (1110)</option>
            <option value="-3">-3 (1101)</option>
            <option value="-4">-4 (1100)</option>
            <option value="-5">-5 (1011)</option>
            <option value="-6">-6 (1010)</option>
            <option value="-7">-7 (1001)</option>
            <option value="-8">-8 (1000)</option>
        </select>
    </div>

    <div class="form-group">
        <label for="operacao">Operação:</label>
        <select id="operacao">
            <option value="soma">Soma (+)</option>
            <option value="sub">Subtração (-)</option>
        </select>
    </div>

    <div class="form-group">
        <label for="paramB">Operando B (Sinalizado C2):</label>
        <select id="paramB">
            <option value="7">+7 (0111)</option>
            <option value="6">+6 (0110)</option>
            <option value="5">+5 (0101)</option>
            <option value="4">+4 (0100)</option>
            <option value="3">+3 (0011)</option>
            <option value="2">+2 (0010)</option>
            <option value="1">+1 (0001)</option>
            <option value="0" selected>0 (0000)</option>
            <option value="-1">-1 (1111)</option>
            <option value="-2">-2 (1110)</option>
            <option value="-3">-3 (1101)</option>
            <option value="-4">-4 (1100)</option>
            <option value="-5">-5 (1011)</option>
            <option value="-6">-6 (1010)</option>
            <option value="-7">-7 (1001)</option>
            <option value="-8">-8 (1000)</option>
        </select>
    </div>

    <button onclick="enviarCalculo()">Calcular no ESP32</button>

    <div class="result-box">
        <strong>Resultado Decimal:</strong> <span id="resDec">-</span><br>
        <strong>Resultado Binário (4b):</strong> <span id="resBin">0000</span>
    </div>

    <div id="overflowAlert" class="overflow-badge">OVERFLOW DETECTADO!</div>
</div>

<script>
function enviarCalculo() {
    let a = document.getElementById("paramA").value;
    let b = document.getElementById("paramB").value;
    let op = document.getElementById("operacao").value;
    
    let url = `/calcular?a=${a}&b=${b}&op=${op}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById("resDec").innerText = data.resultadoDecimal;
            document.getElementById("resBin").innerText = data.resultadoBinario;
            
            if(data.overflow) {
                document.getElementById("overflowAlert").style.display = "block";
            } else {
                document.getElementById("overflowAlert").style.display = "none";
            }
        })
        .catch(err => console.error("Erro na requisição:", err));
}
</script>
</body>
</html>
)=====";

#endif
