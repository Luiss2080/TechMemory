import os
import random
import sys
from collections import Counter

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logica_juego as lj  # noqa: E402

NOMBRES = ["a", "b", "c", "d", "e", "f", "g", "h"]


def nuevo(ahora=0.0, semilla=1):
    t = lj.Tablero(NOMBRES, 4)
    t.iniciar(ahora, random.Random(semilla))
    return t


def indices(t, nombre):
    return [i for i, c in enumerate(t.cartas) if c.nombre == nombre]


def indices_distintos(t):
    a = indices(t, "a")[0]
    b = indices(t, "b")[0]
    return a, b


def test_barajar_pares_cada_nombre_dos_veces():
    for semilla in range(50):
        mazo = lj.barajar_pares(NOMBRES, random.Random(semilla))
        assert Counter(mazo) == {n: 2 for n in NOMBRES}


def test_tablero_tiene_16_cartas_4x4_y_pares_completos():
    t = nuevo()
    assert (t.filas, t.columnas, len(t.cartas)) == (4, 4, 16)
    assert Counter(c.nombre for c in t.cartas) == {n: 2 for n in NOMBRES}


def test_tablero_rechaza_configuracion_invalida():
    with pytest.raises(ValueError):
        lj.Tablero(["a", "b", "c"], 4)
    with pytest.raises(ValueError):
        lj.Tablero(["a", "a"], 2)


def test_iniciar_oculta_todo_y_arranca():
    t = lj.Tablero(NOMBRES, 4)
    assert t.estado == lj.ESPERA
    assert t.iniciar(0)
    assert t.estado == lj.JUGANDO
    assert not any(c.mostrar or c.descubierto for c in t.cartas)


def test_sin_iniciar_no_se_puede_jugar():
    t = lj.Tablero(NOMBRES, 4)
    assert t.seleccionar(0, 0) == lj.IGNORADO
    assert not t.cartas[0].mostrar


def test_iniciar_durante_partida_no_reinicia():
    t = nuevo()
    t.seleccionar(0, 1)
    assert t.iniciar(2) is False
    assert t.cartas[0].mostrar


def test_acierto_marca_ambas_descubiertas():
    t = nuevo()
    i, j = indices(t, "a")
    assert t.seleccionar(i, 1) == lj.PRIMERA
    assert t.seleccionar(j, 1.1) == lj.ACIERTO
    assert t.cartas[i].descubierto and t.cartas[j].descubierto
    assert t.primera is None
    assert t.puntaje() == 20


def test_misma_carta_dos_veces_no_es_acierto():
    t = nuevo()
    i = 0
    assert t.seleccionar(i, 1) == lj.PRIMERA
    assert t.seleccionar(i, 1.1) == lj.IGNORADO
    assert not t.cartas[i].descubierto
    assert t.primera == i


def test_fallo_muestra_ambas_y_las_oculta_tras_el_tiempo():
    t = nuevo()
    a, b = indices_distintos(t)
    t.seleccionar(a, 1)
    assert t.seleccionar(b, 2) == lj.FALLO
    assert t.cartas[a].mostrar and t.cartas[b].mostrar  # se ven durante la espera
    t.actualizar(2 + lj.SEGUNDOS_MOSTRAR_PIEZA - 0.01)
    assert t.cartas[a].mostrar and t.cartas[b].mostrar
    t.actualizar(2 + lj.SEGUNDOS_MOSTRAR_PIEZA)
    assert not t.cartas[a].mostrar and not t.cartas[b].mostrar
    assert not t.cartas[a].descubierto


def test_tercera_carta_durante_fallo_se_ignora():
    t = nuevo()
    a, b = indices_distintos(t)
    c = indices(t, "c")[0]
    t.seleccionar(a, 1)
    t.seleccionar(b, 2)
    assert t.seleccionar(c, 2.5) == lj.IGNORADO
    assert not t.cartas[c].mostrar


def test_tercera_carta_tras_vencer_el_fallo_se_acepta():
    t = nuevo()
    a, b = indices_distintos(t)
    c = indices(t, "c")[0]
    t.seleccionar(a, 1)
    t.seleccionar(b, 2)
    assert t.seleccionar(c, 3.5) == lj.PRIMERA
    assert not t.cartas[a].mostrar


def test_carta_ya_acertada_no_es_clicable():
    t = nuevo()
    i, j = indices(t, "a")
    t.seleccionar(i, 1)
    t.seleccionar(j, 1.1)
    assert t.seleccionar(i, 2) == lj.IGNORADO
    assert t.primera is None


def test_indice_fuera_de_rango():
    t = nuevo()
    assert t.indice(4, 0) is None
    assert t.indice(0, 4) is None
    assert t.indice(-1, 0) is None
    assert t.indice(3, 3) == 15
    assert t.seleccionar(None, 1) == lj.IGNORADO
    assert t.seleccionar(99, 1) == lj.IGNORADO


def test_victoria_al_descubrir_todo():
    t = nuevo()
    ahora = 1.0
    for n in NOMBRES:
        i, j = indices(t, n)
        t.seleccionar(i, ahora)
        t.seleccionar(j, ahora + 0.1)
        ahora += 1
    assert t.gana()
    assert t.estado == lj.GANADO
    assert t.puntaje() == 160
    assert t.seleccionar(0, ahora) == lj.IGNORADO


def test_no_hay_victoria_con_pares_pendientes():
    t = nuevo()
    for n in NOMBRES[:-1]:
        i, j = indices(t, n)
        t.seleccionar(i, 1)
        t.seleccionar(j, 1.1)
    assert not t.gana()
    assert t.estado == lj.JUGANDO


def test_cronometro_cuenta_regresiva():
    t = lj.Tablero(NOMBRES, 4)
    assert t.tiempo_restante(100) == lj.DURACION_JUEGO  # antes de iniciar
    t.iniciar(100)
    assert t.tiempo_restante(100) == lj.DURACION_JUEGO
    assert t.tiempo_restante(130.9) == lj.DURACION_JUEGO - 30
    assert t.tiempo_restante(100 + lj.DURACION_JUEGO + 50) == 0


def test_derrota_al_agotarse_el_tiempo():
    t = nuevo(ahora=0)
    t.actualizar(lj.DURACION_JUEGO - 1)
    assert t.estado == lj.JUGANDO
    t.actualizar(lj.DURACION_JUEGO)
    assert t.estado == lj.PERDIDO
    assert t.seleccionar(0, lj.DURACION_JUEGO + 1) == lj.IGNORADO


def test_seleccion_en_el_instante_del_fin_no_cuenta():
    t = nuevo(ahora=0)
    assert t.seleccionar(0, lj.DURACION_JUEGO) == lj.IGNORADO
    assert t.estado == lj.PERDIDO


def test_reiniciar_tras_timeout_limpia_seleccion_pendiente():
    """Regresion: una carta elegida antes del timeout no debe sobrevivir."""
    t = nuevo(ahora=0)
    t.seleccionar(0, 10)
    t.actualizar(lj.DURACION_JUEGO + 1)
    assert t.estado == lj.PERDIDO
    assert t.iniciar(500, random.Random(7))
    assert t.primera is None
    assert t.estado == lj.JUGANDO
    assert t.tiempo_restante(500) == lj.DURACION_JUEGO
    assert not any(c.mostrar or c.descubierto for c in t.cartas)
    assert t.puntaje() == 0
    # la primera jugada del nuevo juego es una "primera", no una comparacion
    assert t.seleccionar(0, 501) == lj.PRIMERA


def test_reiniciar_tras_victoria_baraja_de_nuevo_y_conserva_pares():
    t = nuevo()
    ahora = 1.0
    for n in NOMBRES:
        i, j = indices(t, n)
        t.seleccionar(i, ahora)
        t.seleccionar(j, ahora + 0.1)
        ahora += 1
    assert t.estado == lj.GANADO
    assert t.iniciar(ahora, random.Random(99))
    assert t.estado == lj.JUGANDO and t.puntaje() == 0
    assert Counter(c.nombre for c in t.cartas) == {n: 2 for n in NOMBRES}
