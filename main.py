import pygame
import sys
from io import BytesIO
import requests
from pygame_widgets.button import ButtonArray, Button
from pygame_widgets.toggle import Toggle
import pygame_widgets
from pygame_textinput.pygame_textinput import TextInputVisualizer
import math


MAP_VALUES = ('map', 'sat', 'sat,skl')


def format_text_block(frame_width, frame_height, text):
    text += '\n'
    data = list(map(lambda x: x + '\n', text.split('\n')))
    rows = frame_height
    width = frame_width
    data = data[:rows]

    text = ''

    while rows > 0 and len(data) > 0:
        if len(data[0]) > width and data[0][width] != '\n':
            text += data[0][:width] + '\n'
            data[0] = data[0][width:]
            rows -= 1
        else:
            text += data.pop(0)
            rows -= 1
    if len(text.split('\n')) > rows:
        if text[-1] == '\n':
                text = text[:-1]
    return text


def get_parameters(toponym, delta):

    global side_text, post_code

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        pass

    json_response = response.json()
    side_text = json_response['response']["GeoObjectCollection"]["featureMember"][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
    try:
        post_code = json_response['response']["GeoObjectCollection"]["featureMember"][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
    except Exception:
        post_code = ''
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


def clear_marks():
    global marks, side_text, post_code
    marks = []
    side_text = '???????? ???????????? ???? ??????????????'
    post_code = ''


def calculate_coords(pos, middle_point, delta):
    zero_x, zero_y = map(float, middle_point)
    angle_x = zero_x - float(delta) / 2
    angle_y = zero_y - float(delta) / 2

    angle_x += float(pos[0]) * float(delta) / 600
    angle_y += float(pos[1] - 50) * math.cos(math.radians(float(delta))) / 450
    return (str(round(angle_x, 6)), str(round(angle_y, 6)))


if __name__ == '__main__':

    pygame.init()

    screen = pygame.display.set_mode((900, 575))
    pygame.display.set_caption('?????????????? ???????????? ???? Maps Api')

    run = True 

    coords = ('37.168', '56.737')  #???????????????????? ??????????
    delta = '0.002' #???????????????????? ??????????

    switcher = ButtonArray(
        screen, 0, 0, 600, 50, (3, 1), 
        texts=('??????????', '??????????????', '????????????'),
        onClicks=[lambda: switch_mode(0), lambda: switch_mode(1), lambda: switch_mode(2)]
    )

    toponym = ''
    should_search_toponym = False
    font = pygame.font.Font('font.otf', 20)
    button_font = pygame.font.Font(None, 13)
    textinput = TextInputVisualizer(font_object=font)
    search_button = Button(screen, 550, 500, 50, 50, font=button_font, onClick=lambda: get_toponym(), text='??????????')

    marks = []

    clear_marks_button = Button(screen, 0, 550, 600, 25, font=font, onClick=lambda: clear_marks(), text='?????????????? ???????????????????? ????????????????????')

    side_text = '???????? ???????????? ???? ??????????????'

    post_code = ''
    should_show_post_code = False
    postal_code_toggle = Toggle(screen, 650, 540, 200, 25, startOn=True)
    toggle_label_font = pygame.font.Font(None, 20)
    postal_code_text = toggle_label_font.render('?????????????????????????? ??????????????', True, (0, 0, 0))

    point_coords = None

    FPS = 100
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if 0 <= event.pos[0] <= 600 and 50 <= event.pos[1] <= 500:
                        point_coords = calculate_coords(event.pos, coords, delta)
        coords = change_coords(coords, k1, k2, delta)

        textinput.update(events)

        if should_search_toponym and toponym != '':
            params = get_parameters(toponym, delta)
            params['pt'] = params['ll'] + ',ya_ru'
            delta = params['spn'].split(',')[0]
            coords = params['ll'].split(',')
            marks = [coords]
            should_search_toponym = False

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
        if point_coords is not None:
            params['pt'] = ','.join(point_coords) + ',ya_ru'
        if len(params['pt']) == 0:
            params.pop('pt')

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=params)
        img = pygame.image.load(BytesIO(response.content))

        side_text = format_text_block(30, 29, side_text)
        while side_text[-1] == '\n':
            side_text = side_text[:-1]
        text_rows = []
        full_adress_font = pygame.font.Font(None, 20)
        for row in side_text.split('\n'):
            textbox = full_adress_font.render(row, True, (0, 0, 0))
            text_rows.append(textbox)

        if postal_code_toggle.getValue() and post_code != '':
            text_rows.append(full_adress_font.render(f'???????????????? ????????????: {post_code}', True, (0, 0, 0)))

        screen.fill((255, 255, 255))
        screen.blit(img, (0, 50))
        
        screen.blit(textinput.surface, (15, 510))

        for i in range(len(text_rows)):
            screen.blit(text_rows[i], (615, 25 + i * 30))

        screen.blit(postal_code_text, (650, 520))

        pygame_widgets.update(events)
        pygame.display.update()
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)