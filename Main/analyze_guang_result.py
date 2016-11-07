# -*- coding: utf-8 -*-
"""
Created on 2016/7/26 17:34

@author: qiding
"""

import pandas as pd


def main():
    # file_name_list = ['real_trading_autocl_iwt0.2s_t15c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t30c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t60c_diff-10bp.csv',
    #                   'real_trading_autocl_iwt0.2s_t60c_diff-15bp.csv', 'real_trading_autocl_iwt0.15s_t45c_diff-15bp.csv']
    # file_name_list = ['real_trading_autocl_iwt0.2s_t15c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t30c_diff-15bp.csv',
    #                   'real_trading_autocl_iwt0.15s_t45c_diff-15bp.csv']
    root_path = 'E:\\StrategyResult\\GuangProject\\out_of_sample_one_month\\'
    # root_path = 'E:\\StrategyResult\\GuangProject\\parameter_screening\\'
    file_name_list = ['real_trading_autocl_iwt0.2s_t15c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t30c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t60c_diff-10bp.csv',
                      'real_trading_autocl_iwt0.2s_t60c_diff-15bp.csv']
    # file_name_list = ['real_trading_autocl_iwt0.2s_t15c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t30c_diff-15bp.csv', 'real_trading_autocl_iwt0.2s_t60c_diff-10bp.csv',
    #                   'real_trading_autocl_iwt0.2s_t60c_diff-15bp.csv', 'real_trading_autocl_iwt0.15s_t45c_diff-15bp.csv']
    # root_path = 'E:\\StrategyResult\\GuangProject\\'
    for file_name in file_name_list:
        file_path = root_path + file_name
        data = pd.read_csv(file_path)
        # data_clean = data[data['AT_forced_close'] == 0]
        # data_clean = data[data['AT_forced_close'] == 1]
        data_clean = data

        mean = data_clean['excess_ret'].mean()
        std = data_clean['excess_ret'].std()
        win_ratio = len(data_clean[data_clean['excess_ret']>=0]) / len(data_clean)
        print(file_name, mean, std, win_ratio)


if __name__ == '__main__':
    main()