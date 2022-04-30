from datetime import datetime
from suntime import Sun
from autobahn.twisted.wamp import ApplicationSession
from arconn.gpio_control import set_out_high, set_out_low
import asyncio


class ARConn(ApplicationSession):

    def __init__(self, config=None):
        super().__init__(config)
        self.current_latitude = 30.1979793
        self.current_longitude = 71.4724978
        self.wamp_publish = False

    @staticmethod
    async def light_on():
        """function from gpio_control module to turn light on"""
        print("light on")
        set_out_high(20)

    @staticmethod
    async def light_off():
        """function from gpio_control module to turn light off"""
        print("light off")
        set_out_low(20)

    # Autobahn connection
    async def onJoin(self, details):
        # 1. subscribe to a topic so we receive events
        async def on_event(msg):
            print(details)
            self.wamp_publish = False
            print(self.wamp_publish)
            print("Got event: {}".format(msg))
            if msg == "on":
                await self.light_on()
            elif msg == "off":
                await self.light_off()

        await self.subscribe(on_event, 'org.codebase')
        print("subscribed")

    async def get_sun_time(self):
        """get_sun_time function gets the sun set and rise time every time using suntime library
        when it's being called from start function for creating asyncio task"""
        # suntime library to get the sun timing according to current location
        get_sun_time = Sun(self.current_latitude, self.current_longitude)

        # current date time
        today_date = datetime.today()

        # methods to get the
        sun_rise_time = get_sun_time.get_local_sunrise_time(today_date)
        sun_set_time = get_sun_time.get_local_sunset_time(today_date)

        print(sun_rise_time)
        sun_rise_seconds = sun_rise_time.timestamp()
        sun_set_seconds = sun_set_time.timestamp()

        # calling function light_on_off to pass the sun set and rise time in seconds as arguments
        await self.light_on_off(sun_set_seconds, sun_rise_seconds)

    async def light_on_off(self, set_seconds, rise_seconds):
        """light_on_off function getting the sun set and rise time in seconds from get_sun_time function
        to manage the tasks to turn light on and off on a specific time according to current time"""
        cur_time = datetime.now()
        cur_time_in_sec = cur_time.timestamp()

        rise_remaining_time = rise_seconds - cur_time_in_sec
        set_remaining_time = set_seconds - cur_time_in_sec

        if self.wamp_publish:
            if set_seconds <= cur_time_in_sec >= rise_seconds:
                light_on_task = asyncio.create_task(self.scheduling_day_sec(set_remaining_time, self.light_on))
                await light_on_task
            elif rise_seconds <= cur_time_in_sec <= set_seconds:
                light_off_task = asyncio.create_task(self.scheduling_day_sec(rise_remaining_time, self.light_off))
                await light_off_task

    @staticmethod
    async def scheduling_day_sec(timeout, get_sun_time):
        await asyncio.sleep(timeout)
        await get_sun_time()

    async def start(self):

        try:
            while True:
                task = asyncio.create_task(self.scheduling_day_sec(10, self.get_sun_time))
                self.wamp_publish = True
                await task

        finally:
            print("Closed")
