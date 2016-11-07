# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 2016/6/15 9:50
Latest Modified on: 

@auther: MK
"""

##################################################################################
# This Code creates the frequently used function and global parameters
##################################################################################
import os
import datetime
import pandas as pd

px_multiplier = 10000

mkt_open_time_morning_str = '93000'
mkt_close_time_morning_str = '113000'
mkt_open_time_afternoon_str = '130000'
mkt_close_time_afternoon_str = '150000'

import socket

name = socket.gethostname()

if name == '2013-20151201LG':
    path_root = 'F:\\IntradayTeamPerformanceAnalysis\\'
    intraday_team_return_path = path_root + 'intraday_team_return.csv'

    raw_data_path_root = '\\\\2013-20151109CR\\StockTick\\'
    output_path = 'F:\\IntradayTeamPerformanceAnalysis\\'
else:
    path_root = 'C:\\Users\\dqi\\Documents\\Data\\WaveCalculateResult\\'
    intraday_team_return_path = path_root + 'intraday_team_return.csv'

    raw_data_path_root = '\\\\2013-20151109CR\\StockTick\\'
    output_path = 'C:\\Users\\dqi\\Documents\\Output\\WaveCalculateResult\\'


def get_path_tickdata():
    # return r"E:\Mingshi\DATA\StcokTick_3s\Tick\\"
    return raw_data_path_root + 'Tick\\'
    # return 'I:\\IntradayData3Seconds\\'
    # return r'Y:\Project Data\Mingshi\MS_Program\Retrace_Program\Strategy\8_201604_IntraDay\Strategy\3_Wave_Define\tick_sample\\'


def get_log_path():
    return output_path + 'LogMultiprocess.log'


def get_path_transaction_data():
    return raw_data_path_root + 'Transaction\\'
    # return 'I:\\IntradayDataTransaction\\'


def get_path_intraday_record():
    return r"E:\Mingshi\MS_Program\Retrace_Program\Strategy\8_201604_IntraDay\data\Chen_Trading_Record\\"


def get_path_output():
    # return r'E:\Mingshi\MS_Program\Retrace_Program\Strategy\8_201604_IntraDay\strategy\3_Wave_Define\Python_Wave_Calculate\Result\\'
    # return r'Y:\Project Data\Mingshi\MS_Program\Retrace_Program\Strategy\8_201604_IntraDay\Strategy\3_Wave_Define\Python_Wave_Calculate\Result\figure\\'
    # return r"F:\MK_temp\Python_Wave_Calculate\Result\\"
    # return 'E:\\StrategyResult\\WaveCalculation\\wave_output_0701\\'
    return output_path


def get_daily_ret_data_path():
    return r'\\SHIMING\Desktop\qiding\DailyMarketData\dailyretme.csv'


# def get_path_output_0707():
#     return 'E:\\StrategyResult\\WaveCalculation\\wave_output_0707\\'


def get_wave_record_path():
    # return 'E:\\StrategyResult\\WaveCalculation\\wave_output_0701\\'
    # return 'E:\\StrategyResult\\WaveCalculation\\wave_output_0704_2\\'
    return output_path


def set_global_paras():
    paras = dict()

    # Wave Breaker Parameters
    paras['breaker_threshold_ret'] = .003
    paras['breaker_threshold_time'] = datetime.timedelta(seconds=10)
    paras['drawback_buffer_ret'] = .001
    paras['drawback_startpoint_ret'] = .001

    # Effective Wave Parameters
    paras['wave_trend_limit'] = .008
    paras['wave_max_duration'] = datetime.timedelta(seconds=300)
    paras['wave_min_duration'] = datetime.timedelta(seconds=60)

    # Effective Begin Time Range
    paras['effective_begin_min'] = "93100"
    paras['effective_begin_max'] = "145200"

    # Wave Returns Parameters       # MK, 20160627
    # paras['trade_depth'] = [1,2,3]
    paras['open_ret_position'] = .2
    paras['close_ret_position'] = .9
    paras['vol_start_position'] = .15
    paras['vol_end_position'] = .25
    paras['capacity_ratio'] = 1

    return paras


def time2hms(time):
    return time.strftime('%H:%M:%S')


def time2ymdhms(time):
    return time.strftime('%y%m%d%H%M%S')


def hms2datetime(hms_str):
    try:
        if len(hms_str) >= 8:
            hms_str = str(hms_str)[:-3]
        else:
            hms_str = str(hms_str)
        return datetime.datetime.strptime(hms_str,'%H%M%S')
    except:
        hms_str = '90000'
        # print("Date Error:",hms_str)
        return datetime.datetime.strptime(hms_str,'%H%M%S')


def hms2datetime2(hms_time):
    hms_str = str(hms_time)
    return datetime.datetime.strptime(hms_str,'%H:%M:%S')


mkt_open_time_morning = hms2datetime(mkt_open_time_morning_str)
mkt_close_time_morning = hms2datetime(mkt_close_time_morning_str)
mkt_open_time_afternoon = hms2datetime(mkt_open_time_afternoon_str)
mkt_close_time_afternoon = hms2datetime(mkt_close_time_afternoon_str)


def in_open_time(t):
    if isinstance(t,str):
        t = hms2datetime(t)

    flag1 = in_morning_time(t)
    flag2 = in_afternoon_time(t)

    return flag1 or flag2


def in_morning_time(t):
    if isinstance(t,str):
        t = hms2datetime(t)
    flag = mkt_open_time_morning <= t <= mkt_close_time_morning
    return flag


def in_afternoon_time(t):
    if isinstance(t,str):
        t = hms2datetime(t)
    flag = mkt_open_time_afternoon <= t <= mkt_close_time_afternoon
    return flag


def get_frequently_trading_list():
    lst = pd.read_csv(os.getcwd()+"\\Util\\stk_list.csv")
    lst = list(lst['coid'])
    lst = list(set(lst)) # Delete duplicates
    lst = [str(s).zfill(6) for s in lst]
    lst = sorted(lst)
    return lst


def find_next_tick(time,time_set):
    for i in range(len(time_set)-1):
        if time >= time_set[i] and time < time_set[i+1]:
            return i+1
    return 0


def get_ret_daily_data():
    ret_daily_data_path = get_daily_ret_data_path()
    # data = pd.read_csv(ret_daily_data_path, date_parser=hms2datetime, parse_dates=['date'])
    data = pd.read_csv(ret_daily_data_path)
    return data


def date2datetime(s):
    return datetime.datetime.strptime(s, '%Y%m%d')


def date2datestr(s):
    s = str(s)
    return '-'.join([s[0:4], s[4:6], s[6:]])


def get_intraday_trading_data():
    data_raw = pd.read_csv(intraday_team_return_path)
    data_raw['month'] = data_raw['date'].apply(lambda x: x[:-3])
    intraday_team_return_data = data_raw.groupby(['month', 'coid'], group_keys=False, as_index=False)[['traded_return', 'traded_amount', 'traded_volume']].mean()
    intraday_team_return_data['coid'] = intraday_team_return_data['coid'].apply(lambda i: str(i).zfill(6))
    intraday_team_return_data['month_last'] = intraday_team_return_data['month'].apply(get_date_list_last_month)
    return intraday_team_return_data


def get_date_list_last_month(month):
    year_, month_ = month.split('-')
    if int(month_) == 1:
        year_last_int = int(year_) - 1
        month_last_int = 12
    else:
        year_last_int = int(year_)
        month_last_int = int(month_) - 1

    date_last_month = str(year_last_int) + '-' + str(month_last_int).zfill(2)

    return date_last_month


def get_intraday_trading_date_list_last_month():
    data = get_intraday_trading_data()
    month_last_list = list(data['month_last'])
    date_list = []
    for month in month_last_list:
        for day in range(1, 32):
            date = month.replace('-', '') + str(day).zfill(2)
            date_list.append(date)
    return date_list


def get_intraday_trading_stk(date_str):
    data = get_intraday_trading_data()
    month = date_str[0:4] + '-' + date_str[4:6]
    data2 = data[data['month_last'] == month]
    if len(data2) == 0:
        return []
    else:
        stk_list = list(data2['coid'].apply(lambda s_: str(s_).zfill(6)))
        stk_list_ = list(set(stk_list))
        return stk_list_


if __name__=='__main__':
    print(mkt_open_time_morning)

    print(in_open_time('93000'))
    print(in_open_time('92500'))
    # print(in_open_time(92500))
