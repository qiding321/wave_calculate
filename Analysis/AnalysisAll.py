
# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 16/6/17 16:46
Latest Modified on: 

@auther: MK
"""

############################################################################
# This code analyzes the wave all days all stocks
############################################################################

import datetime
import time
import os
import pandas as pd


from Strategy.WaveRecord import *
from Strategy.WaveDefine import WaveByTick
from Data.DataInput import TickdataOneDayOneStk
from Data.DataFramework import DataFramework
from Analysis.AnalysisOneDayOneStk import AnalysisOneDayOneStk
import Util.Util as Util


class AnalysisAll:

    def __init__(self,data_framework,define_wave):
        assert isinstance(data_framework,DataFramework)
        assert isinstance(define_wave,WaveByTick)

        self.data_framework = data_framework
        self.define_wave = define_wave

    def loop_date_stk_plot(self,use_freq_stk,output_path,logger=None):

        self.data_framework.update_date_list()

        for one_date in self.data_framework.date_list:

            self.data_framework.update_stk_list(date_str=one_date,use_freq_stk=use_freq_stk)

            intraday_record = self.data_framework.get_intraday_record_from_csv_this_day(one_date)
            for one_stk in self.data_framework.stk_list:

                time_begin = time.clock()

                # DATA is ready #
                data_date_stk = TickdataOneDayOneStk(one_date,one_stk,self.data_framework)

                wave_record = self.define_wave.tick_rolling(data_date_stk)
                assert isinstance(wave_record,WaveRecord)

                analysis_wave = AnalysisOneDayOneStk(data_date_stk.date_str,data_date_stk.stk_str,use_freq_stk,output_path)
                analysis_wave.analyze_plot(data_date_stk,wave_record,self.define_wave.paras,intraday_record)
                analysis_wave.analyze_ret(data_date_stk, wave_record, self.define_wave.paras, logger=logger)

                # print("Processed", one_date, one_stk,time.clock()-time_begin)
                # print("=====================================================")

    def loop_date_stk_calret(self, use_freq_stk, output_path, logger=None):

        self.data_framework.update_date_list()

        for one_date in self.data_framework.date_list:

            self.data_framework.update_stk_list(date_str=one_date,use_freq_stk=use_freq_stk)

            for one_stk in self.data_framework.stk_list:

                # begin = time.clock()
                try:
                    # DATA is ready #
                    data_date_stk = TickdataOneDayOneStk(one_date,one_stk,self.data_framework)

                    wave_record = self.define_wave.tick_rolling(data_date_stk)
                    assert isinstance(wave_record,WaveRecord)

                    analysis_wave = AnalysisOneDayOneStk(data_date_stk.date_str,data_date_stk.stk_str,use_freq_stk,output_path)
                    analysis_wave.analyze_ret(data_date_stk, wave_record, self.define_wave.paras, logger=logger)

                except Exception as e:
                    print('============================Error:', one_date, one_stk, e, '=========================')
                    logger.error('Error:' + str(one_date) + str(one_stk) + str(e))
                # print(time.clock()-begin)


if __name__ == "__main__":

    # begin=time.clock()

    # Step 1:
    test_data = DataFramework("20160620","20160620",Util.get_path_tickdata())
    wave_calculation = WaveByTick(Util.set_global_paras())
    record = test_data.get_intraday_record_from_csv_this_day("20160620","zx600564358")

    # Step 2:
    analysis = AnalysisAll(test_data,wave_calculation)
    analysis.loop_date_stk_plot(True,Util.get_path_output())

    # print(time.clock()-begin)




