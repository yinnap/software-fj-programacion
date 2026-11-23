# excepciones.py
# Define excepciones personalizadas para Software FJ heredando de Exception.
# Permite identificar errores de validación, disponibilidad, cálculo y reservas
# sin interrumpir la ejecución del sistema.


class ErrorSistemaSoftwareFJ(Exception):
    """Excepción base del sistema Software FJ con código de error."""

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL") -> None:
        # Almacena el código de error para trazabilidad y registro en logs.
        self.codigo = codigo
        # Invoca el constructor de Exception con mensaje formateado.
        super().__init__(f"[{codigo}] {mensaje}")


class ErrorValidacionCliente(ErrorSistemaSoftwareFJ):
    """Error lanzado cuando un dato del cliente es inválido o vacío."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="ERR_CLIENTE")


class ErrorValidacionServicio(ErrorSistemaSoftwareFJ):
    """Error lanzado cuando los parámetros de un servicio no son válidos."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="ERR_SERVICIO_DATOS")


class ErrorServicioNoDisponible(ErrorSistemaSoftwareFJ):
    """Error lanzado al intentar reservar o usar un servicio no disponible."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="ERR_SERVICIO_DISP")


class ErrorCalculoCosto(ErrorSistemaSoftwareFJ):
    """Error lanzado ante cálculos inconsistentes, tarifas inválidas o divisiones erróneas."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="ERR_CALCULO")


class ErrorReservaInvalida(ErrorSistemaSoftwareFJ):
    """Error lanzado cuando una reserva tiene datos o transiciones de estado inválidas."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="ERR_RESERVA")
