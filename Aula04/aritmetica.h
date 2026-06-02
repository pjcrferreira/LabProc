#ifndef ARITMETICA_H
#define ARITMETICA_H

#include <Arduino.h>

int16_t executarSoma(int16_t a, int16_t b, bool &overflow);
int16_t executarSubtracao(int16_t a, int16_t b, bool &overflow);
int32_t executarMultiplicacao(int16_t a, int16_t b);
uint32_t executarFatorial(int16_t a, bool &overflow);
int16_t executarDivisao(int16_t a, int16_t b, bool &divByZero);

#endif
