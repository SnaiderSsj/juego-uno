import pygame

ANCHO, ALTO = 1000, 600

COLORES = {
    'Rojo': (255, 0, 0),
    'Azul': (0, 0, 255),
    'Verde': (0, 200, 0),
    'Amarillo': (255, 255, 0),
    'Blanco': (255, 255, 255),
    'Negro': (0, 0, 0),
    'Gris': (200, 200, 200)
}

pygame.font.init()
FUENTE = pygame.font.SysFont('arial', 24)
