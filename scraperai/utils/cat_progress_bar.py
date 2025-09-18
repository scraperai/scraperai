import time
import threading
from functools import wraps
import random

from IPython.display import clear_output

expressions = {
    'normal': ' /\\_/\\  \n( o.o ) \n > ^ <\n{message}',  # Eyes open
    'blinking': ' /\\_/\\  \n( -.- ) \n > ^ <\n{message}',  # Blinking
    'happy': ' /\\_/\\  \n( ^.^ ) \n > ^ <\n{message}'  # Happy
}


def get_dots():
    dot_count = 0

    def dots():
        nonlocal dot_count
        dot_count += 1
        return '.' * (dot_count % 4)

    return dots


def animate_cat(keep_animating, text="SCRAPING", wait_time=4, blink_time=0.1, dot_interval=3):
    dotter = get_dots()
    message = ""
    while keep_animating.is_set():
        iteration = 0
        for _ in range(int(wait_time * 10 * random.random())):
            if iteration % dot_interval == 0:
                dots = dotter()
                message = f"{text}{dots}"
            clear_output(wait=True)
            print(expressions['normal'].format(message=message))
            time.sleep(blink_time)
            if not keep_animating.is_set():
                return
            iteration += 1
        if iteration % dot_interval == 0:
            dots = dotter()
            message = f"{text}{dots}"
        clear_output(wait=True)
        print(expressions['blinking'].format(message=message))
        time.sleep(blink_time)
        if not keep_animating.is_set():
            return
        iteration += 1


def cat_animation(text='LOADING'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            keep_animating = threading.Event()
            keep_animating.set()
            animation_thread = threading.Thread(target=animate_cat, args=(keep_animating, text))
            animation_thread.start()

            try:
                return func(*args, **kwargs)
            finally:
                keep_animating.clear()
                animation_thread.join()
                clear_output(wait=True)
                print(expressions['happy'].format(message=" DONE!"))  # No message for the happy expression

        return wrapper

    return decorator
