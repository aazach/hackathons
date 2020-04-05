#importing libraries for inegration with google calendar
from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

#defining crucial variables/constants
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
GCAL = discovery.build('calendar', 'v3', http=creds.authorize(Http()))


from . import category
from . import topic
from . import timeblock
import datetime


class Calendar:
    def __init__(self):
        self.events = []
        self.start_time = datetime.datetime.now().replace(hour=12, minute=00)
        self.end_time = datetime.datetime.now().replace(hour=18, minute=00)
        self.block_duration = 25
        self.categories = {}

    def set_time_range(self, start, end):
        self.start_time = start
        self.end_time = end

    def set_block_duration(self, duration):
        self.block_duration = duration

    def add_category(self, c: category.Category, time_to_spend: int):
        self.categories[c] = time_to_spend
            
    def get_block_time_division_coefficient(self, tpc: topic.Topic):
        time = tpc.time_spent
        if time > self.block_duration:
            return time / self.block_duration
        else:
            return 1

    def get_daily_division_coefficient(self, n_days):
        learning_time = sum(self.categories.values())
        time_daily = round(learning_time / n_days, 2)
        return time_daily

    @staticmethod
    def create_time_block(duration, c: category.Category, t=None, info=None):
        if info:
            if t:
                name = info + c.name + ' / ' + t.name
            else:
                name = info + c.name
        else:
            if t:
                name = c.name + ' / ' + t.name
            else:
                name = c.name
        return timeblock.TimeBlock(name, duration)

    def divide_topic(self, c: category.Category, t: topic.Topic, div_coef):
        
        small_segment = []
        while div_coef > 0:
            if div_coef >= 1:
                tb = self.create_time_block(self.block_duration, c, t)
                small_segment.append(tb)
                div_coef -= 1
            else:
                tb = self.create_time_block(self.block_duration * div_coef, c, t, "!SHORT! ")
                small_segment.append(tb)
                div_coef -= div_coef
        return small_segment

    def create_segment(self):
        segment = []
        for c, duration in zip(self.categories.keys(), self.categories.values()):
            topics = c.get_topics(duration)
            for t in topics:
                coef = self.get_block_time_division_coefficient(t)
                small_segment = self.divide_topic(c, t, coef)
                segment.extend(small_segment)
        return segment

    def create(self, n_days):
        segment = self.create_segment()

        time_daily = self.get_daily_division_coefficient(n_days)
        today = self.start_time

        cnt = 0

        time_ptr = today
        time_spent = 0
        for seg in segment:
            time_spent += seg.duration
            if time_spent < time_daily and (time_ptr + datetime.timedelta(minutes=seg.duration)).hour < self.end_time.hour:
                seg.set_time_range(time_ptr)
                time_ptr += datetime.timedelta(minutes=seg.duration)
                self.events.append(seg)
                cnt += 1
                if seg != segment[-1] and time_spent + self.block_duration < time_daily:
                    if cnt % 3 == 0:
                        tb = timeblock.TimeBlock("Long Break", 30)
                        tb.set_time_range(time_ptr)
                        time_ptr += datetime.timedelta(minutes=30)
                        self.events.append(tb)
                    else:
                        tb = timeblock.TimeBlock("Short Break")
                        tb.set_time_range(time_ptr)
                        time_ptr += datetime.timedelta(minutes=5)
                        self.events.append(tb)
            else:
                today += datetime.timedelta(days=1)
                time_spent = 0
                time_ptr = today
                cnt = 0
                
#Ads an event to the google calendar
    def add_to_google(self):
        for event in self.events:
            EVENT = event.to_google_calendar()
            e = GCAL.events().insert(calendarId='primary', sendNotifications=True, body=EVENT).execute()
            print('''*** %r event added:
            Start: %s
            End:   %s''' % (e['summary'].encode('utf-8'),
                e['start']['dateTime'], e['end']['dateTime']))
