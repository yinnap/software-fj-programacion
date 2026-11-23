# main.py
# Punto de entrada principal del sistema de Software FJ.
# Simula 12 operaciones completas (válidas e inválidas) sobre clientes, servicios y reservas,
# evidenciando try/except, try/except/else, try/except/finally, excepciones personalizadas,
# encadenamiento de excepciones y registro en logs sin detener la ejecución.

from entidades import Cliente  # Clase Cliente con encapsulación y validaciones.
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada  # Servicios especializados.
from reservas import Reserva, GestorSoftwareFJ, RegistradorLogs  # Reservas, listas en memoria y log.
from excepciones import (
    ErrorSistemaSoftwareFJ,
    ErrorValidacionCliente,
    ErrorValidacionServicio,
    ErrorServicioNoDisponible,
    ErrorCalculoCosto,
    ErrorReservaInvalida,
)


def ejecutar_simulacion() -> None:
    """Ejecuta 12 operaciones secuenciales demostrando estabilidad y manejo de excepciones."""
    # Crea el registrador de logs y el gestor con listas internas (sin base de datos).
    logger = RegistradorLogs("software_fj.log")
    gestor = GestorSoftwareFJ(logger=logger)

    logger.registrar("INFO", "=== INICIO DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")

    # 1. Registro válido de Cliente 1 usando bloque try / except / else.
    try:
        cliente_1 = Cliente("CLI-001", "Laura Gómez", "laura.gomez@correo.com", "3104567890")
    except ErrorValidacionCliente as err:
        logger.registrar("ERROR", f"Operación 1 fallida: {err}")
    else:
        gestor.registrar_cliente(cliente_1)

    # 2. Registro válido de Cliente 2 usando bloque try / except / else.
    try:
        cliente_2 = Cliente("CLI-002", "Carlos Méndez", "carlos.mendez@empresa.co", "3209876543")
    except ErrorValidacionCliente as err:
        logger.registrar("ERROR", f"Operación 2 fallida: {err}")
    else:
        gestor.registrar_cliente(cliente_2)

    # 3. Registro inválido de Cliente por correo electrónico mal formado.
    try:
        cliente_invalido = Cliente("CLI-003", "Ana Ruiz", "correo-sin-arroba", "3001112233")
        gestor.registrar_cliente(cliente_invalido)
    except ErrorValidacionCliente as err:
        logger.registrar("ERROR", f"Operación 3 controlada: {err}")

    # 4. Registro inválido de Cliente por ID vacío (demuestra encadenamiento de excepciones).
    try:
        cliente_sin_id = Cliente("", "Pedro Díaz", "pedro@correo.com", "3112223344")
        gestor.registrar_cliente(cliente_sin_id)
    except ErrorValidacionCliente as err:
        causa = repr(err.__cause__) if err.__cause__ else None
        logger.registrar("ERROR", f"Operación 4 controlada con encadenamiento: {err}", causa)

    # 5. Creación válida de Servicio 1: Reserva de Sala.
    try:
        sala_juntas = ReservaSala("SRV-001", "Sala Ejecutiva Norte", 50000.0, capacidad_personas=12, disponible=True)
    except ErrorSistemaSoftwareFJ as err:
        logger.registrar("ERROR", f"Operación 5 fallida: {err}")
    else:
        gestor.registrar_servicio(sala_juntas)

    # 6. Creación válida de Servicio 2: Alquiler de Equipo.
    try:
        laptop_pro = AlquilerEquipo("SRV-002", "Portátil Desarrollo Workstation", 80000.0, unidades_stock=5, disponible=True)
    except ErrorSistemaSoftwareFJ as err:
        logger.registrar("ERROR", f"Operación 6 fallida: {err}")
    else:
        gestor.registrar_servicio(laptop_pro)

    # 7. Creación válida de Servicio 3: Asesoría Especializada NO disponible.
    try:
        asesoria_cloud = AsesoriaEspecializada(
            "SRV-003", "Arquitectura Cloud y Seguridad", 120000.0, especialidad="Cloud Computing", disponible=False
        )
    except ErrorSistemaSoftwareFJ as err:
        logger.registrar("ERROR", f"Operación 7 fallida: {err}")
    else:
        gestor.registrar_servicio(asesoria_cloud)

    # 8. Creación inválida de Servicio por tarifa negativa (ErrorCalculoCosto).
    try:
        servicio_malo = ReservaSala("SRV-004", "Sala Económica", -15000.0, capacidad_personas=6)
        gestor.registrar_servicio(servicio_malo)
    except (ErrorValidacionServicio, ErrorCalculoCosto) as err:
        logger.registrar("ERROR", f"Operación 8 controlada: {err}")

    # 9. Reserva exitosa y procesada con descuento, recargo e impuesto (try / except / finally).
    estado_op9 = "NO INICIADA"
    try:
        reserva_1 = Reserva(
            "RES-001",
            cliente_1,
            sala_juntas,
            duracion=4,
            descuento_pct=10.0,
            impuesto_pct=19.0,
            recargo_adicional=15000.0,
        )
        gestor.crear_reserva(reserva_1)
        total_1 = reserva_1.procesar()
        estado_op9 = f"PROCESADA (${total_1:,.2f})"
    except ErrorSistemaSoftwareFJ as err:
        estado_op9 = f"FALLIDA ({err})"
        logger.registrar("ERROR", f"Operación 9 fallida: {err}")
    finally:
        logger.registrar("INFO", f"Operación 9 finalizada con estado: {estado_op9}")

    # 10. Reserva fallida por intentar reservar un servicio no disponible.
    try:
        reserva_fallida_disp = Reserva("RES-002", cliente_2, asesoria_cloud, duracion=2)
        gestor.crear_reserva(reserva_fallida_disp)
    except ErrorServicioNoDisponible as err:
        logger.registrar("ERROR", f"Operación 10 controlada (servicio no disponible): {err}")

    # 11. Reserva fallida por duración inválida (0 días).
    try:
        reserva_fallida_dur = Reserva("RES-003", cliente_2, laptop_pro, duracion=0)
        gestor.crear_reserva(reserva_fallida_dur)
    except (ErrorValidacionServicio, ErrorReservaInvalida) as err:
        logger.registrar("ERROR", f"Operación 11 controlada (duración inválida): {err}")

    # 12. Operación no permitida: cancelar una reserva ya procesada.
    try:
        reserva_1.cancelar()
    except ErrorReservaInvalida as err:
        logger.registrar("ERROR", f"Operación 12 controlada (operación no permitida): {err}")

    # Resumen final confirmando que el sistema continuó activo tras los errores.
    logger.registrar(
        "INFO",
        f"=== FIN SIMULACIÓN | Clientes: {len(gestor.clientes)} | "
        f"Servicios: {len(gestor.servicios)} | Reservas: {len(gestor.reservas)} ===",
    )


if __name__ == "__main__":
    ejecutar_simulacion()
