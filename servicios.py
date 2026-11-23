# servicios.py
# Define la clase abstracta Servicio y tres servicios especializados para Software FJ:
# ReservaSala, AlquilerEquipo y AsesoriaEspecializada.
# Implementa herencia, polimorfismo, sobrescritura de métodos, validación estricta
# y cálculo de costos con parámetros opcionales (descuentos, impuestos y recargos).

from abc import abstractmethod  # Permite declarar métodos abstractos que las subclases deben sobrescribir.
from entidades import EntidadSistema  # Clase abstracta base para entidades generales del sistema.
from excepciones import ErrorValidacionServicio, ErrorCalculoCosto  # Excepciones personalizadas.


class Servicio(EntidadSistema):
    """Clase abstracta que representa un servicio general ofrecido por Software FJ."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        # Inicializa el ID desde EntidadSistema y encadena ValueError como ErrorValidacionServicio.
        try:
            super().__init__(id_servicio)
        except ValueError as exc:
            raise ErrorValidacionServicio(f"ID de servicio inválido: {exc}") from exc

        # Valida y asigna nombre, tarifa base y estado de disponibilidad mediante propiedades.
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        """Retorna el nombre del servicio."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        # Verifica que el nombre sea texto y tenga al menos 3 caracteres.
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorValidacionServicio("El nombre del servicio debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base del servicio."""
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        # Evita aceptar valores booleanos como números válidos en Python (True == 1, False == 0).
        if isinstance(valor, bool):
            raise ErrorCalculoCosto(f"Tarifa base inválida (booleano): '{valor}'.")
        # Intenta convertir a float y encadena errores técnicos en ErrorCalculoCosto.
        try:
            monto = float(valor)
        except (TypeError, ValueError) as exc:
            raise ErrorCalculoCosto(f"Tarifa base no numérica: '{valor}'.") from exc
        # Verifica que la tarifa base sea mayor que cero.
        if monto <= 0:
            raise ErrorCalculoCosto("La tarifa base debe ser mayor que cero.")
        self._tarifa_base = monto

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está disponible actualmente."""
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        # Exige un valor booleano estricto para la disponibilidad.
        if not isinstance(estado, bool):
            raise ErrorValidacionServicio("La disponibilidad debe ser un valor booleano (True/False).")
        self._disponible = estado

    @abstractmethod
    def validar_parametros(self, cantidad_o_duracion: int) -> None:
        """Valida los parámetros específicos según el tipo de servicio."""

    @abstractmethod
    def calcular_costo(
        self,
        cantidad_o_duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 19.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo total soportando descuento, impuesto y recargo opcionales."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción específica del tipo de servicio."""

    def _calcular_total_con_ajustes(
        self,
        subtotal: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 19.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Aplica descuento, recargo e impuesto con validación y encadenamiento de errores."""
        # Rechaza booleanos en parámetros numéricos.
        if any(isinstance(x, bool) for x in (subtotal, descuento_pct, impuesto_pct, recargo_adicional)):
            raise ErrorCalculoCosto("Los parámetros de cálculo no pueden ser booleanos.")

        # Convierte a flotante y encadena errores si algún valor no es convertible.
        try:
            sub = float(subtotal)
            desc = float(descuento_pct)
            imp = float(impuesto_pct)
            recargo = float(recargo_adicional)
        except (TypeError, ValueError) as exc:
            raise ErrorCalculoCosto("Parámetros inválidos al calcular costos.") from exc

        # Valida rangos lógicos para evitar cálculos inconsistentes.
        if not (0.0 <= desc < 100.0):
            raise ErrorCalculoCosto("El descuento debe estar entre 0% y menos del 100%.")
        if imp < 0.0 or recargo < 0.0 or sub < 0.0:
            raise ErrorCalculoCosto("Subtotal, impuesto y recargo no pueden ser negativos.")

        # Calcula el total: aplica descuento al subtotal, suma recargos y luego calcula impuesto.
        con_descuento = sub * (1.0 - desc / 100.0)
        base_gravable = con_descuento + recargo
        total = base_gravable * (1.0 + imp / 100.0)
        return round(total, 2)

    def resumen(self) -> str:
        """Sobrescribe resumen() de EntidadSistema integrando descripción, tarifa y estado."""
        estado_txt = "Disponible" if self._disponible else "No disponible"
        return f"{self.describir()} | Tarifa base: ${self._tarifa_base:,.2f} | Estado: {estado_txt}"


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas por horas."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Valida que la capacidad sea un entero positivo (excluyendo booleanos).
        if isinstance(capacidad_personas, bool) or not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise ErrorValidacionServicio("La capacidad de la sala debe ser un número entero mayor que cero.")
        self.capacidad_personas = capacidad_personas

    def validar_parametros(self, cantidad_o_duracion: int) -> None:
        """Valida que la duración en horas esté entre 1 y 24."""
        if isinstance(cantidad_o_duracion, bool) or not isinstance(cantidad_o_duracion, int):
            raise ErrorValidacionServicio("La duración de la sala debe ser un número entero de horas.")
        if not (1 <= cantidad_o_duracion <= 24):
            raise ErrorValidacionServicio("La reserva de sala debe tener una duración entre 1 y 24 horas.")

    def calcular_costo(
        self,
        cantidad_o_duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 19.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo de reserva de sala según horas y ajustes opcionales."""
        self.validar_parametros(cantidad_o_duracion)
        subtotal = self.tarifa_base * cantidad_o_duracion
        return self._calcular_total_con_ajustes(subtotal, descuento_pct, impuesto_pct, recargo_adicional)

    def describir(self) -> str:
        """Describe la sala y su capacidad máxima."""
        return f"Reserva de Sala [{self.id_entidad}] '{self.nombre}' (Capacidad: {self.capacidad_personas} personas)"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos por días."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        unidades_stock: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Valida que las unidades en stock sean un entero no negativo.
        if isinstance(unidades_stock, bool) or not isinstance(unidades_stock, int) or unidades_stock < 0:
            raise ErrorValidacionServicio("Las unidades en stock deben ser un entero mayor o igual a cero.")
        self.unidades_stock = unidades_stock

    def validar_parametros(self, cantidad_o_duracion: int) -> None:
        """Valida duración en días (>= 1) y existencia de unidades disponibles."""
        if isinstance(cantidad_o_duracion, bool) or not isinstance(cantidad_o_duracion, int):
            raise ErrorValidacionServicio("Los días de alquiler deben ser un número entero.")
        if cantidad_o_duracion <= 0:
            raise ErrorValidacionServicio("El alquiler de equipo debe ser de al menos 1 día.")
        if self.unidades_stock <= 0:
            raise ErrorValidacionServicio("No hay unidades disponibles en el inventario de equipos.")

    def calcular_costo(
        self,
        cantidad_o_duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 19.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo del alquiler por días con ajustes opcionales."""
        self.validar_parametros(cantidad_o_duracion)
        subtotal = self.tarifa_base * cantidad_o_duracion
        return self._calcular_total_con_ajustes(subtotal, descuento_pct, impuesto_pct, recargo_adicional)

    def describir(self) -> str:
        """Describe el equipo alquilado y las unidades disponibles."""
        return f"Alquiler de Equipo [{self.id_entidad}] '{self.nombre}' (Unidades: {self.unidades_stock})"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o de software por horas."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Valida que la especialidad sea un texto válido.
        if not isinstance(especialidad, str) or len(especialidad.strip()) < 3:
            raise ErrorValidacionServicio("La especialidad de la asesoría debe tener al menos 3 caracteres.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, cantidad_o_duracion: int) -> None:
        """Valida que la duración de la asesoría esté entre 1 y 100 horas."""
        if isinstance(cantidad_o_duracion, bool) or not isinstance(cantidad_o_duracion, int):
            raise ErrorValidacionServicio("Las horas de asesoría deben ser un número entero.")
        if not (1 <= cantidad_o_duracion <= 100):
            raise ErrorValidacionServicio("La asesoría debe solicitarse entre 1 y 100 horas.")

    def calcular_costo(
        self,
        cantidad_o_duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 19.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo de la asesoría especializada con ajustes opcionales."""
        self.validar_parametros(cantidad_o_duracion)
        subtotal = self.tarifa_base * cantidad_o_duracion
        return self._calcular_total_con_ajustes(subtotal, descuento_pct, impuesto_pct, recargo_adicional)

    def describir(self) -> str:
        """Describe la asesoría y su área de especialidad."""
        return f"Asesoría [{self.id_entidad}] '{self.nombre}' - Especialidad: {self.especialidad}"
