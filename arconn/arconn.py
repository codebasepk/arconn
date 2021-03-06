import asyncio
from asyncio import sleep, Task
from datetime import datetime

from autobahn.twisted.wamp import ApplicationSession
from suntime import Sun

from arconn.gpio_control import set_out_high, set_out_low


class Setter:
    def __init__(self) -> None:
        super().__init__()
        self.task: Task = None
        self.task_type: str = None

    async def call_with_delay(self, delay_seconds, callback):
        await asyncio.sleep(delay_seconds)
        await callback()

    async def light_on(self):
        """function from gpio_control module to turn light on
        """
        await self.cancel()

        set_out_high(20)

    async def light_off(self):
        """function from gpio_control module to turn light off
        """
        await self.cancel()

        set_out_low(20)

    async def set_on_at(self, delay_seconds):
        """set_on_at function get called by client device to turns
        'light-on' at specific time, received from client device
        """

        await self.cancel()
        cur_time = datetime.now()
        cur_time_in_sec = cur_time.timestamp()
        set_delay_seconds = delay_seconds - cur_time_in_sec

        self.task = asyncio.create_task(self.call_with_delay(set_delay_seconds, self.light_on))
        self.task_type = "on"
        await self.task

    def run_set_on(self, delay_seconds):
        asyncio.run(self.set_on_at(delay_seconds))

    async def set_off_at(self, delay_seconds):
        """set_on_at function get called by client device
            to schedule the specific time to turns 'light-off',
            received from client device
            """

        await self.cancel()
        cur_time = datetime.now()
        cur_time_in_sec = cur_time.timestamp()
        set_delay_seconds = delay_seconds - cur_time_in_sec

        self.task = asyncio.create_task(self.call_with_delay(set_delay_seconds, self.light_off))
        self.task_type = "off"
        await self.task

    def run_set_off(self, delay_seconds):
        asyncio.run(self.set_off_at(delay_seconds))

    def is_set(self):
        return self.task is not None and not self.task.done()

    def current_state(self):
        return self.task_type

    async def cancel(self):
        self.task_type = None
        if self.is_set():
            await asyncio.sleep(0)
            self.task.cancel("manual override")


class ARConn(ApplicationSession):

    def __init__(self, config=None):
        super().__init__(config)
        self.current_latitude = 30.1979793
        self.current_longitude = 71.4724978
        self.task = None
        self.setter = Setter()

    def get_sun_times(self):
        """get_sun_time function gets the sun set and rise time
        every time using suntime library when it's being called
        from start function for creating asyncio task
        """

        # suntime library to get the sun timing according to current location
        get_sun_time = Sun(self.current_latitude, self.current_longitude)

        # current date time
        today_date = datetime.today()

        # methods to get the
        sun_rise_time = get_sun_time.get_local_sunrise_time(today_date)
        sun_set_time = get_sun_time.get_local_sunset_time(today_date)

        sun_rise_seconds = sun_rise_time.timestamp()
        sun_set_seconds = sun_set_time.timestamp()

        return sun_set_seconds, sun_rise_seconds

    async def set_sun_time(self):
        sun_set_seconds, sun_rise_seconds = self.get_sun_times()

        # calling function light_on_off to pass the sun set and rise time in seconds as arguments
        await self.light_on_off(sun_set_seconds, sun_rise_seconds)

    async def light_on_off(self, set_seconds, rise_seconds):
        """light_on_off function getting the sun set and rise time in seconds
        from set_sun_time function to manage the tasks to turn light on and
        off on a specific time according to current time
        """

        cur_time = datetime.now()
        cur_time_in_sec = cur_time.timestamp()

        if set_seconds <= cur_time_in_sec <= rise_seconds:
            # this condition will check that if current time greater than sun-set-time and less than sun-rise-time
            # then it will set the time to turn light off
            rise_remaining_time = rise_seconds - cur_time_in_sec
            light_off_task = asyncio.create_task(self.scheduling_day_sec(rise_remaining_time, self.setter.light_off))
            await light_off_task
        elif rise_seconds <= cur_time_in_sec >= set_seconds:
            # this condition will check that if current time less than sun-set-time and greater than sun-rise-time
            # then it will set the time to turn light on
            set_remaining_time = set_seconds - cur_time_in_sec
            light_on_task = asyncio.create_task(self.scheduling_day_sec(set_remaining_time, self.setter.light_on))
            await light_on_task

    @staticmethod
    async def scheduling_day_sec(timeout, set_sun_time):
        await sleep(timeout)
        await set_sun_time()

    async def start(self, set_task):
        # run self.set_sun_time() function first time when asyncio start
        # to check the current state according to current time
        await self.set_sun_time()

        try:
            while set_task:
                self.task = asyncio.create_task(self.scheduling_day_sec(43200, self.set_sun_time))
                await self.task
        finally:
            print("Cancelled")
            # main task get cancelled ss set_task variable set 'False'
            # for cancelling the task it will receive 'false' argument from client device
            self.cancel_main_task()

    def is_set(self):
        return self.task is not None and not self.task.done()

    def cancel_main_task(self):
        if self.is_set():
            self.task.cancel()

    # Autobahn connection
    async def onJoin(self, details):
        """onJoin is an autobahn async function registering procedures
        for calling them from client device to perform the specific tasks
        """

        reg = await self.register(self.start, "pk.codebase.sys.automatically_on_off")
        self.log.info("Registered procedure {procedure}", procedure=reg.procedure)
        reg = await self.register(self.setter.light_on, "pk.codebase.sys.light_on")
        self.log.info("Registered procedure {procedure}", procedure=reg.procedure)
        reg = await self.register(self.setter.light_off, "pk.codebase.sys.light_off")
        self.log.info("Registered procedure {procedure}", procedure=reg.procedure)
        reg = await self.register(self.setter.run_set_on, "pk.codebase.sys.set_on_at")
        self.log.info("Registered procedure {procedure}", procedure=reg.procedure)
        reg = await self.register(self.setter.run_set_off, "pk.codebase.sys.set_off_at")
        self.log.info("Registered procedure {procedure}", procedure=reg.procedure)
