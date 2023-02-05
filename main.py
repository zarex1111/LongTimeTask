import pygame
import sys
from io import BytesIO
import requests
from pygame_widgets.button import ButtonArray, Button
import pygame_widgets
from pygame_textinput.pygame_textinput import TextInputVisualizer


MAP_VALUES = ('map', 'sat', 'sat,skl')


def get_parameters(toponym, delta):

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        pass

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "l": "map"
    }
    return map_params


def switch_mode(value):
    global current_map_value
    current_map_value = value


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


def get_toponym():
    global toponym, should_search_toponym
    toponym = textinput.value
    should_search_toponym = True


if __name__ == '__main__':

    pygame.init()

    screen = pygame.display.set_mode((600, 550))
    pygame.display.set_caption('Большая задача на Maps Api')

    run = True 

    coords = ('37.168', '56.737')  #Изменяемая часть
    delta = '0.002' #Изменяемая часть

    switcher = ButtonArray(
        screen, 0, 0, 600, 50, (3, 1), 
        texts=('Схема', 'Спутник', 'Гибрид'),
        onClicks=[lambda: switch_mode(0), lambda: switch_mode(1), lambda: switch_mode(2)]
    )

    toponym = ''
    should_search_toponym = False
    font = pygame.font.Font('font.otf', 20)
    button_font = pygame.font.Font(None, 13)
    textinput = TextInputVisualizer(font_object=font)
    search_button = Button(screen, 550, 500, 50, 50, font=button_font, onClick=lambda: get_toponym(), text='Поиск')

    marks = []

    FPS = 60
    current_map_value = 0
    while run:
        k1, k2 = 0, 0
        events = pygame.event.get()
        for event in events:
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

        textinput.update(events)

        if should_search_toponym and toponym != '':
            params = get_parameters(toponym, delta)
            params['pt'] = params['ll'] + ',ya_ru'
            should_search_toponym = False
            delta = params['spn'].split(',')[0]
            coords = params['ll'].split(',')
            marks = [coords]

        params = {
            "ll": ",".join([coords[0], coords[1]]),
            "spn": ",".join([delta, delta]),
            "l": MAP_VALUES[current_map_value],
            'pt': ''
        }
        for mark in marks:
            params['pt'] = ','.join(mark) + ',ya_ru'
            if len(marks) > 1:
                params['pt'] += '&'
        if len(params['pt']) == 0:
            params.pop('pt')

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=params)
        img = pygame.image.load(BytesIO(response.content))

        screen.fill((255, 255, 255))
        screen.blit(img, (0, 50))
        
        screen.blit(textinput.surface, (0, 510))
        pygame_widgets.update(events)
        pygame.display.update()
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)