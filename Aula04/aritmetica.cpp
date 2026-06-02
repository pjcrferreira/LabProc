#include "aritmetica.h"

int16_t executarSoma(int16_t a, int16_t b, bool &overflow)
{
    int16_t r = a + b;

    overflow =
    ((a > 0 && b > 0 && r < 0) ||
    (a < 0 && b < 0 && r >= 0));

    return r;
}

int16_t executarSubtracao(int16_t a, int16_t b, bool &overflow)
{
    int16_t r = a - b;

    overflow =
    ((a >= 0 && b < 0 && r < 0) ||
    (a < 0 && b >= 0 && r >= 0));

    return r;
}

// Multiplicação por somas sucessivas
int32_t executarMultiplicacao(int16_t a, int16_t b)
{
    int32_t resultado = 0;

    bool negativo = (a < 0) ^ (b < 0);

    uint16_t absA = abs(a);
    uint16_t absB = abs(b);

    for (uint16_t i = 0; i < absB; i++)
    {
        resultado += absA;
    }

    return negativo ? -resultado : resultado;
}

// Fatorial por multiplicações sucessivas
uint32_t executarFatorial(int16_t a, bool &overflow)
{
    if (a < 0)
    {
        overflow = true;
        return 0;
    }

    // 12! cabe em uint32_t
    // 13! já ultrapassa 32 bits
    if (a > 12)
    {
        overflow = true;
        return 0;
    }

    uint32_t resultado = 1;

    for (uint16_t i = 1; i <= a; i++)
    {
        resultado *= i;
    }

    overflow = false;

    return resultado;
}

// Divisão por subtrações sucessivas
int16_t executarDivisao(int16_t a, int16_t b, bool &divByZero)
{
    if (b == 0)
    {
        divByZero = true;
        return 0;
    }

    divByZero = false;

    bool negativo = (a < 0) ^ (b < 0);

    uint16_t absA = abs(a);
    uint16_t absB = abs(b);

    int16_t quociente = 0;

    while (absA >= absB)
    {
        absA -= absB;
        quociente++;
    }

    return negativo ? -quociente : quociente;
}
