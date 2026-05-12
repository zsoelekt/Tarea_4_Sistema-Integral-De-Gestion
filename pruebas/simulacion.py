from modelos.cliente import Cliente
from modelos.servicios_especializados import ReservaSala
from modelos.reserva import Reserva
from utilidades.logger import registrar_log

def ejecutar_simulacion():
    operaciones = []

    try:
        cliente1 = Cliente("Juan", "juan@gmail.com")
        servicio1 = ReservaSala("Sala Premium", 50)

        reserva1 = Reserva(cliente1, servicio1, 3)
        costo = reserva1.procesar()

        registrar_log(f"Reserva exitosa: {costo}")
        operaciones.append(reserva1)

    except Exception as e:
        registrar_log(str(e))

    try:
        cliente2 = Cliente("Pedro", "correo_invalido")
    except Exception as e:
        registrar_log(f"Error cliente: {e}")
