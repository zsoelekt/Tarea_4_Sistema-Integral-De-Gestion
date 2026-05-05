#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Software FJ - Sistema Integral de Gestión
Gestión de Clientes, Servicios y Reservas
Autor: Tarea 4 - Sistema OOP Avanzado
Fecha: 2026-05-05
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from typing import List, Optional
from decimal import Decimal
import re

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

class LoggerConfigurator:
    """Configurador centralizado de logging para la aplicación"""
    
    @staticmethod
    def setup():
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler('sistema_fj.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('SoftwareFJ')

logger = LoggerConfigurator.setup()

# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class SoftwareFJException(Exception):
    """Excepción base para Software FJ"""
    pass

class ClienteInvalidoException(SoftwareFJException):
    """Excepción cuando los datos del cliente son inválidos"""
    pass

class ServicioInvalidoException(SoftwareFJException):
    """Excepción cuando los datos del servicio son inválidos"""
    pass

class ReservaInvalidaException(SoftwareFJException):
    """Excepción cuando la reserva es inválida"""
    pass

class ServicioNoDisponibleException(SoftwareFJException):
    """Excepción cuando el servicio no está disponible"""
    pass

class ParametroInvalidoException(SoftwareFJException):
    """Excepción por parámetros inválidos"""
    pass

class OperacionNoPermitidaException(SoftwareFJException):
    """Excepción cuando se intenta una operación no permitida"""
    pass

# ============================================================================
# ENUMERACIONES
# ============================================================================

class EstadoReserva(Enum):
    """Estados posibles de una reserva"""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class TipoServicio(Enum):
    """Tipos de servicios disponibles"""
    SALA = "reserva_sala"
    EQUIPO = "alquiler_equipo"
    ASESORIA = "asesoria_especializada"

# ============================================================================
# CLASES ABSTRACTAS BASE
# ============================================================================

class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema"""
    
    _id_counter = 0
    
    def __init__(self, nombre: str):
        """Inicializa una entidad base"""
        self.validar_nombre(nombre)
        self._nombre = nombre
        EntidadBase._id_counter += 1
        self._id = EntidadBase._id_counter
        self._fecha_creacion = datetime.now()
    
    @staticmethod
    def validar_nombre(nombre: str) -> None:
        """Valida que el nombre sea válido"""
        if not nombre or not isinstance(nombre, str):
            raise ParametroInvalidoException("El nombre debe ser una cadena no vacía")
        if len(nombre.strip()) < 3:
            raise ParametroInvalidoException("El nombre debe tener al menos 3 caracteres")
    
    @property
    def id(self) -> int:
        """Obtiene el ID de la entidad"""
        return self._id
    
    @property
    def nombre(self) -> str:
        """Obtiene el nombre de la entidad"""
        return self._nombre
    
    @abstractmethod
    def obtener_descripcion(self) -> str:
        """Retorna una descripción de la entidad"""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, nombre={self._nombre})"


class Servicio(EntidadBase):
    """Clase abstracta para todos los servicios"""
    
    def __init__(self, nombre: str, precio_base: Decimal, tipo_servicio: TipoServicio):
        """Inicializa un servicio"""
        super().__init__(nombre)
        self.validar_precio(precio_base)
        self._precio_base = precio_base
        self._tipo_servicio = tipo_servicio
        self._disponible = True
    
    @staticmethod
    def validar_precio(precio: Decimal) -> None:
        """Valida que el precio sea válido"""
        if not isinstance(precio, (int, float, Decimal)):
            raise ParametroInvalidoException("El precio debe ser un número")
        if precio <= 0:
            raise ParametroInvalidoException("El precio debe ser mayor a cero")
    
    @property
    def precio_base(self) -> Decimal:
        """Obtiene el precio base del servicio"""
        return self._precio_base
    
    @property
    def tipo_servicio(self) -> TipoServicio:
        """Obtiene el tipo de servicio"""
        return self._tipo_servicio
    
    @property
    def disponible(self) -> bool:
        """Verifica si el servicio está disponible"""
        return self._disponible
    
    def cambiar_disponibilidad(self, disponible: bool) -> None:
        """Cambia la disponibilidad del servicio"""
        self._disponible = disponible
        logger.info(f"Servicio {self._nombre} - disponibilidad: {disponible}")
    
    @abstractmethod
    def calcular_costo(self, duracion_horas: int) -> Decimal:
        """Calcula el costo del servicio (debe ser implementado por subclases)"""
        pass
    
    @abstractmethod
    def calcular_costo_con_impuesto(self, duracion_horas: int, impuesto_porcentaje: float = 19.0) -> Decimal:
        """Calcula el costo con impuesto (debe ser implementado por subclases)"""
        pass
    
    @abstractmethod
    def calcular_costo_con_descuento(self, duracion_horas: int, descuento_porcentaje: float = 0.0) -> Decimal:
        """Calcula el costo con descuento (debe ser implementado por subclases)"""
        pass
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción del servicio"""
        return f"Servicio: {self._nombre} (${self._precio_base})"

# ============================================================================
# SERVICIOS ESPECIALIZADOS (POLIMORFISMO Y HERENCIA)
# ============================================================================

class ReservaSala(Servicio):
    """Servicio especializado: Reserva de Salas"""
    
    def __init__(self, nombre: str, precio_base: Decimal, capacidad: int):
        """Inicializa una sala"""
        super().__init__(nombre, precio_base, TipoServicio.SALA)
        self.validar_capacidad(capacidad)
        self._capacidad = capacidad
    
    @staticmethod
    def validar_capacidad(capacidad: int) -> None:
        """Valida la capacidad de la sala"""
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ParametroInvalidoException("La capacidad debe ser un entero positivo")
    
    def calcular_costo(self, duracion_horas: int) -> Decimal:
        """Calcula costo básico: precio_base * horas"""
        if duracion_horas <= 0:
            raise ParametroInvalidoException("Las horas deben ser positivas")
        return self._precio_base * duracion_horas
    
    def calcular_costo_con_impuesto(self, duracion_horas: int, impuesto_porcentaje: float = 19.0) -> Decimal:
        """Calcula costo con IVA"""
        costo_base = self.calcular_costo(duracion_horas)
        impuesto = costo_base * Decimal(impuesto_porcentaje) / Decimal(100)
        return costo_base + impuesto
    
    def calcular_costo_con_descuento(self, duracion_horas: int, descuento_porcentaje: float = 0.0) -> Decimal:
        """Calcula costo con descuento"""
        costo_base = self.calcular_costo(duracion_horas)
        descuento = costo_base * Decimal(descuento_porcentaje) / Decimal(100)
        return costo_base - descuento
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción detallada de la sala"""
        return f"Sala '{self._nombre}' - Capacidad: {self._capacidad} personas - ${self._precio_base}/hora"


class AlquilerEquipo(Servicio):
    """Servicio especializado: Alquiler de Equipos"""
    
    def __init__(self, nombre: str, precio_base: Decimal, cantidad_disponible: int):
        """Inicializa un equipo para alquiler"""
        super().__init__(nombre, precio_base, TipoServicio.EQUIPO)
        self.validar_cantidad(cantidad_disponible)
        self._cantidad_disponible = cantidad_disponible
        self._cantidad_alquilada = 0
    
    @staticmethod
    def validar_cantidad(cantidad: int) -> None:
        """Valida la cantidad disponible"""
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ParametroInvalidoException("La cantidad debe ser un entero positivo")
    
    def reservar_cantidad(self, cantidad: int) -> None:
        """Reserva una cantidad de equipos"""
        if cantidad > self._cantidad_disponible - self._cantidad_alquilada:
            raise ServicioNoDisponibleException(
                f"Solo hay {self._cantidad_disponible - self._cantidad_alquilada} equipos disponibles"
            )
        self._cantidad_alquilada += cantidad
    
    def liberar_cantidad(self, cantidad: int) -> None:
        """Libera equipos alquilados"""
        self._cantidad_alquilada = max(0, self._cantidad_alquilada - cantidad)
    
    def calcular_costo(self, duracion_horas: int) -> Decimal:
        """Calcula costo: precio_base * horas"""
        if duracion_horas <= 0:
            raise ParametroInvalidoException("Las horas deben ser positivas")
        return self._precio_base * duracion_horas
    
    def calcular_costo_con_impuesto(self, duracion_horas: int, impuesto_porcentaje: float = 19.0) -> Decimal:
        """Calcula costo con IVA"""
        costo_base = self.calcular_costo(duracion_horas)
        impuesto = costo_base * Decimal(impuesto_porcentaje) / Decimal(100)
        return costo_base + impuesto
    
    def calcular_costo_con_descuento(self, duracion_horas: int, descuento_porcentaje: float = 0.0) -> Decimal:
        """Calcula costo con descuento"""
        costo_base = self.calcular_costo(duracion_horas)
        descuento = costo_base * Decimal(descuento_porcentaje) / Decimal(100)
        return costo_base - descuento
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción del equipo"""
        return f"Equipo '{self._nombre}' - Disponibles: {self._cantidad_disponible - self._cantidad_alquilada}/{self._cantidad_disponible} - ${self._precio_base}/hora"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: Asesorías Especializadas"""
    
    def __init__(self, nombre: str, precio_base: Decimal, especialidad: str, experiencia_anos: int):
        """Inicializa una asesoría"""
        super().__init__(nombre, precio_base, TipoServicio.ASESORIA)
        self.validar_especialidad(especialidad)
        self._especialidad = especialidad
        self._experiencia_anos = max(0, experiencia_anos)
    
    @staticmethod
    def validar_especialidad(especialidad: str) -> None:
        """Valida la especialidad"""
        if not especialidad or len(especialidad.strip()) < 3:
            raise ParametroInvalidoException("La especialidad debe tener al menos 3 caracteres")
    
    def calcular_costo(self, duracion_horas: int) -> Decimal:
        """Calcula costo: precio_base * horas con bono por experiencia"""
        if duracion_horas <= 0:
            raise ParametroInvalidoException("Las horas deben ser positivas")
        
        bono_experiencia = Decimal(self._experiencia_anos * 5) / Decimal(100)  # 5% por cada año
        multiplicador = Decimal(1) + bono_experiencia
        return self._precio_base * duracion_horas * multiplicador
    
    def calcular_costo_con_impuesto(self, duracion_horas: int, impuesto_porcentaje: float = 19.0) -> Decimal:
        """Calcula costo con IVA"""
        costo_base = self.calcular_costo(duracion_horas)
        impuesto = costo_base * Decimal(impuesto_porcentaje) / Decimal(100)
        return costo_base + impuesto
    
    def calcular_costo_con_descuento(self, duracion_horas: int, descuento_porcentaje: float = 0.0) -> Decimal:
        """Calcula costo con descuento"""
        costo_base = self.calcular_costo(duracion_horas)
        descuento = costo_base * Decimal(descuento_porcentaje) / Decimal(100)
        return costo_base - descuento
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la asesoría"""
        return f"Asesoría '{self._nombre}' - Especialidad: {self._especialidad} - Experiencia: {self._experiencia_anos} años - ${self._precio_base}/hora"

# ============================================================================
# CLASE CLIENTE
# ============================================================================

class Cliente(EntidadBase):
    """Clase Cliente con validaciones robustas y encapsulación"""
    
    def __init__(self, nombre: str, email: str, telefono: str):
        """Inicializa un cliente"""
        super().__init__(nombre)
        self.validar_email(email)
        self.validar_telefono(telefono)
        self._email = email
        self._telefono = telefono
        self._reservas: List['Reserva'] = []
        self._activo = True
    
    @staticmethod
    def validar_email(email: str) -> None:
        """Valida el formato del email"""
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, email):
            raise ClienteInvalidoException(f"Email inválido: {email}")
    
    @staticmethod
    def validar_telefono(telefono: str) -> None:
        """Valida el formato del teléfono"""
        telefono_limpio = ''.join(c for c in telefono if c.isdigit())
        if len(telefono_limpio) < 7:
            raise ClienteInvalidoException(f"Teléfono inválido: {telefono}")
    
    @property
    def email(self) -> str:
        """Obtiene el email del cliente"""
        return self._email
    
    @property
    def telefono(self) -> str:
        """Obtiene el teléfono del cliente"""
        return self._telefono
    
    @property
    def activo(self) -> bool:
        """Verifica si el cliente está activo"""
        return self._activo
    
    def agregar_reserva(self, reserva: 'Reserva') -> None:
        """Agrega una reserva al cliente"""
        self._reservas.append(reserva)
    
    def obtener_reservas(self) -> List['Reserva']:
        """Obtiene todas las reservas del cliente"""
        return self._reservas.copy()
    
    def desactivar(self) -> None:
        """Desactiva el cliente"""
        self._activo = False
        logger.info(f"Cliente {self._nombre} desactivado")
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción del cliente"""
        return f"Cliente: {self._nombre} - Email: {self._email} - Teléfono: {self._telefono} - Activo: {self._activo}"
    
    def __str__(self) -> str:
        return f"Cliente(id={self._id}, nombre={self._nombre}, email={self._email})"

# ============================================================================
# CLASE RESERVA
# ============================================================================

class Reserva(EntidadBase):
    """Clase Reserva con manejo avanzado de excepciones"""
    
    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_horas: int, fecha_inicio: datetime):
        """Inicializa una reserva"""
        try:
            super().__init__(f"Reserva-{cliente.nombre}-{servicio.nombre}")
            self.validar_duracion(duracion_horas)
            
            if not isinstance(cliente, Cliente):
                raise ClienteInvalidoException("El cliente debe ser una instancia de Cliente")
            if not isinstance(servicio, Servicio):
                raise ServicioInvalidoException("El servicio debe ser una instancia de Servicio")
            if not servicio.disponible:
                raise ServicioNoDisponibleException(f"El servicio {servicio.nombre} no está disponible")
            if not cliente.activo:
                raise ClienteInvalidoException(f"El cliente {cliente.nombre} está desactivado")
            
            self._cliente = cliente
            self._servicio = servicio
            self._duracion_horas = duracion_horas
            self._fecha_inicio = fecha_inicio
            self._fecha_fin = fecha_inicio + timedelta(hours=duracion_horas)
            self._estado = EstadoReserva.PENDIENTE
            self._costo_total = Decimal(0)
            self._confirmada = False
            
            logger.info(f"Reserva creada: {self}")
        except SoftwareFJException as e:
            logger.error(f"Error al crear reserva: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear reserva: {str(e)}")
            raise SoftwareFJException(f"Error inesperado: {str(e)}") from e
    
    @staticmethod
    def validar_duracion(duracion: int) -> None:
        """Valida la duración de la reserva"""
        if not isinstance(duracion, int) or duracion <= 0:
            raise ParametroInvalidoException("La duración debe ser un entero positivo (horas)")
        if duracion > 24:
            raise ParametroInvalidoException("La duración no puede exceder 24 horas")
    
    @property
    def cliente(self) -> Cliente:
        """Obtiene el cliente de la reserva"""
        return self._cliente
    
    @property
    def servicio(self) -> Servicio:
        """Obtiene el servicio de la reserva"""
        return self._servicio
    
    @property
    def estado(self) -> EstadoReserva:
        """Obtiene el estado de la reserva"""
        return self._estado
    
    @property
    def costo_total(self) -> Decimal:
        """Obtiene el costo total de la reserva"""
        return self._costo_total
    
    def confirmar_reserva(self, aplicar_impuesto: bool = True) -> None:
        """Confirma la reserva y calcula el costo final"""
        try:
            if self._confirmada:
                raise OperacionNoPermitidaException("La reserva ya está confirmada")
            if self._estado == EstadoReserva.CANCELADA:
                raise OperacionNoPermitidaException("No se puede confirmar una reserva cancelada")
            
            if aplicar_impuesto:
                self._costo_total = self._servicio.calcular_costo_con_impuesto(self._duracion_horas)
            else:
                self._costo_total = self._servicio.calcular_costo(self._duracion_horas)
            
            self._estado = EstadoReserva.CONFIRMADA
            self._confirmada = True
            
            logger.info(f"Reserva confirmada: {self} - Costo: ${self._costo_total}")
        except SoftwareFJException as e:
            logger.error(f"Error al confirmar reserva: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al confirmar: {str(e)}")
            raise SoftwareFJException(f"Error inesperado: {str(e)}") from e
    
    def cancelar_reserva(self, razon: str = "") -> None:
        """Cancela la reserva"""
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise OperacionNoPermitidaException("La reserva ya está cancelada")
            if self._estado in [EstadoReserva.COMPLETADA, EstadoReserva.EN_PROCESO]:
                raise OperacionNoPermitidaException(f"No se puede cancelar una reserva {self._estado.value}")
            
            self._estado = EstadoReserva.CANCELADA
            logger.info(f"Reserva cancelada: {self} - Razón: {razon}")
        except SoftwareFJException as e:
            logger.error(f"Error al cancelar reserva: {str(e)}")
            raise
    
    def procesar_reserva(self) -> None:
        """Procesa la reserva (la pone en curso)"""
        try:
            if not self._confirmada:
                raise OperacionNoPermitidaException("La reserva debe estar confirmada antes de procesarla")
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaException(f"No se puede procesar una reserva en estado {self._estado.value}")
            
            self._estado = EstadoReserva.EN_PROCESO
            logger.info(f"Reserva procesada: {self}")
        except SoftwareFJException as e:
            logger.error(f"Error al procesar reserva: {str(e)}")
            raise
    
    def completar_reserva(self) -> None:
        """Marca la reserva como completada"""
        try:
            if self._estado != EstadoReserva.EN_PROCESO:
                raise OperacionNoPermitidaException(f"No se puede completar una reserva en estado {self._estado.value}")
            
            self._estado = EstadoReserva.COMPLETADA
            logger.info(f"Reserva completada: {self}")
        except SoftwareFJException as e:
            logger.error(f"Error al completar reserva: {str(e)}")
            raise
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción detallada de la reserva"""
        return (f"Reserva #{self._id} | Cliente: {self._cliente.nombre} | "
                f"Servicio: {self._servicio.nombre} | Duración: {self._duracion_horas}h | "
                f"Estado: {self._estado.value} | Costo: ${self._costo_total}")
    
    def __str__(self) -> str:
        return f"Reserva(id={self._id}, cliente={self._cliente.nombre}, servicio={self._servicio.nombre}, estado={self._estado.value})"

# ============================================================================
# SISTEMA DE GESTIÓN
# ============================================================================

class SistemaGestionSoftwareFJ:
    """Sistema integral de gestión para Software FJ"""
    
    def __init__(self):
        """Inicializa el sistema de gestión"""
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        logger.info("Sistema de Gestión Software FJ inicializado")
    
    # ========== GESTIÓN DE CLIENTES ==========
    
    def registrar_cliente(self, nombre: str, email: str, telefono: str) -> Cliente:
        """Registra un nuevo cliente"""
        try:
            cliente = Cliente(nombre, email, telefono)
            self._clientes.append(cliente)
            logger.info(f"Cliente registrado: {cliente}")
            return cliente
        except ClienteInvalidoException as e:
            logger.error(f"Error al registrar cliente: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al registrar cliente: {str(e)}")
            raise SoftwareFJException(f"Error inesperado: {str(e)}") from e
    
    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Cliente]:
        """Obtiene un cliente por ID"""
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente
        return None
    
    def listar_clientes(self) -> List[Cliente]:
        """Lista todos los clientes activos"""
        return [c for c in self._clientes if c.activo]
    
    # ========== GESTIÓN DE SERVICIOS ==========
    
    def crear_sala(self, nombre: str, precio_base: float, capacidad: int) -> ReservaSala:
        """Crea un nuevo servicio de sala"""
        try:
            precio = Decimal(str(precio_base))
            sala = ReservaSala(nombre, precio, capacidad)
            self._servicios.append(sala)
            logger.info(f"Sala creada: {sala.obtener_descripcion()}")
            return sala
        except (ServicioInvalidoException, ParametroInvalidoException) as e:
            logger.error(f"Error al crear sala: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear sala: {str(e)}")
            raise ServicioInvalidoException(f"Error inesperado: {str(e)}") from e
    
    def crear_equipo(self, nombre: str, precio_base: float, cantidad_disponible: int) -> AlquilerEquipo:
        """Crea un nuevo servicio de alquiler de equipos"""
        try:
            precio = Decimal(str(precio_base))
            equipo = AlquilerEquipo(nombre, precio, cantidad_disponible)
            self._servicios.append(equipo)
            logger.info(f"Equipo creado: {equipo.obtener_descripcion()}")
            return equipo
        except (ServicioInvalidoException, ParametroInvalidoException) as e:
            logger.error(f"Error al crear equipo: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear equipo: {str(e)}")
            raise ServicioInvalidoException(f"Error inesperado: {str(e)}") from e
    
    def crear_asesoria(self, nombre: str, precio_base: float, especialidad: str, experiencia_anos: int) -> AsesoriaEspecializada:
        """Crea un nuevo servicio de asesoría especializada"""
        try:
            precio = Decimal(str(precio_base))
            asesoria = AsesoriaEspecializada(nombre, precio, especialidad, experiencia_anos)
            self._servicios.append(asesoria)
            logger.info(f"Asesoría creada: {asesoria.obtener_descripcion()}")
            return asesoria
        except (ServicioInvalidoException, ParametroInvalidoException) as e:
            logger.error(f"Error al crear asesoría: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear asesoría: {str(e)}")
            raise ServicioInvalidoException(f"Error inesperado: {str(e)}") from e
    
    def obtener_servicio_por_id(self, servicio_id: int) -> Optional[Servicio]:
        """Obtiene un servicio por ID"""
        for servicio in self._servicios:
            if servicio.id == servicio_id:
                return servicio
        return None
    
    def listar_servicios_disponibles(self) -> List[Servicio]:
        """Lista todos los servicios disponibles"""
        return [s for s in self._servicios if s.disponible]
    
    # ========== GESTIÓN DE RESERVAS ==========
    
    def crear_reserva(self, cliente: Cliente, servicio: Servicio, duracion_horas: int, 
                     fecha_inicio: Optional[datetime] = None) -> Reserva:
        """Crea una nueva reserva"""
        try:
            if fecha_inicio is None:
                fecha_inicio = datetime.now()
            
            reserva = Reserva(cliente, servicio, duracion_horas, fecha_inicio)
            self._reservas.append(reserva)
            cliente.agregar_reserva(reserva)
            logger.info(f"Reserva creada: {reserva}")
            return reserva
        except ReservaInvalidaException as e:
            logger.error(f"Error al crear reserva: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear reserva: {str(e)}")
            raise ReservaInvalidaException(f"Error inesperado: {str(e)}") from e
    
    def obtener_reserva_por_id(self, reserva_id: int) -> Optional[Reserva]:
        """Obtiene una reserva por ID"""
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        return None
    
    def listar_reservas_del_cliente(self, cliente_id: int) -> List[Reserva]:
        """Lista todas las reservas de un cliente"""
        cliente = self.obtener_cliente_por_id(cliente_id)
        if cliente:
            return cliente.obtener_reservas()
        return []
    
    def listar_todas_reservas(self) -> List[Reserva]:
        """Lista todas las reservas del sistema"""
        return self._reservas.copy()
    
    # ========== OPERACIONES COMPLEJAS ==========
    
    def obtener_reporte_general(self) -> str:
        """Genera un reporte general del sistema"""
        reporte = []
        reporte.append("="*60)
        reporte.append("REPORTE GENERAL - SOFTWARE FJ")
        reporte.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        reporte.append("="*60)
        
        reporte.append(f"\nTotal de Clientes: {len(self._clientes)}")
        reporte.append(f"Clientes Activos: {len([c for c in self._clientes if c.activo])}")
        
        reporte.append(f"\nTotal de Servicios: {len(self._servicios)}")
        reporte.append(f"Servicios Disponibles: {len([s for s in self._servicios if s.disponible])}")
        
        reporte.append(f"\nTotal de Reservas: {len(self._reservas)}")
        for estado in EstadoReserva:
            count = len([r for r in self._reservas if r.estado == estado])
            reporte.append(f"  - {estado.value}: {count}")
        
        total_ingresos = sum(r.costo_total for r in self._reservas if r.estado == EstadoReserva.COMPLETADA)
        reporte.append(f"\nIngresos Totales (Reservas Completadas): ${total_ingresos}")
        
        reporte.append("\n" + "="*60)
        return "\n".join(reporte)

# ============================================================================
# FUNCIÓN PRINCIPAL - DEMOSTRACIÓN DEL SISTEMA
# ============================================================================

def demostrar_sistema():
    """Demuestra el funcionamiento completo del sistema con 10+ operaciones"""
    
    logger.info("\n" + "="*70)
    logger.info("INICIANDO DEMOSTRACIÓN DEL SISTEMA SOFTWARE FJ")
    logger.info("="*70)
    
    sistema = SistemaGestionSoftwareFJ()
    
    # ========== OPERACIÓN 1: Registro válido de clientes ==========
    logger.info("\n[OPERACIÓN 1] Registro de clientes válidos...")
    try:
        cliente1 = sistema.registrar_cliente("Juan Pérez", "juan.perez@email.com", "+57 312 345 6789")
        cliente2 = sistema.registrar_cliente("María García", "maria.garcia@email.com", "+57 301 234 5678")
        cliente3 = sistema.registrar_cliente("Carlos López", "carlos.lopez@email.com", "+57 315 987 6543")
        logger.info("✓ 3 clientes registrados exitosamente")
    except Exception as e:
        logger.error(f"✗ Error en registro de clientes: {str(e)}")
    
    # ========== OPERACIÓN 2: Intento de registro inválido de cliente ==========
    logger.info("\n[OPERACIÓN 2] Intento de registro de cliente con datos inválidos...")
    try:
        cliente_invalido = sistema.registrar_cliente("XX", "email_invalido", "123")  # Datos inválidos
        logger.info("✗ Se permitió crear cliente con datos inválidos (ERROR)")
    except ClienteInvalidoException as e:
        logger.info(f"✓ Excepción capturada correctamente: {str(e)}")
    except Exception as e:
        logger.error(f"✗ Error inesperado: {str(e)}")
    
    # ========== OPERACIÓN 3: Creación correcta de servicios ==========
    logger.info("\n[OPERACIÓN 3] Creación de servicios correctos...")
    try:
        sala_conferencias = sistema.crear_sala("Sala Conferencias A", 50.00, 20)
        sala_reunion = sistema.crear_sala("Sala Reuniones B", 30.00, 8)
        proyector = sistema.crear_equipo("Proyector 4K", 25.00, 5)
        asesoria_tech = sistema.crear_asesoria("Asesoría Tecnológica", 100.00, "Sistemas", 8)
        asesoria_legal = sistema.crear_asesoria("Asesoría Legal", 150.00, "Derecho Corporativo", 12)
        logger.info("✓ 5 servicios creados exitosamente")
    except Exception as e:
        logger.error(f"✗ Error en creación de servicios: {str(e)}")
    
    # ========== OPERACIÓN 4: Intento de creación de servicio inválido ==========
    logger.info("\n[OPERACIÓN 4] Intento de creación de servicio con precio inválido...")
    try:
        sala_invalida = sistema.crear_sala("Sala Inválida", -50.00, 10)  # Precio negativo
        logger.info("✗ Se permitió crear servicio con precio negativo (ERROR)")
    except ServicioInvalidoException as e:
        logger.info(f"✓ Excepción capturada correctamente: {str(e)}")
    except Exception as e:
        logger.error(f"✗ Error inesperado: {str(e)}")
    
    # ========== OPERACIÓN 5: Creación exitosa de reserva ==========
    logger.info("\n[OPERACIÓN 5] Creación exitosa de reserva...")
    try:
        reserva1 = sistema.crear_reserva(cliente1, sala_conferencias, 3)
        reserva1.confirmar_reserva(aplicar_impuesto=True)
        logger.info(f"✓ Reserva confirmada: {reserva1.obtener_descripcion()}")
    except Exception as e:
        logger.error(f"✗ Error al crear/confirmar reserva: {str(e)}")
    
    # ========== OPERACIÓN 6: Intento de reserva con cliente inactivo ==========
    logger.info("\n[OPERACIÓN 6] Intento de reserva con cliente desactivado...")
    try:
        cliente1.desactivar()
        reserva_fallida = sistema.crear_reserva(cliente1, sala_reunion, 2)
        logger.info("✗ Se permitió crear reserva con cliente inactivo (ERROR)")
    except ClienteInvalidoException as e:
        logger.info(f"✓ Excepción capturada correctamente: {str(e)}")
    except Exception as e:
        logger.error(f"✗ Error inesperado: {str(e)}")
    
    # Reactivar cliente para siguientes operaciones
    cliente1._activo = True
    
    # ========== OPERACIÓN 7: Reserva con intento de parámetro inválido ==========
    logger.info("\n[OPERACIÓN 7] Intento de reserva con duración inválida...")
    try:
        reserva_invalida = sistema.crear_reserva(cliente2, proyector, 0)  # Duración inválida
        logger.info("✗ Se permitió crear reserva con duración inválida (ERROR)")
    except ReservaInvalidaException as e:
        logger.info(f"✓ Excepción capturada correctamente: {str(e)}")
    except Exception as e:
        logger.error(f"✗ Error inesperado: {str(e)}")
    
    # ========== OPERACIÓN 8: Cálculos de costo con polimorfismo ==========
    logger.info("\n[OPERACIÓN 8] Cálculos de costo con diferentes servicios (polimorfismo)...")
    try:
        duracion_test = 5
        
        # Sala: cálculo simple
        costo_sala = sala_conferencias.calcular_costo(duracion_test)
        costo_sala_impuesto = sala_conferencias.calcular_costo_con_impuesto(duracion_test, 19.0)
        costo_sala_descuento = sala_conferencias.calcular_costo_con_descuento(duracion_test, 10.0)
        
        logger.info(f"Sala Conferencias (5h):")
        logger.info(f"  - Costo base: ${costo_sala}")
        logger.info(f"  - Con IVA 19%: ${costo_sala_impuesto}")
        logger.info(f"  - Con descuento 10%: ${costo_sala_descuento}")
        
        # Asesoría: cálculo con bono por experiencia
        costo_asesoria = asesoria_tech.calcular_costo(duracion_test)
        costo_asesoria_impuesto = asesoria_tech.calcular_costo_con_impuesto(duracion_test, 19.0)
        
        logger.info(f"\nAsesoría Tecnológica (5h, 8 años experiencia):")
        logger.info(f"  - Costo base (con bono): ${costo_asesoria}")
        logger.info(f"  - Con IVA 19%: ${costo_asesoria_impuesto}")
        
        logger.info("✓ Cálculos de costo ejecutados correctamente")
    except Exception as e:
        logger.error(f"✗ Error en cálculo de costos: {str(e)}")
    
    # ========== OPERACIÓN 9: Flujo completo de reserva ==========
    logger.info("\n[OPERACIÓN 9] Flujo completo de reserva (pendiente -> confirmada -> en proceso -> completada)...")
    try:
        reserva2 = sistema.crear_reserva(cliente2, asesoria_legal, 2)
        logger.info(f"1. Creada: {reserva2.obtener_descripcion()}")
        
        reserva2.confirmar_reserva(aplicar_impuesto=True)
        logger.info(f"2. Confirmada: {reserva2.obtener_descripcion()}")
        
        reserva2.procesar_reserva()
        logger.info(f"3. En proceso: {reserva2.obtener_descripcion()}")
        
        reserva2.completar_reserva()
        logger.info(f"4. Completada: {reserva2.obtener_descripcion()}")
        
        logger.info("✓ Flujo de reserva ejecutado correctamente")
    except Exception as e:
        logger.error(f"✗ Error en flujo de reserva: {str(e)}")
    
    # ========== OPERACIÓN 10: Cancelación de reserva ==========
    logger.info("\n[OPERACIÓN 10] Cancelación de reserva...")
    try:
        reserva3 = sistema.crear_reserva(cliente3, sala_reunion, 4)
        logger.info(f"Reserva creada: {reserva3.obtener_descripcion()}")
        
        reserva3.cancelar_reserva("Cliente solicitó cancelación")
        logger.info(f"Reserva cancelada: {reserva3.obtener_descripcion()}")
        
        # Intento de cancelar reserva ya cancelada
        try:
            reserva3.cancelar_reserva("Intento de cancelación duplicada")
        except OperacionNoPermitidaException as e:
            logger.info(f"✓ Intento de cancelación duplicada rechazado: {str(e)}")
        
        logger.info("✓ Operación de cancelación ejecutada correctamente")
    except Exception as e:
        logger.error(f"✗ Error en cancelación de reserva: {str(e)}")
    
    # ========== OPERACIÓN 11+: Operaciones adicionales y reporte final ==========
    logger.info("\n[OPERACIÓN 11] Listados y consultas del sistema...")
    try:
        clientes_activos = sistema.listar_clientes()
        servicios_disponibles = sistema.listar_servicios_disponibles()
        todas_reservas = sistema.listar_todas_reservas()
        
        logger.info(f"Clientes activos: {len(clientes_activos)}")
        logger.info(f"Servicios disponibles: {len(servicios_disponibles)}")
        logger.info(f"Total de reservas: {len(todas_reservas)}")
        logger.info("✓ Consultas ejecutadas correctamente")
    except Exception as e:
        logger.error(f"✗ Error en consultas: {str(e)}")
    
    # ========== REPORTE FINAL ==========
    logger.info("\n" + sistema.obtener_reporte_general())
    
    logger.info("\n" + "="*70)
    logger.info("DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
    logger.info("Revisa el archivo 'sistema_fj.log' para ver todos los eventos registrados")
    logger.info("="*70)

if __name__ == "__main__":
    demostrar_sistema()
