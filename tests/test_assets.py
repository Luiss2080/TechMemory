"""Los archivos que usa el juego existen con el nombre exacto (Linux distingue mayúsculas)."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import Poryecto_Final as juego  # noqa: E402  (no ejecuta el juego: main() está protegido)

DISCO = set(os.listdir(os.path.join(ROOT, "Material")))


def test_imagenes_de_pares_existen():
    faltan = [n for n in juego.IMAGENES + ["Ocultaa.png"] if n not in DISCO]
    assert faltan == []


def test_sonidos_referenciados_existen():
    fuente = open(os.path.join(ROOT, "Poryecto_Final.py"), encoding="utf-8").read()
    sonidos = re.findall(r'cargar_sonido\("([^"]+)"\)', fuente)
    assert len(sonidos) == 5
    assert [s for s in sonidos if s not in DISCO] == []


def test_tablero_del_juego_es_valido():
    from logica_juego import Tablero
    t = Tablero(juego.IMAGENES, juego.COLUMNAS)
    assert len(t.cartas) == 16
