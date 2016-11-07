# -*- coding: utf-8 -*-
"""
Created on 2016/7/7 9:03

@author: qiding
"""

import Util.Util as Util
import logging
import os
import datetime
import pandas as pd

from Data.DataFramework import DataFramework


logger = logging.getLogger()
file_log = logging.FileHandler('\\\\SHIMING\\Desktop\\qiding\\GradedFundTrading\\Log\\data_download.log')
logger.addHandler(file_log)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
file_log.setFormatter(formatter)
logger.setLevel(logging.INFO)


def main():

    start_date = '20160301'
    end_date = '20160628'
    # start_date = "20160501"
    # end_date = "20160601"

    wave_record_path = Util.get_wave_record_path() + 'wave_ret_record\\'
    # daily_data_path = Util.get_daily_ret_data_path()

    summary_output_path_each_day_each_stk = Util.get_wave_record_path() + 'summary_output_stk_date.csv'
    summary_output_path_all_day_each_stk = Util.get_wave_record_path() + 'summary_output_by_stk.csv'

    wave_capacity_threshold = 0
    wave_amount_threshold = 10000

    ret_daily_data = Util.get_ret_daily_data()

    data_all_wave = get_all_wave(wave_record_path, start_date, end_date).drop_duplicates(keep='last', subset=['date', 'stock', 'wave_num'])
    data_all_wave['amount_tradable'] = data_all_wave['vol_capacity'] * data_all_wave['open_prc']

    data_wave_by_date_stk = get_wave_by_stock_date(data_all_wave, wave_capacity_threshold, wave_amount_threshold)
    print(summary_output_path_each_day_each_stk)
    data_wave_by_date_stk.to_csv(summary_output_path_each_day_each_stk, index=False)

    data_wave_by_date_stk_merge_daily_data = merge_daily_data(ret_daily_data, data_wave_by_date_stk)

    data_wave_by_stk_group = get_wave_by_stock(data_wave_by_date_stk_merge_daily_data)

    data_wave_by_stk_group_add_rank = add_rank(data_wave_by_stk_group, ['avg_effective_wave_num', 'avg_profit', 'avg_ret', 'ret_sum_one_day'])
    print(summary_output_path_all_day_each_stk)
    data_wave_by_stk_group_add_rank.to_csv(summary_output_path_all_day_each_stk)


def add_rank(data_wave_by_stk_group, column_list):
    for col in column_list:
        rank_col = pd.Series(list(range(1, len(data_wave_by_stk_group) + 1)), index=data_wave_by_stk_group.sort_values(col, ascending=False).index)
        data_wave_by_stk_group[col+'_rank'] = rank_col
    data_wave_by_stk_group['avg_rank'] = data_wave_by_stk_group[[cl+'_rank' for cl in column_list]].mean(axis=1)

    return data_wave_by_stk_group.sort_values('avg_rank')


def merge_daily_data(ret_daily_data, data_wave_by_date_stk):
    ret_daily_data_ = ret_daily_data.rename(columns={'id': 'stock'})[['date', 'stock', 'px_last', 'px_volume', 'eqy_sh_out']]
    data = pd.merge(left=ret_daily_data_, right=data_wave_by_date_stk, on=['stock', 'date'], how='right')
    return data


def get_wave_by_stock(data_wave_by_date_stk):
    assert isinstance(data_wave_by_date_stk, pd.DataFrame)

    group_by_stk = data_wave_by_date_stk.groupby('stock')
    data = []
    index_all = []
    for stk, chunk in group_by_stk:
        avg_size = (chunk['eqy_sh_out'] * chunk['px_last']).mean()
        avg_px = chunk['px_last'].mean()
        avg_trading_amount_one_stk_all_time = (chunk['px_last'] * chunk['px_volume']).mean()
        trading_day_num = len(chunk.index)
        trading_day_num_effective_wave = len(chunk[chunk['effective_wave_num']!=0].index)
        avg_effective_wave_num = chunk['effective_wave_num'].mean()
        avg_all_wave_num = chunk['all_wave_num'].mean()
        std_effective_wave_num = chunk['effective_wave_num'].std()
        avg_amount_tradable = chunk['amount_tradable_effective'].mean()
        avg_amount_tradable_6times = avg_amount_tradable * 6
        avg_profit = chunk['effective_tradable_profit_sum'].mean()
        avg_profit_60pct = avg_profit * .6
        avg_ret = chunk['wave_avg_ret_effective'].mean()
        ret_sum_one_day = (chunk['wave_avg_ret_effective']*chunk['all_wave_num']).mean()
        avg_effective_wave_ratio = chunk['effective_wave_ratio'].mean()
        std_effective_wave_ratio = chunk['effective_wave_ratio'].std()

        index = ['avg_size', 'avg_px', 'avg_trading_amount_one_stk_all_time', 'trading_day_num',
                 'trading_day_num_effective_wave', 'avg_effective_wave_num', 'avg_all_wave_num',
                 'std_effective_wave_num', 'avg_amount_tradable', 'avg_amount_tradable_6times',  'avg_profit', 'avg_profit_60pct', 'avg_ret',
                 'ret_sum_one_day', 'avg_effective_wave_ratio', 'std_effective_wave_ratio']
        value = [avg_size, avg_px, avg_trading_amount_one_stk_all_time, trading_day_num,
                 trading_day_num_effective_wave, avg_effective_wave_num, avg_all_wave_num,
                 std_effective_wave_num, avg_amount_tradable, avg_amount_tradable_6times, avg_profit, avg_profit_60pct, avg_ret,
                 ret_sum_one_day, avg_effective_wave_ratio, std_effective_wave_ratio]
        data.append(pd.Series(value, index=index))
        index_all.append(stk)

    return pd.DataFrame(data, index=index_all)


def get_wave_by_stock_date(data_all_wave, wave_capacity_threshold, wave_amount_threshold):

    data_all_wave['is_effective'] = ((data_all_wave['vol_capacity'] >= wave_capacity_threshold) & (data_all_wave['amount_tradable'] >= wave_amount_threshold)).apply(lambda y: 1 if y else 0)
    data_all_wave['vol_capacity_effective'] = data_all_wave['vol_capacity'] * data_all_wave['is_effective']
    data_all_wave['amount_tradable_effective'] = data_all_wave['amount_tradable'] * data_all_wave['is_effective']
    data_all_wave['ret_effective'] = data_all_wave['is_effective'] * data_all_wave['ret']
    data_all_wave['profit'] = data_all_wave['ret'] * data_all_wave['vol_capacity'] * data_all_wave['is_effective']

    data_wave_by_date_stk = data_all_wave.groupby(['stock', 'date'], as_index=False).agg({
        'wave_num':  'count', 'ret_effective':  'mean', 'vol_capacity_effective': 'sum', 'profit': 'sum', 'amount_tradable_effective': 'sum', 'is_effective': 'sum'
    }).rename(columns={
        'wave_num': 'all_wave_num', 'ret_effective': 'wave_avg_ret_effective', 'vol_capacity_effective': 'vol_tradable_sum', 'profit': 'effective_tradable_profit_sum', 'amount_tradable_effective': 'amount_tradable_effective',
        'is_effective': 'effective_wave_num'
    })
    data_wave_by_date_stk['effective_wave_ratio'] = data_wave_by_date_stk['effective_wave_num'] / data_wave_by_date_stk['all_wave_num']

    return data_wave_by_date_stk


def get_all_wave(wave_record_path, start_date, end_date):
    file_list = [file_name_ for file_name_ in os.listdir(wave_record_path) if start_date<=file_name_.split('.')[0].split('_')[-1]<=end_date]
    data_all_list = []
    for wave_record_file_name in file_list:
        data_this_day = pd.read_csv(wave_record_path+wave_record_file_name)
        data_this_day['date'] = data_this_day['date'].apply(Util.date2datestr)
        data_all_list.append(data_this_day)
    data_all_df = pd.DataFrame(pd.concat(data_all_list))

    return data_all_df


if __name__ == '__main__':
    main()
