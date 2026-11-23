# reservas.py
# Gestiona reservas, listas internas en memoria (sin base de datos) y registro de logs
# en archivo de texto para el sistema Software FJ.

from datetime import datetime  # Permite agregar fecha y hora a cada entrada del archivo de log.
from pathlib import Path  # Maneja rutas de archivo de forma limpia y multiplataforma.
from entidades import Cliente  # Clase Cliente validada y encapsulada.
from servicios import Servicio  # Clase abstracta Servicio y sus subclases.
from excepciones import (
    ErrorValidacionCliente,
    ErrorValidacionServicio,
    ErrorServicioNoDisponible,
    ErrorReservaInvalida,
)


class RegistradorLogs:
    """Registra eventos y errores en un archivo de log sin usar base de datos."""

    def __init__(self, ruta_log: str = "software_fj.log") -> None:
        # Define la ruta del archivo donde se guardarán los eventos y errores.
        self.ruta_log = Path(ruta_log)

    def registrar(self, nivel: str, mensaje: str, detalle_encadenado: str | None = None) -> None:
        """Escribe una línea con marca de tiempo, nivel, mensaje y causa encadenada si aplica."""
        # Genera marca de tiempo actual para trazabilidad.
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca_tiempo}] [{nivel.upper()}] {mensaje}"
        if detalle_encadenado:
            linea += f" | Causa encadenada: {detalle_encadenado}"

        # Usa try/except/finally para proteger la escritura en disco y mostrar siempre el mensaje.
        try:
            with self.ruta_log.open("a", encoding="utf-8") as archivo:
                archivo.write(linea + "\n")
        except OSError as exc:
            print(f"[AVISO LOG] No se pudo escribir en '{self.ruta_log}': {exc}")
        finally:
            print(linea)


class Reserva:
    """Integra cliente, servicio, duración y estado con confirmación, cancelación y procesamiento."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 19.0,
        recargo_adicional: float = 0.0,
    ) -> None:
        # Valida que el ID de la reserva sea un texto no vacío.
        if not isinstance(id_reserva, str) or not id_reserva.strip():
            raise ErrorReservaInvalida("El ID de la reserva es obligatorio y debe ser texto.")
        # Valida que el parámetro cliente sea una instancia de Cliente.
        if not isinstance(cliente, Cliente):
            raise ErrorReservaInvalida("La reserva requiere un objeto Cliente válido.")
        # Valida que el parámetro servicio sea una instancia de Servicio.
        if not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida("La reserva requiere un objeto Servicio válido.")
        # Verifica que el servicio esté disponible antes de crear la reserva.
        if not servicio.disponible:
            raise ErrorServicioNoDisponible(
                f"El servicio '{servicio.nombre}' (ID: {servicio.id_entidad}) no está disponible."
            )

        # Valida la duración según las reglas específicas del servicio.
        servicio.validar_parametros(duracion)

        # Asigna atributos internos de la reserva.
        self.id_reserva = id_reserva.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.descuento_pct = descuento_pct
        self.impuesto_pct = impuesto_pct
        self.recargo_adicional = recargo_adicional
        self._estado = "PENDIENTE"
        self.costo_total: float | None = None

    @property
    def estado(self) -> str:
        """Retorna el estado actual de la reserva."""
        return self._estado

    def confirmar(self) -> None:
        """Confirma una reserva pendiente si el servicio sigue disponible."""
        if self._estado == "CANCELADA":
            raise ErrorReservaInvalida(f"No se puede confirmar la reserva '{self.id_reserva}' porque está CANCELADA.")
        if self._estado == "PROCESADA":
            raise ErrorReservaInvalida(f"La reserva '{self.id_reserva}' ya fue PROCESADA.")
        if not self.servicio.disponible:
            raise ErrorServicioNoDisponible(f"El servicio '{self.servicio.nombre}' ya no está disponible.")

        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        """Cancela una reserva si no ha sido cancelada ni procesada previamente."""
        if self._estado == "PROCESADA":
            raise ErrorReservaInvalida(f"No se puede cancelar la reserva '{self.id_reserva}' porque ya está PROCESADA.")
        if self._estado == "CANCELADA":
            raise ErrorReservaInvalida(f"La reserva '{self.id_reserva}' ya se encuentra CANCELADA.")

        self._estado = "CANCELADA"

    def procesar(self) -> float:
        """Confirma si está pendiente, calcula el costo total y marca la reserva como PROCESADA."""
        if self._estado == "CANCELADA":
            raise ErrorReservaInvalida(f"No se puede procesar la reserva '{self.id_reserva}' porque está CANCELADA.")
        if self._estado == "PENDIENTE":
            # Confirma automáticamente la reserva pendiente antes de procesar.
            self.confirmar()

        # Calcula el costo aplicando parámetros opcionales configurados en la reserva.
        total = self.servicio.calcular_costo(
            self.duracion,
            descuento_pct=self.descuento_pct,
            impuesto_pct=self.impuesto_pct,
            recargo_adicional=self.recargo_adicional,
        )
        self.costo_total = total
        self._estado = "PROCESADA"
        return total

    def resumen(self) -> str:
        """Devuelve un resumen completo y legible de la reserva."""
        costo_txt = f"${self.costo_total:,.2f}" if self.costo_total is not None else "Pendiente de cálculo"
        return (
            f"Reserva [{self.id_reserva}] | Estado: {self._estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion} | Total: {costo_txt}"
        )


class GestorSoftwareFJ:
    """Administra listas en memoria de clientes, servicios y reservas sin base de datos."""

    def __init__(self, logger: RegistradorLogs | None = None) -> None:
        # Listas internas en memoria (sin uso de base de datos, según el Anexo 3).
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger = logger if logger is not None else RegistradorLogs()

    def registrar_cliente(self, cliente: Cliente) -> None:
        """Agrega un cliente a la lista interna evitando identificadores duplicados."""
        if not isinstance(cliente, Cliente):
            raise ErrorValidacionCliente("Solo se pueden registrar objetos de tipo Cliente.")
        if any(c.id_entidad == cliente.id_entidad for c in self.clientes):
            raise ErrorValidacionCliente(f"Ya existe un cliente registrado con ID '{cliente.id_entidad}'.")
        self.clientes.append(cliente)
        self.logger.registrar("INFO", f"Cliente registrado: {cliente.resumen()}")

    def registrar_servicio(self, servicio: Servicio) -> None:
        """Agrega un servicio a la lista interna evitando identificadores duplicados."""
        if not isinstance(servicio, Servicio):
            raise ErrorValidacionServicio("Solo se pueden registrar objetos de tipo Servicio.")
        if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
            raise ErrorValidacionServicio(f"Ya existe un servicio registrado con ID '{servicio.id_entidad}'.")
        self.servicios.append(servicio)
        self.logger.registrar("INFO", f"Servicio registrado: {servicio.resumen()}")

    def crear_reserva(self, reserva: Reserva) -> None:
        """Agrega una reserva a la lista interna evitando identificadores duplicados."""
        if not isinstance(reserva, Reserva):
            raise ErrorReservaInvalida("Solo se pueden registrar objetos de tipo Reserva.")
        if any(r.id_reserva == reserva.id_reserva for r in self.reservas):
            raise ErrorReservaInvalida(f"Ya existe una reserva con ID '{reserva.id_reserva}'.")
        self.reservas.append(reserva)
        self.logger.registrar("INFO", f"Reserva creada: {reserva.resumen()}")
