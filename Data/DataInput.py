# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 2016/6/15 13:05
Latest Modified on: 

@auther: MK
"""

############################################################################
# This code creates the tick dataset for later use
############################################################################

import numpy as np
import pandas as pd
from Data.DataFramework import DataFramework
import Util.Util as Util

pd.options.display.width = 1000
pd.set_option('display.max_rows',100)
pd.set_option('display.max_columns',100)


class TickdataOneDayOneStk:

    def __init__(self,date_str,stk_str,data):
        assert isinstance(data,DataFramework)
        self.date_str = date_str
        self.stk_str = stk_str
        self.data_from_csv = data.get_tickdata_from_csv_this_day_this_stk(date_str,stk_str)
        self.transaction_data_from_csv = data.get_transaction_data_from_csv_this_day_this_stk(date_str,stk_str)

        try:
            self.data_from_csv_filter_time = self.data_from_csv.select(Util.in_open_time)
            self.transaction_data_from_csv_filter_time = self.transaction_data_from_csv.select(Util.in_open_time)
        except:
            self.data_from_csv_filter_time = pd.DataFrame()

        try:
            # Deal with the Zero Price at Limit Board
            self.data_from_csv_filter_time['bid1'] = np.where(self.data_from_csv_filter_time['bid1'] == 0,
                                                              self.data_from_csv_filter_time['ask1'],
                                                              self.data_from_csv_filter_time['bid1'])
            self.data_from_csv_filter_time['ask1'] = np.where(self.data_from_csv_filter_time['ask1'] == 0,
                                                              self.data_from_csv_filter_time['bid1'],
                                                              self.data_from_csv_filter_time['ask1'])

            px_mid_this_day_this_stk = self.data_from_csv_filter_time.loc[:, ['ask1', 'bid1',
                                                                              'asize3', 'asize2', 'asize1',
                                                                              'bsize1', 'bsize2', 'bsize3']]  # 20160622, MK
            px_mid_this_day_this_stk['ask1'] = px_mid_this_day_this_stk['ask1']/Util.px_multiplier
            px_mid_this_day_this_stk['bid1'] = px_mid_this_day_this_stk['bid1']/Util.px_multiplier
            px_mid_this_day_this_stk['mid_prc'] = (px_mid_this_day_this_stk['bid1'] + px_mid_this_day_this_stk['ask1'])/2

            transaction_data_set_index = self.transaction_data_from_csv_filter_time
            volume_buy = transaction_data_set_index[transaction_data_set_index['bs_flag'] == 66][['trade_volume']]  # 66 is ascii code for 'B'
            volume_sell = transaction_data_set_index[transaction_data_set_index['bs_flag'] == 83][['trade_volume']]  # 83 is ascii code for 'S

            self.px_mid_this_day_this_stk = px_mid_this_day_this_stk.loc[px_mid_this_day_this_stk['mid_prc'] > 0]
            self.volume_buy = volume_buy
            self.volume_sell = volume_sell
            # px_mid_this_day_this_stk = (self.data_from_csv_filter_time['bid1'] +
            #                             self.data_from_csv_filter_time['ask1'])/2/10000
            # self.px_mid_this_day_this_stk = px_mid_this_day_this_stk[px_mid_this_day_this_stk>0]

        except Exception as e:
            print('data_error, {}, {}, {}'.format(self.date_str, self.stk_str, e))
            self.px_mid_this_day_this_stk = pd.DataFrame({"mid_prc": [], "ask1": [], "bid1": [],
                                                          "asize3": [], "asize2": [], "asize1": [],
                                                          "bsize1": [], "bsize2": [], "bsize3": [],
                                                          'volume_buy': [], 'volume_sell': []})
            self.volume_buy = pd.Series()
            self.volume_sell = pd.Series()


if __name__ == "__main__":
    test_data = DataFramework("20160401", "20160401", Util.get_path_tickdata())
    test_tickdata = TickdataOneDayOneStk("20160401", "000005", test_data)
