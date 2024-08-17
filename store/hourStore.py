from datetime import datetime


class HourStore:
    currentTime = ""
    response_hour = 0
    response_minute = 0
    response_meridian = ""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(HourStore, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def get_instance():
        if HourStore.instance is None:
            HourStore.instance = HourStore()
        return HourStore.instance

    def set_current_time(self, time):
        self.currentTime = time

    def get_current_time(self):
        return self.currentTime

    def set_response_hour(self, hour):
        self.response_hour = hour

    def get_response_hour(self):
        return self.response_hour

    def set_response_minute(self, minute):
        self.response_minute = minute

    def get_response_minute(self):
        return self.response_minute

    def set_response_meridian(self, meridian):
        self.response_meridian = meridian

    def get_response_meridian(self):
        return self.response_meridian

    def get_time(self):
        hour = self.get_response_hour()
        minute = self.get_response_minute()
        meridian = self.get_response_meridian()

        # Convert to 24-hour format
        if meridian.lower() == "pm" and hour != 12:
            hour += 12
        elif meridian.lower() == "am" and hour == 12:
            hour = 0

        # Create a datetime object for the current date with the specified time
        now = datetime.now()
        specified_time = datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute,
                                  second=now.second)

        # Format date and time as requested
        formatted_date = specified_time.strftime("%b %d %Y")
        formatted_time = specified_time.strftime("%H:%M:%S")

        # Return the formatted date and time in a dictionary
        return {
            "date": formatted_date,
            "time": formatted_time
        }
