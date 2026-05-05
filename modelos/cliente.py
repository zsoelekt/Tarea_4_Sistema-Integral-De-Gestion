from modelos.entidad import Entidad

class Cliente(Entidad):
    def __init__(self, nombre, correo):
        self.__nombre = nombre
        self.__correo = correo
        self.validar()

    def validar(self):
        if "@" not in self.__correo:
            raise ValueError("Correo inválido")

    def mostrar_info(self):
        return f"Cliente: {self.__nombre} - {self.__correo}"

    @property
    def nombre(self):
        return self.__nombre
