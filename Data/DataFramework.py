# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 2016/6/15 10:29
Latest Modified on: 

@auther: MK
"""

############################################################################
# This code creates the DATA property and function
############################################################################

import os
import pandas as pd

import Util.Util as Util


# pd.options.display.width = 1000
# pd.set_option('display.max_rows',100)
# pd.set_option('display.max_columns',100)


class DataFramework:

    def __init__(self, start_date_str, end_date_str, path_tickdata, path_transaction_data, use_specific_stk=False):

        self.start_date_str = start_date_str
        self.end_date_str = end_date_str
        self.path_tickdata = path_tickdata
        self.path_transaction_data = path_transaction_data

        self.date_list = []
        self.stk_list = []

        self.use_specific_stk = use_specific_stk

    def update_date_list(self):

        if not self.use_specific_stk:
            date_list_raw = []
            date_list_raw.extend(os.listdir(self.path_tickdata + "SH"))
            date_list_raw.extend(os.listdir(self.path_tickdata + "SZ"))
        else:
            date_list_raw = Util.get_intraday_trading_date_list_last_month()
        # Delete duplicates
        date_list_raw = list(set(date_list_raw))
        date_list = [d for d in date_list_raw if self.start_date_str <= d <= self.end_date_str]

        self.date_list = sorted(date_list)

    def update_stk_list(self, date_str, use_freq_stk):
        if not use_freq_stk and not self.use_specific_stk:
            stk_list_raw = []
            stk_list_raw.extend(os.listdir(self.path_tickdata + "SH\\" + date_str))
            stk_list_raw.extend(os.listdir(self.path_tickdata + "SZ\\" + date_str))
            # Delete duplicates
            stk_list_raw = list(set(stk_list_raw))
            stk_list = [s.split('.')[0] for s in stk_list_raw]
            # stk_list = ['002308']  # todo
            self.stk_list = sorted(stk_list)
        elif not self.use_specific_stk:
            stk_list = Util.get_frequently_trading_list()
            self.stk_list = sorted(stk_list)
        else:
            stk_list = Util.get_intraday_trading_stk(date_str)
            self.stk_list = sorted(stk_list)

    def get_tickdata_from_csv_this_day_this_stk(self, date_str, stk_str):
        try:
            for exch in ['SH', 'SZ']:
                if os.path.exists(self.path_tickdata + exch + "\\" + date_str + "\\" + stk_str + ".csv"):
                    path = self.path_tickdata + exch + "\\" + date_str + "\\" + stk_str + ".csv"
                    data_raw = pd.read_csv(path,encoding="GBK", parse_dates=['time'], date_parser=Util.hms2datetime)
                    data_raw = data_raw.drop_duplicates(subset=['time'], keep='last')
                    data_raw = data_raw.set_index('time')
                    return data_raw
            print('no tick data', date_str, stk_str)
            return pd.Series()

        except Exception as e:
            print("DataFramework Input Tick Part", date_str, stk_str, str(e))
            return pd.Series()

    def get_transaction_data_from_csv_this_day_this_stk(self, date_str, stk_str):  # todo qiding 0701
        try:
            for exch in ['SH', 'SZ']:
                if os.path.exists(self.path_transaction_data + exch + "\\" + date_str + "\\" + stk_str + ".csv"):
                    path = self.path_transaction_data + exch + "\\" + date_str + "\\" + stk_str + ".csv"
                    data_raw = pd.read_csv(path,encoding="GBK", parse_dates=['time'], date_parser=Util.hms2datetime)
                    # data_raw = data_raw.drop_duplicates(subset=['time'], keep='sum')
                    data_raw_drop_duplicates = data_raw.groupby('time').agg({'bs_flag': lambda x: x.iloc[-1], 'trade_volume': 'sum'})
                    return data_raw_drop_duplicates
            print('no tick data', date_str, stk_str)
            return pd.Series()

        except Exception as e:
            print("DataFramework Input Transaction Part", date_str, stk_str, str(e))
            return pd.Series()

    def get_intraday_record_from_csv_this_day(self, date_str, account_str="zx600564358"):
        try:
            file_path = Util.get_path_intraday_record() + date_str + "\\" + account_str + ".csv"
            data_raw = pd.read_csv(file_path, encoding="GBK", parse_dates=['委托时间'], date_parser=Util.hms2datetime2)
            data_raw['证券代码'] = data_raw['证券代码'].apply(lambda x: str(x).zfill(6))

            # Only keep the Intra-day record
            data_raw = data_raw.loc[(data_raw['是否日内交易']=="是") & (data_raw['成交数量']>0)]
            data_raw = data_raw[['委托时间','证券代码','买卖']]
            data_raw = data_raw.sort_values(by=['委托时间'])

            return data_raw

        except:
            print('=====================================error in get intraday record=====================================')
            return pd.DataFrame()


if __name__ == "__main__":
    pass
    # test_data = DataFramework("20160607", "20160620", Util.get_path_tickdata())
    # test_date_stk = test_data.get_tickdata_from_csv_this_day_this_stk("20160620", "000957")