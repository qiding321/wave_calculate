# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 16/6/16 14:24
Latest Modified on:

@auther: MK
"""

############################################################################
# This code analyzes the wave per day per stock
############################################################################

import datetime
import time
import os
import pandas as pd
import matplotlib.pyplot as plt

from Strategy.WaveRecord import *
from Strategy.WaveDefine import WaveByTick
from Data.DataInput import TickdataOneDayOneStk
from Data.DataFramework import DataFramework
import Util.Util as Util


class AnalysisOneDayOneStk:

    def __init__(self,date_str,stk_str,use_freq_stk,output_path):
        self.date_str = date_str
        self.stk_str = stk_str
        self.use_freq_stk = use_freq_stk
        self.output_path = output_path
        self.figure_path = output_path + "figure\\" + self.date_str + "\\" + self.stk_str + ".jpg"

        # self.wave_record_txt_path = output_figure_path + "wave_record.txt"

    def analyze_plot(self,data_date_stk,wave_record,paras,intraday_record):    # MK 20160621
        assert isinstance(data_date_stk,TickdataOneDayOneStk)
        assert isinstance(wave_record,WaveRecord)

        # Figure Document per Day
        if os.path.exists(self.output_path + "figure\\" + self.date_str):
            pass
        else:
            os.makedirs(self.output_path + "figure\\" + self.date_str)

        # CSV file to store the Wave Info
        if not os.path.exists(self.output_path + "figure\\" + self.date_str + "\\" + "wave_record_" + self.date_str + ".csv"):
            tmp = open(self.output_path + "figure\\" + self.date_str + "\\" + "wave_record_" + self.date_str + ".csv",'w')
            tmp.write('date,stock,wave_tot,wave_num,direction,open_time,open_prc,close_time,close_prc\n')
            tmp.close()



        prc_series = data_date_stk.px_mid_this_day_this_stk['mid_prc']
        prc_series.name = None


        try:

            #### title string for the Figure ####
            title = "Date: %s, Stock: %s" %(self.date_str,self.stk_str)
            subtitle = "Parameters {trend_limit: %.3f, breaker_ret: %.3f, breaker_time: %ds, buffer_ret: %.3f, startpoint_ret: %.3f}" \
                    % (paras['wave_trend_limit'],paras['breaker_threshold_ret'],
                       paras['breaker_threshold_time'].seconds,paras['drawback_buffer_ret'],paras['drawback_startpoint_ret'])


            #### Plot the Figure ####

            if len(prc_series) == 0:
                print(self.date_str,self.stk_str, "No Tick Data")

            else:
                # Firstly Plot the Raw Tick Data Price Pattern #
                idx_num = list(range(len(prc_series)))
                idx_time = list(prc_series.index)
                idx_time_str = list((x.strftime('%H:%M') for x in prc_series.index))

                plt.interactive(False) # Close the Interactive Mode
                plt.figure(figsize=(15,10),dpi=100)
                plt.suptitle(title,fontsize=18)
                plt.title(subtitle)
                plt.xlabel("Time",fontsize=15)
                plt.ylabel("Price",fontsize=15)


                plt.plot(idx_num, prc_series, color='b')
                plt.xticks(idx_num[::int(len(idx_num)/16)], idx_time_str[::int(len(idx_num)/16)])

                # Secondly, Plot the Effective Wave Range Pattern #
                plt.plot([],[],marker='*',color='red',label='Up Wave')
                plt.plot([],[],marker='*',color='green',label='Down Wave')
                for wave in wave_record.wave_list:  # if wave.list is empty, there's no Loop
                    assert isinstance(wave, OneWave)
                    xticks0 = idx_time.index(wave.start_time) # return the sequence number of that index value in Index
                    xticks1 = idx_time.index(wave.end_time)
                    xticks_ = list(range(xticks0, xticks1+1))
                    plt.plot(xticks0, wave.start_prc, '*')
                    plt.plot(xticks1, wave.end_prc, '*')
                    plt.plot(xticks_, prc_series[wave.start_time:wave.end_time],color=('r' if wave.direction==1 else 'g'))

                plt.grid()

                # Thirdly, Plot the Intra-day Trading Record
                if self.use_freq_stk == True:                 # MK, 20160628
                    record = intraday_record.loc[intraday_record['证券代码']==self.stk_str]
                    record = record.reset_index(drop=True)
                    if len(record) > 0:
                        plt.scatter([],[],marker='o',color='yellow',label='Sell Point')
                        plt.scatter([],[],marker='o',color='black',label='Buy Point')
                        for rows,cols in record.iterrows():
                            xticks = Util.find_next_tick(cols['委托时间'],idx_time)
                            if xticks > 0:
                                yticks = prc_series[xticks]

                                if cols["买卖"] in ("买入","证券买入"):
                                    plt.plot(xticks,yticks,'ko')
                                elif cols["买卖"] in ("卖出","证券卖出"):
                                    plt.plot(xticks,yticks,'yo')

                plt.legend(loc='upper right',shadow=True,bbox_to_anchor=(1.2,0.9))
                plt.subplots_adjust(right=0.85,left=0.1)

                # Finally, store the Figure #
                print(self.date_str,self.stk_str,' Effectve Wave Num: ', len(wave_record.wave_list))
                plt.savefig(self.figure_path,dpi=150)
                plt.close()

                # record in csv
                to_csv = open(self.output_path + "figure\\" + self.date_str + "\\" + "wave_record_" + self.date_str + ".csv",'a')
                for num,wave in enumerate(wave_record.wave_list):
                    to_append = "%s,%s,%d,%d,%d,%s,%.3f,%s,%.3f\n" % (self.date_str,self.stk_str,len(wave_record.wave_list),
                                                                   num+1,wave.direction,Util.time2hms(wave.start_time),
                                                                   wave.start_prc,Util.time2hms(wave.end_time),wave.end_prc)
                    to_csv.write(to_append)
                to_csv.close()


        except Exception as e:
            print("Analysis Part:",self.date_str,self.stk_str,str(e))

    def analyze_ret(self,data_date_stk,wave_record,paras, logger=None):
        assert isinstance(data_date_stk,TickdataOneDayOneStk)
        assert isinstance(wave_record,WaveRecord)

        # CSV file to store the Wave Ret Info
        if not os.path.exists(self.output_path + "wave_ret_record\\" + "wave_ret_" + self.date_str + ".csv"):
            tmp = open(self.output_path + "wave_ret_record\\" + "wave_ret_" + self.date_str + ".csv",'w')
            tmp.write('date,stock,wave_tot,wave_num,direction,start_time,start_prc,end_time,end_prc,open_time,open_prc,close_time,close_prc,ret,vol_capacity\n')
            tmp.close()

        prc_dataframe = data_date_stk.px_mid_this_day_this_stk
        volume_buy = data_date_stk.volume_buy
        volume_sell = data_date_stk.volume_sell
        wave_list = wave_record.wave_list

        if len(prc_dataframe) == 0:
            if logger is not None:
                logger.error(str(self.date_str) + str(self.stk_str) + 'No Tick Data')
            print(self.date_str, self.stk_str, "No Tick Data")
            return
        if len(wave_list) == 0:
            if logger is not None:
                logger.info(str(self.date_str) + str(self.stk_str) + 'No Wave Record')
            print(self.date_str, self.stk_str, "No Wave Record")
            # Append the results
            to_append =  "%s,%s,%d\n" % (self.date_str,self.stk_str,len(wave_list))
            to_csv = open(self.output_path + "wave_ret_record\\" + "wave_ret_" + self.date_str + ".csv",'a')
            to_csv.write(to_append)
            to_csv.close()
        else:
            if logger is not None:
                logger.info(str(self.date_str) + str(self.stk_str) + 'Effective Wave Num' + str(len(wave_list)))
            print(self.date_str, self.stk_str, "Effective Wave Num:", len(wave_list))
            wave_num = 1
            for wave in wave_list:
                assert isinstance(wave,OneWave)

                prc_dataframe_local = prc_dataframe.loc[(prc_dataframe.index>=wave.start_time) &
                                                        (prc_dataframe.index<=wave.end_time),:]

                # Calculate the Open and Close Price Position
                wave_ret = (wave.end_prc/wave.start_prc - 1)
                open_prc_position = wave.start_prc * (1 + wave_ret*paras['open_ret_position'])
                close_prc_position = wave.start_prc * (1 + wave_ret*paras['close_ret_position'])

                if wave.direction == 1:

                    # Time
                    open_time = prc_dataframe_local.loc[prc_dataframe_local['mid_prc']>=open_prc_position].index[0]
                    close_time = prc_dataframe_local.loc[prc_dataframe_local['mid_prc']<=close_prc_position].index[-1]
                    if open_time > close_time: # MK,20160630
                        close_time = open_time

                    # Price and Ret
                    open_prc = prc_dataframe_local.loc[prc_dataframe_local.index==open_time,"ask1"][0]
                    # close_prc = prc_dataframe_local.loc[prc_dataframe_local.index==close_time,"bid1"][0]
                    close_prc = prc_dataframe_local.loc[prc_dataframe_local.index==close_time,"mid_prc"][0]
                    if close_prc<=20:
                        close_prc = prc_dataframe_local.loc[prc_dataframe_local.index==close_time, 'bid1'][0]

                    ret = close_prc/open_prc - 1

                    # Volume
                    volume_direction = volume_buy  # 83 is ascii code for 'S

                    time_duration = datetime.timedelta(seconds=(wave.end_time - wave.start_time).total_seconds())
                    vol_start_time = open_time - time_duration * .05
                    vol_end_time = close_time + time_duration * .05
                    vol_series_local = volume_direction.loc[(volume_direction.index>=vol_start_time) &
                                                               (volume_direction.index<=vol_end_time)]  # todo qd 0701
                    if len(vol_series_local) == 0:
                        vol_capacity = 0
                    else:
                        if vol_end_time==vol_start_time:
                            vol_capacity = 0.0
                        else:
                            vol_capacity_ = vol_series_local.sum() / (vol_end_time-vol_start_time).total_seconds()
                            vol_capacity = vol_capacity_.values[0]

                elif wave.direction == -1:

                    # Time
                    open_time = prc_dataframe_local.loc[prc_dataframe_local['mid_prc']<=open_prc_position].index[0]
                    close_time = prc_dataframe_local.loc[prc_dataframe_local['mid_prc']>=close_prc_position].index[-1]
                    if open_time > close_time: # MK,20160630
                        close_time = open_time

                    # Price and Ret
                    open_prc = prc_dataframe_local.loc[prc_dataframe_local.index==open_time,"bid1"][0]
                    # close_prc = prc_dataframe_local.loc[prc_dataframe_local.index==close_time,"ask1"][0]
                    close_prc = prc_dataframe_local.loc[prc_dataframe_local.index==close_time,"mid_prc"][0]
                    if close_prc<=20:
                        close_prc = prc_dataframe_local.loc[prc_dataframe_local.index==close_time, 'ask1'][0]

                    ret = (close_prc/open_prc - 1) * (-1)

                    # Volume

                    volume_direction = volume_sell  # 83 is ascii code for 'S

                    time_duration = datetime.timedelta(seconds=(wave.end_time - wave.start_time).total_seconds())
                    vol_start_time = open_time - time_duration * .05
                    vol_end_time = close_time + time_duration * .05
                    vol_series_local = volume_direction.loc[(volume_direction.index>=vol_start_time) &
                                                               (volume_direction.index<=vol_end_time)]  # todo qd 0701
                    if len(vol_series_local) == 0:
                        vol_capacity = 0.0
                    else:
                        if vol_end_time==vol_start_time:
                            vol_capacity = 0.0
                        else:
                            vol_capacity_ = vol_series_local.sum() / (vol_end_time-vol_start_time).total_seconds()
                            vol_capacity = vol_capacity_.values[0]

                # Append the results
                to_append = "%s,%s,%d,%d,%d,%s,%.3f,%s,%.3f,%s,%.3f,%s,%.3f,%.4f,%.1f\n" % (self.date_str,self.stk_str,len(wave_list),
                                                                                            wave_num,wave.direction,Util.time2hms(wave.start_time),
                                                                                            wave.start_prc,Util.time2hms(wave.end_time),wave.end_prc,
                                                                                            Util.time2hms(open_time), open_prc,Util.time2hms(close_time),
                                                                                            close_prc,ret,vol_capacity)
                to_csv = open(self.output_path + "wave_ret_record\\" + "wave_ret_" + self.date_str + ".csv",'a')
                to_csv.write(to_append)
                to_csv.close()

                wave_num += 1


if __name__ == "__main__":

    begin=time.clock()
    tmp_date="20160603"
    tmp_code="002477"

    # Step 1:
    test_data = DataFramework(tmp_date,tmp_date,Util.get_path_tickdata())
    wave_calculation = WaveByTick(Util.set_global_paras())

    # Step 2:
    test_tickdata = TickdataOneDayOneStk(tmp_date,tmp_code,test_data)
    wave_record = wave_calculation.tick_rolling(test_tickdata)
    analysis_wave = AnalysisOneDayOneStk(tmp_date,tmp_code,False,Util.get_path_output())
    analysis_wave.analyze_plot(test_tickdata,wave_record,Util.set_global_paras(),test_data.get_intraday_record_from_csv_this_day(tmp_date,"zx600564358"))
    plt.show()
    # analysis_wave.analyze_ret(test_tickdata,wave_record,Util.set_global_paras())


    print(time.clock()-begin)









