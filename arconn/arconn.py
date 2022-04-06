import time
from datetime import datetime, time

from suntime import Sun
import timesched

from arconn.gpio_control import set_out_high, set_out_low

sun_set_hours = None
sun_set_minutes = None
sun_rise_hours = None
sun_rise_minutes = None

light_scheduler = timesched.Scheduler()


def light_on():
    set_out_high(20)


def light_off():
    set_out_low(20)


def get_sun_timings():
    current_latitude1 = 30.1979793
    current_longitude1 = 71.4724978

    get_sun_time = Sun(current_latitude1, current_longitude1)
    # current date time
    today_date = datetime.today()

    sun_rise_time = get_sun_time.get_local_sunrise_time(today_date)
    sun_set_time = get_sun_time.get_local_sunset_time(today_date)
    print(sun_set_time)

    global sun_set_hours
    global sun_set_minutes
    global sun_rise_hours
    global sun_rise_minutes

    sun_set_hours = sun_set_time.strftime("%H")
    sun_set_minutes = sun_set_time.strftime("%M")
    sun_rise_hours = sun_rise_time.strftime("%I")
    sun_rise_minutes = sun_rise_time.strftime("%M")


def light_on_off():
    get_sun_timings()

    # 2nd scheduler to turn light on/off
    light_scheduler.repeat_on_days('MTWTFSs', time(sun_set_hours, sun_set_minutes), 0, light_on)
    light_scheduler.repeat_on_days('MTWTFSs', time(sun_rise_hours, sun_rise_minutes), 0, light_off)
    # run scheduler
    light_scheduler.run()


class ARConn:
    try:
        # getting  sun set and rise time in seconds to set the scheduler
        get_sun_timings()

        # Scheduling sun set and rise time
        light_scheduler.repeat_on_days('MTWTFSs', time(3, 00), 0, light_on_off)

        # Running scheduler
        light_scheduler.run()

    finally:
        print("Closed")
