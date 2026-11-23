# entidades.py
# Define la clase abstracta EntidadSistema (para entidades generales del sistema)
# y la clase Cliente con encapsulación de datos personales y validaciones estrictas.

from abc import ABC, abstractmethod  # Permite crear clases abstractas y métodos abstractos.
import re  # Permite validar el formato del correo electrónico mediante expresión regular.
from excepciones import ErrorValidacionCliente  # Excepción personalizada para datos de cliente.


class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales dentro del sistema Software FJ."""

    def __init__(self, id_entidad: str) -> None:
        # Valida que el identificador sea una cadena de texto no vacía ni compuesta solo por espacios.
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El identificador de la entidad debe ser un texto no vacío.")
        # Almacena el identificador en un atributo protegido para mantener control sobre su acceso.
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        """Devuelve el identificador único de la entidad."""
        return self._id_entidad

    @abstractmethod
    def resumen(self) -> str:
        """Método abstracto que obliga a las clases hijas a definir su propio resumen."""


class Cliente(EntidadSistema):
    """Representa un cliente con encapsulación de datos personales y validaciones."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> None:
        # Intenta inicializar la clase base y encadena ValueError como ErrorValidacionCliente si falla.
        try:
            super().__init__(id_cliente)
        except ValueError as exc:
            raise ErrorValidacionCliente(f"ID de cliente inválido: {exc}") from exc

        # Asigna los atributos mediante sus propiedades para ejecutar las validaciones desde el inicio.
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        """Obtiene el nombre completo del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        # Verifica que el nombre sea texto y tenga al menos 2 caracteres útiles.
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErrorValidacionCliente("El nombre del cliente debe tener al menos 2 caracteres.")
        # Guarda el nombre limpio en el atributo encapsulado _nombre.
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        """Obtiene el correo electrónico del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        # Valida que el correo cumpla con un formato básico de usuario@dominio.extensión.
        if not isinstance(valor, str) or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", valor.strip()):
            raise ErrorValidacionCliente(f"Correo electrónico inválido: '{valor}'.")
        # Guarda el correo normalizado en minúsculas en _correo.
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        """Obtiene el teléfono de contacto del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        # Convierte a cadena, quita espacios y valida que tenga entre 7 y 15 dígitos numéricos.
        limpio = str(valor).strip()
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            raise ErrorValidacionCliente(f"Teléfono inválido: '{valor}'. Debe tener entre 7 y 15 dígitos.")
        # Guarda el teléfono validado en _telefono.
        self._telefono = limpio

    def resumen(self) -> str:
        """Retorna un resumen legible de los datos del cliente."""
        return f"Cliente [{self._id_entidad}] {self._nombre} | Correo: {self._correo} | Tel: {self._telefono}"
