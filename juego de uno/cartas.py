import random
import pygame
from constantes import COLORES, FUENTE
from collections import deque  # para colas

class Carta:
    def __init__(self, color, valor):
        self.color = color
        self.valor = valor
        self.rect = pygame.Rect(0, 0, 80, 120)
        self.especial = valor in ["+2", "+4", "CambioColor", "Salto", "Reversa"]

    def dibujar(self, ventana, x, y):
        self.rect.topleft = (x, y)
        color_real = COLORES.get(self.color, COLORES['Gris'])
        pygame.draw.rect(ventana, color_real, self.rect)
        pygame.draw.rect(ventana, COLORES['Negro'], self.rect, 2)
        texto = FUENTE.render(f"{self.valor}", True, COLORES['Negro'])
        ventana.blit(texto, (x + 15, y + 45))

    def es_compatible(self, otra):
        if self.especial and self.color == "comodín":
            return True  # Comodines son siempre compatibles
        return (
            self.color == otra.color or
            self.valor == otra.valor or
            self.color == "comodín"
        )

    def aplicar_efecto(self, mazo, manos, turnos):
        if self.valor == "+2":
            siguiente_jugador = turnos[1]
            manos[siguiente_jugador].extend(repartir_cartas(mazo, 2))
            turnos.rotate(-1)  # Pasa el turno después de robar
        elif self.valor == "+4":
            siguiente_jugador = turnos[1]
            manos[siguiente_jugador].extend(repartir_cartas(mazo, 4))
            turnos.rotate(-1)
        elif self.valor == "CambioColor":
            return True  # Indica que necesita selección de color
        elif self.valor == "Salto":
            turnos.rotate(-1)  # Salta al siguiente jugador
        elif self.valor == "Reversa":
            turnos.reverse()  # Invierte la dirección de la cola
            turnos.rotate(-1)
        return False

def repartir_cartas(mazo, cantidad):
    return [mazo.pop() for _ in range(cantidad)]

def generar_mazo():
    colores = ['Rojo', 'Azul', 'Verde', 'Amarillo']
    valores = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    mazo = []

    for color in colores:
        for valor in valores:
            mazo.append(Carta(color, valor))
            if valor != '0':
                mazo.append(Carta(color, valor))

    # Cartas especiales
    for color in colores:
        for _ in range(2):
            mazo.append(Carta(color, "+2"))
            mazo.append(Carta(color, "Salto"))
            mazo.append(Carta(color, "Reversa"))

    for _ in range(4):
        mazo.append(Carta("comodín", "+4"))
        mazo.append(Carta("comodín", "CambioColor"))

    random.shuffle(mazo)
    return mazo[::-1]  # pila (última carta se usa con .pop())