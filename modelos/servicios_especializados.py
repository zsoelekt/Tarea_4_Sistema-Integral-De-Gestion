from modelos.servicio import Servicio

class ReservaSala(Servicio):

    def calcular_costo(self, horas):
        return self.precio_base * horas


class AlquilerEquipo(Servicio):

    def calcular_costo(self, horas):
        return (self.precio_base * horas) + 20


class AsesoriaEspecializada(Servicio):

    def calcular_costo(self, horas):
        return (self.precio_base * horas) * 1.15
