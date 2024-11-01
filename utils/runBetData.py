# -*- coding: utf-8 -*-

# Author : 'hxc'

# Time: 2023/5/31 5:35 PM

# File_name: 'runBetData.py'

"""
Describe: this is a demo!
"""

import os
import json
import logging



class RunBetData(object):
    def __init__(self, file_name,name):
        self.coin = file_name
        self.text = ""
        self.data_path = os.getcwd() + "/temp/" + name + "/temp_"

    def _get_json_data(self):
        '''读取json文件'''
        tmp_json = {}
        with open(self.data_path + self.coin + '.json', 'r') as f:

            tmp_json = json.load(f)
            f.close()
        return tmp_json

    def _modify_json_data(self, data):
        '''修改json文件'''
        with open(self.data_path + self.coin + '.json', "w") as f:
            f.write(json.dumps(data, indent=4))
        f.close()

    ####------下面为输出函数--------####

    def get_local_position_info(self):
        """
        获取最新的last_timestamp
        :return:
        """
        data_json = self._get_json_data()
        return data_json["local_position_info"]

    def modify_local_position_info(self, local_position_info):
        """
        修改 last_timestamp
        :return:
        """
        data_json = self._get_json_data()
        data_json['local_position_info'] = local_position_info
        self._modify_json_data(data_json)

    def get_detected_positions(self):
        """
        获取最新的last_timestamp
        :return:
        """
        data_json = self._get_json_data()
        return data_json["detected_positions"]


    def modify_detected_positions(self,detected_positions):
        """
        修改 last_timestamp
        :return:
        """
        data_json = self._get_json_data()
        data_json['detected_positions'] = detected_positions
        self._modify_json_data(data_json)

    def get_highest_profits(self):
        """
        获取最新的last_timestamp
        :return:
        """
        data_json = self._get_json_data()
        return data_json["highest_profits"]

    def modify_highest_profits(self, highest_profits):
        """
        修改 last_timestamp
        :return:
        """
        data_json = self._get_json_data()
        data_json['highest_profits'] = highest_profits
        self._modify_json_data(data_json)


