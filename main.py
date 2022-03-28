import RPi.GPIO as GPIO
import time
import sched
from datetime import date, datetime, timedelta
from suntime import Sun, SunTimeException

GPIO.setmode(GPIO.BCM)

GPIO.setup(20, GPIO.OUT)
GPIO.output(20, GPIO.HIGH)


try:
    now = datetime.now()

    run_at = now + timedelta(seconds=30)
    delay = (run_at - now).total_seconds()

    print(delay)
    print(run_at)

    s = sched.scheduler(time.time, time.sleep)


    def light_on_off(time_):
        current_latitude1 = 30.1979793
        current_longitude1 = 71.4724978

        print("Latitude = ", current_latitude1)
        print("Longitude = ", current_longitude1)

        get_sun_time = Sun(current_latitude1, current_longitude1)

        today_date = date.today()

        sun_rise_time = get_sun_time.get_local_sunrise_time(today_date)
        sun_set = get_sun_time.get_local_sunset_time(today_date)
        sun_set_time = sun_set.strftime("%Y-%m-%d %H:%M")
        print("sun_set", sun_set_time)

        print('On {} the sun at Multan   raised at {} and get down at {}.'.
              format(today_date, sun_rise_time.strftime('%H:%M'), sun_set.strftime('%H:%M')))

        current_time = datetime.now()
        current_time_24 = current_time.strftime("%Y-%m-%d %H:%M")
        print("Curr", current_time)
        current_time_12 = current_time.strftime("%Y-%m-%d %I:%M")

        if current_time_12 == sun_rise_time:
            GPIO.output(20, GPIO.HIGH)
        elif current_time_24 == sun_set_time:
            GPIO.output(20, GPIO.LOW)

        s.enter(delay, 1, light_on_off, (time_,))


    s.enter(delay, 1, light_on_off, (s,))
    s.run()
finally:
    GPIO.cleanup()
