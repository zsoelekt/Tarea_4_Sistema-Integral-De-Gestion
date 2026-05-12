from modelos.entidad import Entidad

class Cliente(Entidad):

    def __init__(self, nombre, correo):

        if "@" not in correo:
            raise ValueError("Correo inválido")

        self.__nombre = nombre
        self.__correo = correo

    def mostrar_info(self):
        return f"{self.__nombre} - {self.__correo}"

    def get_nombre(self):
        return self.__nombre
