from abc import ABCMeta
from datetime import datetime


class DatetimeParser(metaclass=ABCMeta):

    def parse(self, string):
        pass

    def getHour(self):
        pass


class AndroidDatetimeParser(DatetimeParser):

    def parse(self, string):
        try:
            year, rest = string.split('년')
        except ValueError as e:
            raise ValueError
        month, rest = rest.split('월')
        day, rest = rest.split('일')

        hourFlag, time = rest.strip().split(' ')
        hour, minute = time.split(':')
        hour = int(hour)

        if hourFlag == '오전':
            if hour == 12:
                hour = 0
        else:
            if hour < 12:
                hour += 12

        return datetime(int(year), int(month), int(day), hour, int(minute), 0)

    def getHour(self, string):
        return self.parse(string).hour


class IOSDateTimeParser(DatetimeParser):

    def parse(self, string):
        year, month, day, rest = string.split('.')

        hourFlag, time = rest.strip().split(' ')
        hour, minute = time.split(':')

        hour = int(hour)

        if hourFlag == '오전':
            if hour == 12:
                hour = 0
        else:
            if hour < 12:
                hour += 12

        return datetime(int(year), int(month), int(day), hour, int(minute), 0)

    def getHour(self, string):
        return self.parse(string).hour
