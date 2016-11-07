# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 2016/6/15 13:39
Latest Modified on: 

@auther: MK
"""


############################################################################
# This code defines the One Wave,
#           creates the class for Wave Record
############################################################################

class OneWave:

    def __init__(self,date_str,stk_str,start_time,end_time,start_prc,end_prc,direction,
                 wave_max_duration,wave_min_duration,wave_trend_limit):
        self.date_str = date_str
        self.stk_str = stk_str
        self.start_time = start_time
        self.end_time = end_time
        self.start_prc = start_prc
        self.end_prc = end_prc
        self.direction = direction

        self.wave_max_duration = wave_max_duration
        self.wave_min_duration = wave_min_duration
        self.wave_trend_limit = wave_trend_limit

    def is_effective(self):
        if self.end_time - self.start_time > self.wave_max_duration or self.end_time - self.start_time < self.wave_min_duration:
            return False
        if -self.wave_trend_limit < self.end_prc / self.start_prc - 1 < self.wave_trend_limit:
            return False
        return True


class WaveRecord:

    def __init__(self,date_str,stk_str):
        self.date_str = date_str
        self.stk_str = stk_str
        self.wave_list = []

    def update_wave(self,one_wave):
        assert isinstance(one_wave,OneWave)
        self.wave_list.append(one_wave)

    def __repr__(self):
        return str(self.wave_list)

