# -*- coding: utf-8 -*-

"""
Project Name: Code
First Created on: 16/6/17 16:42
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


sys.path.append(os.path.pardir)

import Util.Util as Util
from Data.DataFramework import DataFramework
from Strategy.WaveDefine import WaveByTick
from Analysis.AnalysisAll import AnalysisAll



def main():


    begin_time = time.clock()

    print("#################### Setup ####################")
    # ======================== Additional Parameters ============================ #
    start_date = "20160620"
    end_date = "20160620"
    use_freq_stk = True

    # ======================== Path ============================= #
    tick_data_path = Util.get_path_tickdata()
    output_path = Util.get_path_output()


    # ======================== Data ============================= #
    print("#################### Data ####################")
    data_framework = DataFramework(start_date_str=start_date,end_date_str=end_date,path_tickdata=tick_data_path)



    # ======================== Strategy ============================= #
    print("#################### Strategy:Wave ####################")
    define_wave = WaveByTick(Util.set_global_paras())


    # ======================== Analysis ============================= #
    print("#################### Analysis ####################")
    analysis_all = AnalysisAll(data_framework,define_wave)
    analysis_all.loop_date_stk_plot(use_freq_stk=use_freq_stk,output_path=output_path)


    # ======================== End ============================= #
    print("Complete! Total Time Used:",time.clock()-begin_time)




if __name__ == "__main__":
    main()












