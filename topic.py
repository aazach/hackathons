import datetime


class Topic:
    def __init__(self, name: str, difficulty: int, time_spent: int, spaced_rep_time=0):
        self.name = name
        self.difficulty = difficulty
        self.time_spent = time_spent
        self.last_done = datetime.datetime.now()
        self.spaced_rep_time = spaced_rep_time

    def change_name(self, name):
        self.name = name

    def is_after_spaced_time(self):
        return self.last_done + datetime.timedelta(days=self.spaced_rep_time) <= datetime.datetime.now()

    def set_difficulty(self, diff):
        self.difficulty = diff

    def update_last_done(self):
        self.last_done = datetime.datetime.now()

    def update_spaced_rep_time(self, difficulty):
        if difficulty == 1:
            self.spaced_rep_time = (self.spaced_rep_time + 1.5)**2 + 3
        elif difficulty == 2:
            self.spaced_rep_time = (self.spaced_rep_time**1.5) + 2
        else:
            self.spaced_rep_time = 1
