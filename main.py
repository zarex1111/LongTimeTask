from needful_funcs import get_params
import pygame
import sys
from io import BytesIO
import requests


if __name__ == '__main__':

    pygame.init()

    screen = pygame.display.set_mode((600, 450))
    pygame.display.set_caption('Большая задача на Maps Api')

    run = True 

    coords = ('37.168', '56.737')  #Изменяемая часть
    delta = '0.002' #Изменяемая часть


    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

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