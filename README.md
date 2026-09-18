# TechMemory

Juego de memoria en Python con Pygame: se voltean cartas de a dos para encontrar los pares de logotipos tecnológicos antes de que se acabe el tiempo. Nació como proyecto de la asignatura Programación I (Universidad Privada Domingo Savio, Facultad de Ingeniería; estudiantes Carlos Eduardo Salvatierra Chávez, Luis Mario Rocha Vela y Jesús Enrique Salas Espinoza; docente Zambrana Chacón Jaime). El título del juego en el código es "CodePairs".

## Qué hace (verificado en el código y con tests)

- Tablero de 4x4 con 8 pares de logotipos; el mazo se baraja en cada partida y cada logotipo aparece exactamente dos veces.
- Cronómetro en cuenta regresiva de **3 minutos** (180 s; el README anterior decía 2 minutos, era incorrecto). Al llegar a 0 la partida se pierde.
- Un par distinto queda visible 1 segundo y se vuelve a ocultar; mientras tanto no se aceptan más clics en cartas.
- Hacer clic dos veces en la misma carta, o en una carta ya acertada, se ignora.
- Puntaje: 10 puntos por cada carta descubierta (20 por par; máximo 160).
- Al ganar o perder, el botón inferior permite volver a jugar: se rebaraja y se reinicia tiempo, puntaje y selección.
- Efectos de sonido (voltear, acierto, fallo, victoria) y música de fondo. Si no hay dispositivo de audio, el juego arranca en silencio.

No existe contador de movimientos ni ranking: no están implementados.

## Requisitos e instalación

Python 3.10 o superior.

```bash
pip install -r requirements.txt
```

`requirements.txt` usa `pygame-ce`, un fork compatible de Pygame (el código no usa nada específico del fork; el `pygame` clásico también debería servir, pero solo se probó `pygame-ce` 2.5.7 con Python 3.14).

## Ejecutar

```bash
python Poryecto_Final.py
```

(El nombre del archivo tiene el error tipográfico original; se conserva para no romper enlaces.) Se ejecuta desde cualquier carpeta: las rutas de `Material/` son relativas al script.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

La lógica del juego (`logica_juego.py`) no depende de Pygame y tiene 20 tests; otros 3 comprueban que los archivos de `Material/` existan con las mayúsculas exactas. En un entorno sin pantalla/sonido usa `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy`. El workflow de GitHub Actions (`.github/workflows/ci.yml`) ejecuta lo mismo en Python 3.10 y 3.12.

Los tests **no** cubren el dibujado ni la interacción real con el ratón; esa parte solo se verificó con una ejecución de humo sin pantalla (arranque, clic en "Iniciar", clic en una carta, cierre).

## Estructura

- `Poryecto_Final.py`: ventana, dibujo, sonido y eventos.
- `logica_juego.py`: reglas puras (mazo, jugadas, victoria, tiempo).
- `Material/`: imágenes y sonidos. `clic.wav` y `wthatsApp.png` no se usan.
- `tests/`: pruebas con pytest.

## Limitaciones conocidas

- **Logotipos de terceros:** las imágenes representan marcas de terceros (C++, Chrome, GitHub, Python, Visual Studio Code, Wi-Fi, etc.). No hay constancia en el repositorio de que se tengan permisos ni licencias para redistribuirlas; úsalas solo con fines educativos y reemplázalas antes de cualquier distribución.
- **Origen del código:** el título de ventana original mencionaba "Memorama en Python - By Parzibyte", lo que indica que la base del código proviene de un tutorial de ese autor; no se ha verificado su licencia ni se conserva atribución formal.
- **Sonidos:** se desconoce el origen y la licencia de los `.wav`. `FondoPerfect.wav` pesa unos 32 MB, lo que engorda el repositorio.
- Tablero y duración fijos en el código (no configurables por el usuario).
- Sin pantalla de menú, sin pausa y sin guardado de resultados.
- La ventana usa la fuente "Arial black" del sistema; si no existe, Pygame usa una de reemplazo.

## Licencia

Este repositorio **no incluye archivo LICENSE**, por lo que por defecto todos los derechos están reservados por sus autores y no se concede permiso de reutilización. Los autores deberían añadir una licencia explícita si desean permitirlo (y resolver antes lo indicado sobre logotipos y sonidos).
