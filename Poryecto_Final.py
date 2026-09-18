import os
import sys
import time

import pygame

import logica_juego as lj

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIAL = os.path.join(BASE_DIR, "Material")

ALTURA_BOTON = 40
MEDIDA_CUADRO = 165
COLUMNAS = 4

# Nombre de archivo de cada par (respetando mayúsculas: Linux distingue).
IMAGENES = ["C++.png", "chat.png", "chrome.png", "Github.png",
            "phyton.png", "Turtle.png", "Wifi.png", "Visual_Code.png"]

COLOR_BLANCO = (255, 255, 255)
COLOR_ROJO = (255, 0, 0)
COLOR_AZUL = (30, 136, 229)


def ruta(nombre):
    return os.path.join(MATERIAL, nombre)


def cargar_sonido(nombre):
    """Devuelve un Sound o None si no hay dispositivo de audio / falta el archivo."""
    if not pygame.mixer.get_init():
        return None
    try:
        return pygame.mixer.Sound(ruta(nombre))
    except (pygame.error, FileNotFoundError) as exc:
        print(f"Aviso: no se pudo cargar el sonido {nombre}: {exc}")
        return None


def reproducir(sonido, veces=0):
    if sonido is not None:
        sonido.play(veces)


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as exc:
        print(f"Aviso: sin audio ({exc}); el juego continúa en silencio.")

    tablero = lj.Tablero(IMAGENES, COLUMNAS)
    ancho = tablero.columnas * MEDIDA_CUADRO
    alto = tablero.filas * MEDIDA_CUADRO + ALTURA_BOTON
    pantalla = pygame.display.set_mode((ancho, alto))
    pygame.display.set_caption("CodePairs - Juego de memoria")

    imagenes = {
        n: pygame.transform.scale(pygame.image.load(ruta(n)).convert_alpha(),
                                  (MEDIDA_CUADRO, MEDIDA_CUADRO))
        for n in IMAGENES
    }
    oculta = pygame.transform.scale(
        pygame.image.load(ruta("Ocultaa.png")).convert_alpha(),
        (MEDIDA_CUADRO, MEDIDA_CUADRO))

    s_fondo = cargar_sonido("FondoPerfect.wav")
    s_clic = cargar_sonido("Correcta.wav")
    s_exito = cargar_sonido("ganador .wav")
    s_fracaso = cargar_sonido("equivocado .wav")
    s_voltear = cargar_sonido("voltear.wav")

    fuente = pygame.font.SysFont("Arial black", 20)
    boton = pygame.Rect(0, alto - ALTURA_BOTON, ancho, ALTURA_BOTON)
    reloj = pygame.time.Clock()
    reproducir(s_fondo, -1)
    estado_previo = tablero.estado

    while True:
        ahora = time.monotonic()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type != pygame.MOUSEBUTTONDOWN:
                continue
            x, y = evento.pos
            if boton.collidepoint(evento.pos):
                if tablero.iniciar(ahora):
                    reproducir(s_clic)
                continue
            resultado = tablero.seleccionar(
                tablero.indice(x // MEDIDA_CUADRO, y // MEDIDA_CUADRO), ahora)
            if resultado == lj.PRIMERA:
                reproducir(s_voltear)
            elif resultado == lj.ACIERTO:
                reproducir(s_clic)
            elif resultado == lj.FALLO:
                reproducir(s_fracaso)

        tablero.actualizar(ahora)
        if tablero.estado != estado_previo and tablero.estado == lj.GANADO:
            reproducir(s_exito)
        estado_previo = tablero.estado

        pantalla.fill(COLOR_BLANCO)
        for i, carta in enumerate(tablero.cartas):
            pos = ((i % tablero.columnas) * MEDIDA_CUADRO,
                   (i // tablero.columnas) * MEDIDA_CUADRO)
            visible = carta.mostrar or carta.descubierto
            pantalla.blit(imagenes[carta.nombre] if visible else oculta, pos)

        if tablero.estado == lj.JUGANDO:
            pygame.draw.rect(pantalla, COLOR_BLANCO, boton)
            texto = f"Puntos: {tablero.puntaje()}"
        else:
            pygame.draw.rect(pantalla, COLOR_AZUL, boton)
            texto = {lj.GANADO: "Ganaste. Jugar de nuevo",
                     lj.PERDIDO: "Se acabo el tiempo. Reintentar"}.get(
                         tablero.estado, "Iniciar juego")
        color = COLOR_ROJO if tablero.estado == lj.JUGANDO else COLOR_BLANCO
        render = fuente.render(texto, True, color)
        pantalla.blit(render, render.get_rect(center=boton.center))

        cronometro = time.strftime("%M:%S", time.gmtime(tablero.tiempo_restante(ahora)))
        pantalla.blit(fuente.render(cronometro, True, COLOR_ROJO), (10, 10))
        pygame.display.update()
        reloj.tick(60)


if __name__ == "__main__":
    main()
