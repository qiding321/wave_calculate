# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 2016/6/15 14:06
Latest Modified on: 

@auther: MK
"""

############################################################################
# This code defines the Wave Calculation
############################################################################

import datetime
import time
import pandas as pd

from Data.DataFramework import DataFramework
from Data.DataInput import TickdataOneDayOneStk
from Strategy.WaveRecord import *
import Util.Util as Util

# pd.options.display.width = 1000
# pd.set_option('display.max_rows',100)
# pd.set_option('display.max_columns',100)


class WaveByTick:

    def __init__(self,paras):
        assert isinstance(paras,dict)
        self.paras = paras
        self.wave_max_duration = paras['wave_max_duration']
        self.wave_min_duration = paras['wave_min_duration']
        self.wave_trend_limit = paras['wave_trend_limit']

        self.breaker_threshold_ret = paras['breaker_threshold_ret']
        self.breaker_threshold_time = paras['breaker_threshold_time']
        self.drawback_buffer_ret = paras['drawback_buffer_ret']
        self.drawback_startpoint_ret = paras['drawback_startpoint_ret']

        self.effective_begin_min = paras['effective_begin_min']
        self.effective_begin_max = paras['effective_begin_max']

    def tick_rolling(self,data_date_stk):
        assert isinstance(data_date_stk,TickdataOneDayOneStk)
        date_str = data_date_stk.date_str
        stk_str = data_date_stk.stk_str

        ## Wave Record Initiate
        wave_record_date_stk = WaveRecord(date_str=date_str,stk_str=stk_str)

        ## Morning Wave ##
        prc_series_am = data_date_stk.px_mid_this_day_this_stk['mid_prc'].select(Util.in_morning_time)

        idx_num = 0
        while idx_num < len(prc_series_am.index):

            idx = prc_series_am.index[idx_num]   # 20160622,MK: Only Calculate Wave within 9:31:00 and 14:52:00
            if idx >= Util.hms2datetime(self.effective_begin_min) and idx <= Util.hms2datetime(self.effective_begin_max):

                this_wave = self.cal_wave_from_any_tick(idx_num_now=idx_num,prc_series=prc_series_am,
                                                        date_str=date_str,stk_str=stk_str)
                if this_wave is not None:
                    assert isinstance(this_wave,OneWave)
                    wave_record_date_stk.update_wave(this_wave)

                    # If wave is effective, then skip to the End Tick
                    time_end_this_wave = this_wave.end_time
                    idx_num =list(prc_series_am.index).index(time_end_this_wave)
                else:
                    idx_num += 1
            else:
                idx_num += 1

        ## After Wave ##
        prc_series_pm = data_date_stk.px_mid_this_day_this_stk['mid_prc'].select(Util.in_afternoon_time)

        idx_num = 0
        while idx_num < len(prc_series_pm.index):

            idx = prc_series_pm.index[idx_num]   # 20160622,MK: Only Calculate Wave within 9:31:00 and 14:52:00
            if idx >= Util.hms2datetime(self.effective_begin_min) and idx <= Util.hms2datetime(self.effective_begin_max):

                this_wave = self.cal_wave_from_any_tick(idx_num_now=idx_num,prc_series=prc_series_pm,
                                                        date_str=date_str,stk_str=stk_str)
                if this_wave is not None:
                    assert isinstance(this_wave,OneWave)
                    wave_record_date_stk.update_wave(this_wave)

                    # If wave is effective, then skip to the End Tick
                    time_end_this_wave = this_wave.end_time
                    idx_num =list(prc_series_pm.index).index(time_end_this_wave)
                else:
                    idx_num += 1
            else:
                idx_num += 1

            # this_wave = self.cal_wave_from_any_tick(idx_num_now=idx_num,prc_series=prc_series_pm,
            #                                         date_str=date_str,stk_str=stk_str)
            # if this_wave is not None:
            #     assert isinstance(this_wave,OneWave)
            #     wave_record_date_stk.update_wave(this_wave)
            #
            #     # If wave is effective, then skip to the End Tick
            #     time_end_this_wave = this_wave.end_time
            #     idx_num =list(prc_series_pm.index).index(time_end_this_wave)
            # else:
            #     idx_num += 1

        return wave_record_date_stk



    ## Calculate Wave from any point: Return (None or OneWave)
    def cal_wave_from_any_tick(self,idx_num_now,prc_series,date_str,stk_str):
        if idx_num_now >= len(prc_series.index) - 1:
            return None
        time_now = prc_series.index[idx_num_now]
        prc_now = prc_series.iloc[idx_num_now]
        prc_next = prc_series.iloc[idx_num_now + 1]
        direction = 1 if prc_next>prc_now else (0 if prc_next==prc_now else -1)

        if direction == 0:
            return None

        idx_num_moving = idx_num_now + 1
        while True:
            # Return None, NO Observation
            if idx_num_moving >= len(prc_series.index):
                return None

            # Time Gap>5min
            time_moving = prc_series.index[idx_num_moving]

            if time_moving - time_now > self.wave_max_duration:   # Revised 2016.06.16
                # break  # Original condition, if lasts more than 5min, then whole wave is ineffective

                prc_range = prc_series[idx_num_now:idx_num_moving]   # Delete the lastest point
                # Store the Peak point
                prc_end = prc_range.max() if direction==1 else prc_range.min()
                time_end = prc_range.idxmax() if direction==1 else prc_range.idxmin()

                # Store the Wave if effective
                wave = OneWave(date_str=date_str,stk_str=stk_str,start_time=time_now,end_time=time_end,
                               start_prc=prc_now,end_prc=prc_end,direction=direction,wave_trend_limit=self.wave_trend_limit,
                               wave_max_duration=self.wave_max_duration,wave_min_duration=self.wave_min_duration)
                if wave.is_effective() == True:
                    return wave ##################### Most Important Output ################
                else:
                    return None


            # Wave Breaker
            prc_range = prc_series[idx_num_now:idx_num_moving+1]
            breaker_flag = self.is_breaker_tick(prc_series_range=prc_range,direction=direction)
            if breaker_flag == True:
                # Store the Peak point
                prc_end = prc_range.max() if direction==1 else prc_range.min()
                time_end = prc_range.idxmax() if direction==1 else prc_range.idxmin()

                # Store the Wave if effective
                wave = OneWave(date_str=date_str,stk_str=stk_str,start_time=time_now,end_time=time_end,
                               start_prc=prc_now,end_prc=prc_end,direction=direction,wave_trend_limit=self.wave_trend_limit,
                               wave_max_duration=self.wave_max_duration,wave_min_duration=self.wave_min_duration)
                if wave.is_effective() == True:
                    return wave ##################### Most Important Output ################
                else:
                    return None
            idx_num_moving += 1
        return None

    def is_breaker_tick(self,prc_series_range,direction):
        breaker_threshold_ret = self.breaker_threshold_ret
        breaker_threshold_time = self.breaker_threshold_time
        drawback_buffer_ret = self.drawback_buffer_ret
        drawback_startpoint_ret = self.drawback_startpoint_ret

        if direction == 1:
            if prc_series_range.iloc[-1]/prc_series_range.iloc[0] - 1 < -drawback_startpoint_ret: # MK, 20160622, draw down >0.1% from start-point
                return True
            if prc_series_range.iloc[-1]/prc_series_range.max() - 1 < -breaker_threshold_ret: # draw down >0.2%
                return True
            if prc_series_range.index[-1] - prc_series_range.idxmax() > breaker_threshold_time:
                if prc_series_range.iloc[-1]/prc_series_range.max() - 1 < -drawback_buffer_ret:  ##### Whether to setup immune ret 0.001
                    return True
                # return True
        elif direction == -1:
            if prc_series_range.iloc[-1]/prc_series_range.iloc[0] - 1 > drawback_startpoint_ret: # MK, 20160622
                return True
            if prc_series_range.iloc[-1]/prc_series_range.min() - 1 > breaker_threshold_ret: # draw down >0.2%
                return True
            if prc_series_range.index[-1] - prc_series_range.idxmin() > breaker_threshold_time:
                if prc_series_range.iloc[-1]/prc_series_range.min() - 1 > drawback_buffer_ret:
                    return True
                # return True

        return False



if __name__ == "__main__":

    begin=time.clock()

    test_data = DataFramework("20160620","20160620",Util.get_path_tickdata())
    test_tickdata = TickdataOneDayOneStk("20160620","000166",test_data)

    wave_calculation = WaveByTick(Util.set_global_paras())
    wave_record = wave_calculation.tick_rolling(test_tickdata)

    print(time.clock()-begin)