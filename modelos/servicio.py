from abc import ABC, abstractmethod

class Servicio(ABC):

    def __init__(self, nombre, precio_base):
        self.nombre = nombre
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, horas):
        pass
