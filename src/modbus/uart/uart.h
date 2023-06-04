#ifndef UART_H_
#define UART_H_

struct UART_RESPONSE
{
    void *data;
    unsigned int status;
};

void init_uart(double Kp_, double Ki_, double Kd_);
void pid_atualiza_referencia(float referencia_);
double pid_controle(double saida_medida);

#endif /* UART_H_ */