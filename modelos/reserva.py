class Reserva:

    def __init__(self, cliente, servicio, horas):

        if horas <= 0:
            raise ValueError("Las horas deben ser mayores a 0")

        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "Pendiente"

    def confirmar(self):
        self.estado = "Confirmada"

    def cancelar(self):
        self.estado = "Cancelada"

    def procesar(self):

        costo = self.servicio.calcular_costo(self.horas)

        self.confirmar()

        return costo
