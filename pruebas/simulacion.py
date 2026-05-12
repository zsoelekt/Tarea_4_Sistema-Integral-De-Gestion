from modelos.cliente import Cliente
from modelos.reserva import Reserva
from modelos.servicios_especializados import *
from utilidades.logger import registrar_log

def ejecutar_simulacion():

    operaciones = [

        ("Juan", "juan@gmail.com", ReservaSala("Sala VIP", 50), 2),

        ("Pedro", "correo_malo", ReservaSala("Sala VIP", 50), 2),

        ("Ana", "ana@gmail.com", AlquilerEquipo("Computador", 30), 3),

        ("Luis", "luis@gmail.com", AsesoriaEspecializada("Python", 100), 1),

        ("Mario", "mario@gmail", ReservaSala("Sala", 40), 2),

        ("Jorge", "jorge@gmail.com", AlquilerEquipo("VideoBeam", 20), -1),

        ("Carlos", "carlos@gmail.com", ReservaSala("Premium", 80), 5),

        ("Diana", "diana@gmail.com", AsesoriaEspecializada("IA", 120), 2),

        ("Jose", "josegmail.com", ReservaSala("VIP", 60), 1),

        ("Sara", "sara@gmail.com", AlquilerEquipo("Tablet", 25), 4)

    ]

    for nombre, correo, servicio, horas in operaciones:

        try:

            cliente = Cliente(nombre, correo)

            reserva = Reserva(cliente, servicio, horas)

            costo = reserva.procesar()

            mensaje = f"Reserva exitosa de {nombre} - Total: ${costo}"

            print(mensaje)

            registrar_log(mensaje)

        except Exception as e:

            error = f"Error con {nombre}: {e}"

            print(error)

            registrar_log(error)

        finally:

            registrar_log("Operación finalizada")
