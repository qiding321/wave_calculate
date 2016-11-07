# -*- coding: utf-8 -*-
"""
Created on 2016/7/4 11:15

@author: qiding
"""

import Util.Util as Util
from Data.DataFramework import DataFramework
from Data.DataInput import TickdataOneDayOneStk

import pandas as pd
import os
import datetime
import multiprocessing


def main():
    start_date = "20160501"
    # end_date = "20160505"
    # start_date = "20160506"
    # end_date = "20160510"
    # start_date = "20160511"
    # end_date = "20160515"
    # start_date = "20160516"
    # end_date = "20160520"
    # start_date = "20160521"
    # end_date = "20160525"
    # start_date = "20160526"
    # end_date = "20160530"
    # start_date = "20160531"
    end_date = "20160601"

    # start_date = "20160509"
    # end_date = "20160609"

    wave_record_path = Util.get_wave_record_path() + 'wave_ret_record\\'
    output_path = Util.get_path_output()
    file_exist = os.listdir(output_path)

    file_list = [file_name_ for file_name_ in os.listdir(wave_record_path) if start_date<=file_name_.split('.')[0].split('_')[-1]<=end_date]
    # file_list = [file_name_ for file_name_ in os.listdir(wave_record_path) if start_date<=file_name_.split('.')[0].split('_')[-1]<=end_date and file_name_ not in file_exist]

    pool = multiprocessing.Pool(processes=11)

    for wave_record_file_name in file_list:

        print(wave_record_file_name, 'start', datetime.datetime.now())
        # pool.apply_async(one_day_update, (wave_record_file_name,))
        one_day_update(wave_record_file_name)

    # pool.close()
    # pool.join()


def update_one_wave(old_wave, tick_data_one_day_one_stock):
    assert isinstance(tick_data_one_day_one_stock, TickdataOneDayOneStk)
    direction = old_wave['direction']

    start_time = Util.hms2datetime2(old_wave['start_time'])
    end_time = Util.hms2datetime2(old_wave['end_time'])

    open_time = Util.hms2datetime2(old_wave['open_time'])
    close_time = Util.hms2datetime2(old_wave['close_time'])

    # if close price < 20 than use opposite price
    if old_wave['close_prc']<=20:
        close_prc = tick_data_one_day_one_stock.data_from_csv_filter_time.loc[tick_data_one_day_one_stock.data_from_csv_filter_time.index==close_time, 'ask1' if direction==-1 else 'bid1'][0] / Util.px_multiplier  # todo
        old_wave['close_prc'] = close_prc
        old_wave['ret'] = close_prc / old_wave['open_prc'] - 1 if direction==1 else 1 - close_prc / old_wave['open_prc']

    # vol_capacity by time

    volume_direction = tick_data_one_day_one_stock.volume_buy if direction==1 else tick_data_one_day_one_stock.volume_sell  # 83 is ascii code for 'S

    time_duration = end_time - start_time
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

    old_wave['vol_capacity'] = vol_capacity
    return old_wave


def one_day_update(wave_record_file_name):
    start_date = "20160501"
    end_date = "20160601"

    wave_record_path = Util.get_wave_record_path() + 'wave_ret_record\\'
    output_path = Util.get_path_output()
    tick_data_path = Util.get_path_tickdata()
    transaction_data_path = Util.get_path_transaction_data()
    data_framework = DataFramework(start_date_str=start_date, end_date_str=end_date, path_tickdata=tick_data_path, path_transaction_data=transaction_data_path)

    output = []
    date_str = wave_record_file_name.split('.')[0].split('_')[-1]
    wave_record_one_day_all_stock = pd.read_csv(wave_record_path + wave_record_file_name)

    total_num = len(wave_record_one_day_all_stock)
    num = 0
    stock_str = ''
    for k, one_wave_row in wave_record_one_day_all_stock.iterrows():
        num += 1
        if one_wave_row['wave_tot'] == 0:
            one_wave_new = one_wave_row
        else:
            stock_str_new = str(one_wave_row['stock']).zfill(6)
            if stock_str == stock_str_new:
                pass
            else:
                stock_str = stock_str_new
                tick_data_one_day_one_stock = TickdataOneDayOneStk(date_str, stock_str, data_framework)
            one_wave_new = update_one_wave(one_wave_row, tick_data_one_day_one_stock)
        output.append(one_wave_new)
        print(date_str, one_wave_row['stock'], 'done', num/total_num, datetime.datetime.now())

    output_df = pd.DataFrame(output)
    output_df.to_csv(output_path + wave_record_file_name, index=False)
    print(output_path+wave_record_file_name, 'done')



if __name__ == '__main__':

    main()






















