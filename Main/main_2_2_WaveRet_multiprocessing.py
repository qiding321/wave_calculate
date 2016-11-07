# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 2016/6/22 22:27
Latest Modified on: 

@auther: MK
"""



############################################################################
# This code is the main code for the whole project
############################################################################

import pandas as pd
import datetime
import time
import os
import sys
import multiprocessing

sys.path.append(os.path.pardir)

import Util.Util as Util
from Data.DataFramework import DataFramework
from Strategy.WaveDefine import WaveByTick
from Analysis.AnalysisAll import AnalysisAll
import logging


def main(start_date, end_date, logger):

    begin_time = time.clock()

    # ======================== Additional Parameters ============================ #
    # start_date = "20160516"
    # end_date = "20160601"
    use_freq_stk = False

    # ======================== Path ============================= #
    tick_data_path = Util.get_path_tickdata()
    transaction_data_path = Util.get_path_transaction_data()
    output_path = Util.get_path_output()

    # ======================== Data ============================= #
    data_framework = DataFramework(start_date_str=start_date, end_date_str=end_date, path_tickdata=tick_data_path, path_transaction_data=transaction_data_path)

    # ======================== Strategy ============================= #
    define_wave = WaveByTick(Util.set_global_paras())

    # ======================== Analysis ============================= #
    analysis_all = AnalysisAll(data_framework, define_wave)
    analysis_all.loop_date_stk_calret(use_freq_stk=use_freq_stk, output_path=output_path, logger=logger)

    # ======================== End ============================= #
    print("Complete! Total Time Used:", time.clock()-begin_time)


if __name__ == "__main__":
    multiprocessing_num = 2
    pool = multiprocessing.Pool(processes=multiprocessing_num)

    start_date = '20160101'
    end_date = '20161101'
    tick_data_path = Util.get_path_tickdata()
    transaction_data_path = Util.get_path_transaction_data()
    output_path = Util.get_path_output()

    logger = logging.getLogger()
    file_log = logging.FileHandler(Util.get_log_path())
    logger.addHandler(file_log)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_log.setFormatter(formatter)
    logger.setLevel(logging.INFO)


    data_framework = DataFramework(start_date_str=start_date, end_date_str=end_date, path_tickdata=tick_data_path, path_transaction_data=transaction_data_path)

    data_framework.update_date_list()

    for date_str in data_framework.date_list:
        print(date_str)
        # main(date_str, date_str, logger)
        pool.apply_async(main, args=(date_str, date_str, logger, ))
    pool.close()
    pool.join()

