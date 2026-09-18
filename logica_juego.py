"""Lógica pura del juego de memoria CodePairs (sin pygame, testeable).

El tiempo se inyecta como parámetro ``ahora`` (segundos, reloj monotónico)
para que la lógica sea determinista y no bloquee el bucle de dibujo.
"""
import random

DURACION_JUEGO = 180          # segundos
SEGUNDOS_MOSTRAR_PIEZA = 1.0  # tiempo que se ve un par incorrecto
PUNTOS_POR_CARTA = 10

ESPERA = "espera"
JUGANDO = "jugando"
GANADO = "ganado"
PERDIDO = "perdido"

# Resultados de seleccionar()
IGNORADO = "ignorado"
PRIMERA = "primera"
ACIERTO = "acierto"
FALLO = "fallo"


class Carta:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mostrar = False
        self.descubierto = False


def barajar_pares(nombres, rng=random):
    """Devuelve cada nombre exactamente dos veces, en orden aleatorio."""
    mazo = [n for n in nombres for _ in range(2)]
    rng.shuffle(mazo)
    return mazo


class Tablero:
    def __init__(self, nombres, columnas):
        mazo_size = len(nombres) * 2
        if columnas <= 0 or mazo_size % columnas != 0:
            raise ValueError("Las cartas no llenan un tablero rectangular")
        if len(set(nombres)) != len(nombres):
            raise ValueError("Los nombres de par deben ser únicos")
        self.nombres = list(nombres)
        self.columnas = columnas
        self.filas = mazo_size // columnas
        self.cartas = [Carta(n) for n in barajar_pares(self.nombres)]
        self.estado = ESPERA
        self.primera = None       # índice de la primera carta elegida
        self.par_fallido = None   # (i, j) pendiente de ocultarse
        self._oculta_en = None
        self._inicio = None

    # --- ciclo de vida -------------------------------------------------
    def iniciar(self, ahora, rng=random):
        """Baraja, oculta todo y arranca el cronómetro (también reinicia)."""
        if self.estado == JUGANDO:
            return False
        mazo = barajar_pares(self.nombres, rng)
        self.cartas = [Carta(n) for n in mazo]
        self.primera = None
        self.par_fallido = None
        self._oculta_en = None
        self._inicio = ahora
        self.estado = JUGANDO
        return True

    def tiempo_restante(self, ahora):
        if self.estado == ESPERA or self._inicio is None:
            return DURACION_JUEGO
        return max(DURACION_JUEGO - int(ahora - self._inicio), 0)

    def actualizar(self, ahora):
        """Oculta el par fallido cuando vence su tiempo y detecta el fin por tiempo."""
        if self.estado != JUGANDO:
            return
        if self.par_fallido and ahora >= self._oculta_en:
            i, j = self.par_fallido
            self.cartas[i].mostrar = False
            self.cartas[j].mostrar = False
            self.par_fallido = None
            self._oculta_en = None
        if self.tiempo_restante(ahora) == 0:
            self.estado = PERDIDO
            self.primera = None
            self.par_fallido = None

    # --- jugada --------------------------------------------------------
    def indice(self, columna, fila):
        if not (0 <= columna < self.columnas and 0 <= fila < self.filas):
            return None
        return fila * self.columnas + columna

    def seleccionar(self, indice, ahora):
        if self.estado != JUGANDO or indice is None:
            return IGNORADO
        self.actualizar(ahora)
        if self.estado != JUGANDO or self.par_fallido:
            return IGNORADO  # dos cartas ya reveladas: no se admite una tercera
        if not 0 <= indice < len(self.cartas):
            return IGNORADO
        carta = self.cartas[indice]
        if carta.mostrar or carta.descubierto:
            return IGNORADO  # la misma carta (o una ya acertada) no cuenta
        carta.mostrar = True
        if self.primera is None:
            self.primera = indice
            return PRIMERA
        otra = self.cartas[self.primera]
        if otra.nombre == carta.nombre:
            otra.descubierto = carta.descubierto = True
            self.primera = None
            if self.gana():
                self.estado = GANADO
            return ACIERTO
        self.par_fallido = (self.primera, indice)
        self._oculta_en = ahora + SEGUNDOS_MOSTRAR_PIEZA
        self.primera = None
        return FALLO

    # --- consultas -----------------------------------------------------
    def gana(self):
        return all(c.descubierto for c in self.cartas)

    def puntaje(self):
        return sum(c.descubierto for c in self.cartas) * PUNTOS_POR_CARTA
