#ifndef INDEX_H
#define INDEX_H

const char MAIN_page[] PROGMEM = R"=====(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora Iterativa RISC-V</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            text-align: center;
            padding: 20px;
        }

        .container {
            max-width: 500px;
            background: #1e293b;
            margin: 0 auto;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            border: 1px solid #334155;
        }

        h2 {
            color: #38bdf8;
            margin-bottom: 25px;
            font-size: 24px;
        }

        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }

        label {
            font-weight: bold;
            display: block;
            margin-bottom: 8px;
            color: #94a3b8;
        }

        select,
button {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    border-radius: 8px;
    background: #334155;
    border: 1px solid #475569;
    color: white;
    box-sizing: border-box;
}

select:focus {
    border-color: #38bdf8;
    outline: none;
}

button {
    background-color: #0284c7;
    font-weight: bold;
    cursor: pointer;
    margin-top: 15px;
    border: none;
    transition: background 0.2s;
}

button:hover {
    background-color: #0369a1;
}

.result-box {
    margin-top: 25px;
    padding: 20px;
    border-radius: 10px;
    background-color: #0f172a;
    border: 1px solid #334155;
    text-align: left;
}

.result-line {
    margin-bottom: 8px;
    font-size: 16px;
}

.highlight {
    color: #38bdf8;
    font-weight: bold;
}

.alert-badge {
    display: none;
    margin-top: 15px;
    padding: 12px;
    background-color: #ef4444;
    color: white;
    font-weight: bold;
    border-radius: 8px;
}
</style>
</head>

<body>

<div class="container">

<h2>Calculadora Co-Processada ESP32-C3</h2>

<div class="form-group">
<label for="paramA">Operando A:</label>
<select id="paramA"></select>
</div>

<div class="form-group">
<label for="operacao">Operação Co-Processada:</label>
<select id="operacao" onchange="toggleOperandoB()">
<option value="soma">Soma (+)</option>
<option value="sub">Subtração (-)</option>
<option value="mult">Multiplicação (*)</option>
<option value="fat">Fatorial (!)</option>
<option value="div">Divisão (/) [Desafio]</option>
</select>
</div>

<div class="form-group" id="groupB">
<label for="paramB">Operando B:</label>
<select id="paramB"></select>
</div>

<button onclick="executarCalculo()">
Disparar Execução em C
</button>

<div class="result-box">
<div class="result-line">
Resultado Decimal:
<span id="resDec" class="highlight">-</span>
</div>

<div class="result-line">
Resultado Binário:
<span id="resBin" class="highlight">
0000000000000000
</span>
</div>

<div class="result-line">
Tempo de Execução:
<span id="resTempo" class="highlight">-</span>
&mu;s
</div>
</div>

<div id="statusAlert" class="alert-badge"></div>

</div>

<script>

function gerarOpcoes(selectId)
{
    const select = document.getElementById(selectId);

    for (let i = 20; i >= -20; i--)
    {
        const option = document.createElement("option");

        option.value = i;

        let binario = (i & 0x3F)
        .toString(2)
        .padStart(6, '0');

        option.textContent = i + " (" + binario + ")";

        if (i === 0)
        {
            option.selected = true;
        }

        select.appendChild(option);
    }
}

function toggleOperandoB()
{
    let op = document.getElementById("operacao").value;

    document.getElementById("groupB").style.display =
    (op === "fat") ? "none" : "block";
}

function executarCalculo()
{
    let a = document.getElementById("paramA").value;
    let b = document.getElementById("paramB").value;
    let op = document.getElementById("operacao").value;

    let url =
    "/calcular?a=" +
    encodeURIComponent(a) +
    "&b=" +
    encodeURIComponent(b) +
    "&op=" +
    encodeURIComponent(op);

    fetch(url)
    .then(function(response)
    {
        return response.json();
    })
    .then(function(data)
    {
        document.getElementById("resDec").innerText =
        data.resultadoDecimal;

        document.getElementById("resBin").innerText =
        data.resultadoBinario;

        document.getElementById("resTempo").innerText =
        data.tempoUs;

        let alertBox =
        document.getElementById("statusAlert");

        if (data.divByZero)
        {
            alertBox.innerText =
            "⚠️ ERRO: DIVISÃO POR ZERO!";

        alertBox.style.display = "block";
        }
        else if (data.overflow)
        {
            alertBox.innerText =
            "⚠️ AVISO: OVERFLOW DETECTADO!";

        alertBox.style.display = "block";
        }
        else
        {
            alertBox.style.display = "none";
        }
    })
    .catch(function(error)
    {
        console.error(error);

        let alertBox =
        document.getElementById("statusAlert");

        alertBox.innerText =
        "⚠️ ERRO DE COMUNICAÇÃO COM O ESP32";

        alertBox.style.display = "block";
    });
}

window.onload = function()
{
    gerarOpcoes("paramA");
    gerarOpcoes("paramB");
    toggleOperandoB();
};

</script>

</body>
</html>
)=====";

    #endif
