import RPi.GPIO as GPIO
import time
import sched
from datetime import date, datetime, timedelta
from suntime import Sun, SunTimeException

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)

sun_set_seconds = None
sun_rise_seconds = None

def delay_timings():
    delay_timings.s = sched.scheduler(time.time, time.sleep)
    now = datetime.now()

    run_at = now + timedelta(hours=12)
    delay_timings.delay = (run_at - now).total_seconds()


def get_sun_timings():
    current_latitude1 = 30.1979793
    current_longitude1 = 71.4724978

    print("Latitude = ", current_latitude1)
    print("Longitude = ", current_longitude1)

    get_sun_time = Sun(current_latitude1, current_longitude1)
    # current date time
    today_date = datetime.today()

    sun_rise_time = get_sun_time.get_local_sunrise_time(today_date)
    sun_set_time = get_sun_time.get_local_sunset_time(today_date)
    # sun_set_time = sun_set.strftime("%Y-%m-%d %H:%M")
    print("sun_set", sun_set_time)

    global sun_set_seconds
    global sun_rise_seconds

    sun_set_seconds = sun_set_time.timestamp()
    sun_rise_seconds = sun_rise_time.timestamp()
    print('On {} the sun at Multan   raised at {} and get down at {}.'.
          format(today_date, sun_rise_time.strftime('%H:%M'), sun_set_time.strftime('%H:%M')))


def light_on_off(time_):
    get_sun_timings()

    delay_timings.s.enter(delay_timings.delay, 1, light_on_off, (time_,))


def light_on(time_):
    if GPIO.HIGH:
        #print("On")
        GPIO.output(20, GPIO.LOW)
    delay_timings.s.enter(sun_set_seconds, 1, light_on, (time_,))


def light_off(time_):
    #if GPIO.LOW:
    print("Off")
    GPIO.output(20, GPIO.HIGH)
    delay_timings.s.enter(sun_rise_seconds, 1, light_off, (time_,))


class ARConn:
    delay_timings()
    try:
        time_ = delay_timings.s

        # Calling func for getting the sun set and rise time in seconds to set the scheduler
        get_sun_timings()

        def __init__(self, time_):
            self.time = time_

        # Scheduling sun set and rise time
        delay_timings.s.enter(delay_timings.delay, 1, light_on_off, (delay_timings.s,))
        # Scheduling light on
        delay_timings.s.enterabs(sun_set_seconds, 1, light_on, (delay_timings.s,))
        # Scheduling light off
        delay_timings.s.enterabs(sun_rise_seconds, 1, light_off, (delay_timings.s,))
        # Running scheduler
        delay_timings.s.run()
    finally:
        GPIO.cleanup()
