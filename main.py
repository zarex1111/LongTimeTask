from needful_funcs import get_params
import pygame
import sys
from io import BytesIO
import requests


def change_delta(previous, k):
    f_p = float(previous)
    change = f_p / 1.6
    if 50 > f_p + k * change > 0:
        f_p += k * change
    return str(f_p)


def change_coords(previous, k1, k2, delta):
    moving = float(delta) * 0.3
    par, mer = previous
    par, mer = float(par), float(mer)
    if -180 < par + k2 * moving < 180:
        par += k2 * moving
    if -90 < mer + k1 * moving < 90:
        mer += k1 * moving
    return (str(par), str(mer))


if __name__ == '__main__':

    pygame.init()

    screen = pygame.display.set_mode((600, 450))
    pygame.display.set_caption('Большая задача на Maps Api')

    run = True 

    coords = ('37.168', '56.737')  #Изменяемая часть
    delta = '0.002' #Изменяемая часть

    FPS = 60
    while run:
        k1, k2 = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEDOWN:
                    delta = change_delta(delta, -1)
                elif event.key == pygame.K_PAGEUP:
                    delta = change_delta(delta, 1)
                elif event.key == pygame.K_UP:
                    k1 = 1
                elif event.key == pygame.K_DOWN:
                    k1 = -1
                elif event.key == pygame.K_LEFT:
                    k2 = -1
                elif event.key == pygame.K_RIGHT:
                    k2 = 1
        coords = change_coords(coords, k1, k2, delta)

        params = {
            "ll": ",".join([coords[0], coords[1]]),
            "spn": ",".join([delta, delta]),
            "l": "map"
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=params)
        img = pygame.image.load(BytesIO(response.content))
        
        screen.fill((0, 0, 0))
        screen.blit(img, (0, 0))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)