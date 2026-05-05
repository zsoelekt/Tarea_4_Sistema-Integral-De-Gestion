from modelos.servicio import Servicio

class ReservaSala(Servicio):
    def calcular_costo(self, horas):
        return self.tarifa * horas

    def describir(self):
        return "Reserva de sala empresarial"


class AlquilerEquipo(Servicio):
    def calcular_costo(self, horas):
        return (self.tarifa * horas) + 20

    def describir(self):
        return "Alquiler de equipos tecnológicos"


class Asesoria(Servicio):
    def calcular_costo(self, horas):
        return self.tarifa * horas * 1.2

    def describir(self):
        return "Asesoría especializada"
