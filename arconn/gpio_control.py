import os

BASE_GPIO = '/sys/class/gpio'
PATH_GPIO = os.path.join(BASE_GPIO, 'gpio{}')
GPIO_OUT_ON = 0
GPIO_OUT_OFF = 1


def _set(direction, pin_number, value):
    path = PATH_GPIO.format(pin_number)
    if os.path.exists(path):
        with open(os.path.join(path, 'direction'), 'w') as file:
            file.write(direction)
        with open(os.path.join(path, 'value'), 'w') as file:
            file.write(str(value))
        return True
    else:
        print("Path {} does not exist".format(path))
        return False


def set_out_high(pin_number):
    _set('out', pin_number, GPIO_OUT_ON)


def set_out_low(pin_number):
    _set('out', pin_number, GPIO_OUT_OFF)


def get_state(pin_number):
    path = PATH_GPIO.format(pin_number)
    with open(os.path.join(path, 'direction')) as file:
        direction = file.read().strip()
    with open(os.path.join(path, 'value')) as file:
        value = file.read().strip()

    return {
        'pin_number': pin_number,
        'direction': direction,
        'value': value,
        'value_verbose': 'on' if value == '0' else 'off'
    }


def get_states():
    def is_gpio(item):
        return item.startswith('gpio') and 'chip' not in item

    return [get_state(int(pin.replace('gpio', ''))) for pin in filter(is_gpio, os.listdir(BASE_GPIO))]
