class PID:
    def __init__(self, Kp_, Ki_, Kd_):
        self.saida_medida = 0.0
        self.sinal_de_controle = 0.0
        self.referencia = 0.0
        self.Kp = Kp_
        self.Ki = Ki_
        self.Kd = Kd_
        self.T = 1
        self.last_time = 0
        self.erro_total = 0.0
        self.erro_anterior = 0.0
        self.sinal_de_controle_MAX = 100
        self.sinal_de_controle_MIN = -100

    def updateReference(self, referencia_):
        self.referencia = referencia_

    def pidControl(self, saida_medida):
        erro = self.referencia - saida_medida

        self.erro_total += erro # Acumula o erro (Termo Integral)

        if self.erro_total >= self.sinal_de_controle_MAX:
            self.erro_total =  self.sinal_de_controle_MAX
        elif self.erro_total <= self.sinal_de_controle_MIN:
            self.erro_total = self.sinal_de_controle_MIN

        delta_error = erro - self.erro_anterior # Diferença entre os erros (Termo Derivativo)

        self.sinal_de_controle = self.Kp * erro + (self.Ki*self.T) * self.erro_total + (self.Kd/self.T) * delta_error # PID calcula sinal de controle

        if self.sinal_de_controle < 0 and self.sinal_de_controle >= -40:
            self.sinal_de_controle = -40

        if self.sinal_de_controle >= self.sinal_de_controle_MAX:
            self.sinal_de_controle = self.sinal_de_controle_MAX
        elif self.sinal_de_controle <= self.sinal_de_controle_MIN:
            self.sinal_de_controle = self.sinal_de_controle_MIN

        self.erro_anterior = erro

        return self.sinal_de_controle

