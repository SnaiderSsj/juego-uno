import pygame
import random
import sys
from collections import deque

pygame.init()

# Configuración de la ventana y fuente
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("UNO Simplificado")
fuente = pygame.font.SysFont("arial", 24)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# --- Clase para botones ---
class Button:
    def __init__(self, rect, text, color, text_color=NEGRO):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = fuente.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- Clase Carta ---
class Carta:
    def __init__(self, color, valor):
        self.color = color  # Puede ser "Rojo", "Verde", "Azul", "Amarillo" o None para comodín
        self.valor = valor

    def es_compatible(self, otra, color_actual):
        # Los comodines (color None) son siempre compatibles
        if self.color is None:
            return True
        return (self.color == otra.color or self.valor == otra.valor or self.color == color_actual)

    def __str__(self):
        if self.color is None:
            return f"Comodín {self.valor}"
        return f"{self.color} {self.valor}"

    def dibujar(self, surface, x, y):
        rect = pygame.Rect(x, y, 80, 120)
        # Mapeo de colores básicos
        color_map = {
            "Rojo": (255, 0, 0),
            "Verde": (0, 255, 0),
            "Azul": (0, 0, 255),
            "Amarillo": (255, 255, 0)
        }
        if self.color is None:
            bg = (160, 32, 240)  # Para comodines
        else:
            bg = color_map.get(self.color, (128, 128, 128))
        pygame.draw.rect(surface, bg, rect)
        pygame.draw.rect(surface, NEGRO, rect, 2)
        texto = fuente.render(str(self.valor), True, NEGRO)
        surface.blit(texto, (x + 10, y + 45))
        self.rect = rect

# --- Funciones auxiliares ---
def crear_mazo():
    colores = ["Rojo", "Verde", "Azul", "Amarillo"]
    numeros = [str(n) for n in range(10)]
    especiales = ["+2", "Reversa", "Salto"]
    mazo = []
    # Cartas numéricas: dos de cada (menos el 0, que solo se agrega una vez)
    for color in colores:
        for num in numeros:
            if num == "0":
                mazo.append(Carta(color, num))
            else:
                mazo.extend([Carta(color, num)] * 2)
        # Cartas especiales
        for esp in especiales:
            mazo.extend([Carta(color, esp)] * 2)
    # Comodines y +4
    mazo.extend([Carta(None, "Comodín"), Carta(None, "+4")] * 4)
    random.shuffle(mazo)
    return mazo

def repartir_cartas(mazo, cantidad):
    return [mazo.pop() for _ in range(cantidad)]

def calcular_puntuacion(mano):
    puntos = 0
    for carta in mano:
        if carta.valor.isdigit():
            puntos += int(carta.valor)
        elif carta.valor in ["+2", "Reversa", "Salto"]:
            puntos += 20
        else:
            puntos += 50
    return puntos

def guardar_historial(resultado):
    with open("historial.txt", "a") as f:
        f.write(resultado + "\n")

# --- Función principal del juego ---
def main():
    reloj = pygame.time.Clock()
    mazo = crear_mazo()
    jugadores = ["Jugador 1", "Jugador 2"]
    manos = {j: repartir_cartas(mazo, 7) for j in jugadores}
    turnos = deque(jugadores)
    
    # Seleccionar una carta inicial que no sea un comodín
    carta_en_juego = mazo.pop()
    while carta_en_juego.color is None:
        mazo.insert(0, carta_en_juego)
        random.shuffle(mazo)
        carta_en_juego = mazo.pop()
    color_actual = carta_en_juego.color

    # Crear botones: uno para "Pasar" y otro para "UNO"
    boton_pasar = Button((650, 450, 120, 50), "Pasar", (200, 200, 200))
    boton_uno = Button((650, 520, 120, 50), "UNO", (200, 200, 200))
    
    # Crear botones para seleccionar color
    colores = ["Rojo", "Verde", "Azul", "Amarillo"]
    color_map = {
        "Rojo": (255, 0, 0),
        "Verde": (0, 255, 0),
        "Azul": (0, 0, 255),
        "Amarillo": (255, 255, 0)
    }
    botones_color = [
        Button((50 + i * 100, 400, 80, 40), color, color_map[color])
        for i, color in enumerate(colores)
    ]
    
    seleccionado = 0
    uno_presionado = False
    en_juego = True
    esperando_color = False  # Estado para saber si estamos esperando la selección de color
    carta_jugada = None  # Almacena la carta jugada mientras se selecciona el color

    while en_juego:
        pantalla.fill(BLANCO)
        jugador = turnos[0]
        mano = manos[jugador]

        # Dibujar interfaz de texto
        turno_texto = fuente.render(f"Turno: {jugador}", True, NEGRO)
        pantalla.blit(turno_texto, (50, 20))
        carta_texto = fuente.render(f"Carta en juego: {carta_en_juego}", True, NEGRO)
        pantalla.blit(carta_texto, (50, 60))
        color_texto = fuente.render(f"Color actual: {color_actual}", True, NEGRO)
        pantalla.blit(color_texto, (50, 100))
        mano_texto = fuente.render("Tu mano:", True, NEGRO)
        pantalla.blit(mano_texto, (50, 140))
        
        # Dibujar las cartas de la mano
        for i, carta in enumerate(mano):
            carta.dibujar(pantalla, 50 + i * 90, 180)
            if i == seleccionado and not esperando_color:  # No resaltar si estamos esperando color
                pygame.draw.rect(pantalla, NEGRO, carta.rect, 4)
        
        # Dibujar los botones
        boton_pasar.draw(pantalla)
        boton_uno.draw(pantalla)
        if uno_presionado:
            uno_texto = fuente.render("¡UNO!", True, (255, 0, 0))
            pantalla.blit(uno_texto, (650, 20))
        
        # Dibujar botones de color si estamos esperando selección
        if esperando_color:
            instruccion = fuente.render("Elige un color:", True, NEGRO)
            pantalla.blit(instruccion, (50, 360))
            for boton in botones_color:
                boton.draw(pantalla)
        
        pygame.display.flip()
        
        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                en_juego = False
                
            elif evento.type == pygame.KEYDOWN and not esperando_color:  # Deshabilitar teclas mientras se elige color
                if evento.key == pygame.K_LEFT and mano:
                    seleccionado = (seleccionado - 1) % len(mano)
                elif evento.key == pygame.K_RIGHT and mano:
                    seleccionado = (seleccionado + 1) % len(mano)
                elif evento.key == pygame.K_u:
                    if len(mano) == 1:
                        uno_presionado = True
                elif evento.key == pygame.K_p:  # Tecla P para "Pasar"
                    if mazo:
                        mano.append(mazo.pop())
                    for idx, carta in enumerate(mano):
                        if carta.valor == "Salto":
                            mano.pop(idx)
                            break
                    turnos.rotate(-1)
                    uno_presionado = False
                elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if mano:
                        carta = mano[seleccionado]
                        if carta.es_compatible(carta_en_juego, color_actual):
                            carta_en_juego = carta
                            mano.pop(seleccionado)
                            seleccionado = min(seleccionado, len(mano) - 1) if mano else 0
                            uno_presionado = False
                            
                            # Efectos de cartas
                            if carta.valor == "+2":
                                turnos.rotate(-1)
                                if mazo:
                                    manos[turnos[0]].extend(repartir_cartas(mazo, 2))
                                turnos.rotate(-1)
                            elif carta.valor == "Reversa":
                                pass  # En 2 jugadores, repetir turno
                            elif carta.valor == "Salto":
                                turnos.rotate(-1)
                            elif carta.valor in ["Comodín", "+4"]:
                                esperando_color = True  # Activar selección de color
                                carta_jugada = carta  # Guardar la carta jugada
                                continue  # No rotar turno hasta elegir color
                            else:
                                turnos.rotate(-1)
                        else:
                            if mazo:
                                mano.append(mazo.pop())
                
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if esperando_color:
                    # Verificar si se hizo clic en un botón de color
                    for boton in botones_color:
                        if boton.is_clicked(pos):
                            color_actual = boton.text  # Actualizar color actual
                            esperando_color = False  # Desactivar selección de color
                            if carta_jugada.valor == "+4":
                                turnos.rotate(-1)
                                if mazo:
                                    manos[turnos[0]].extend(repartir_cartas(mazo, 4))
                                turnos.rotate(-1)
                            else:
                                turnos.rotate(-1)
                            carta_jugada = None  # Limpiar carta jugada
                            break
                else:
                    # Manejo de botones "Pasar" y "UNO"
                    if boton_pasar.is_clicked(pos):
                        if mazo:
                            mano.append(mazo.pop())
                        for idx, carta in enumerate(mano):
                            if carta.valor == "Salto":
                                mano.pop(idx)
                                break
                        turnos.rotate(-1)
                        uno_presionado = False
                    elif boton_uno.is_clicked(pos):
                        if len(mano) == 1:
                            uno_presionado = True
        
        # Verificar si el jugador se quedó sin cartas (gana la ronda)
        if not mano:
            ganador = jugador
            perdedor = [j for j in jugadores if j != jugador][0]
            puntos = calcular_puntuacion(manos[perdedor]) if manos[perdedor] else 0
            pantalla.fill(BLANCO)
            mensaje = f"{ganador} ganó la ronda y obtuvo {puntos} puntos."
            final_text = fuente.render(mensaje, True, NEGRO)
            pantalla.blit(final_text, (100, 250))
            pygame.display.flip()
            pygame.time.wait(5000)
            guardar_historial(mensaje)
            en_juego = False

        reloj.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Ocurrió un error:", e)