# -*- coding: utf-8 -*-

# Author : 'hxc'

# Time: 2024/1/12 6:05 AM

# File_name: 'pid_monitor.py'

"""
Describe: this is a demo!
"""


import os
import json
from utils.send_message import FeiShuMessage

import sys

parmName = sys.argv[1]

os.system("ps -ef|grep run_take_over_position_bot|grep -v grep|awk '{print $11}{print $12}' >pid_info.txt")


param_path = "./data/param_"
with open(param_path + parmName + '.json', 'r') as f:
    tmp_json = json.load(f)
    bot_id = tmp_json['messageInfo']['feishu']

def read_txt(txt_file):
    """
    读取文件
    :param txt_file:
    :return:
    """
    with open(txt_file, 'r', encoding="UTF-8") as fr:
        text = fr.read()
        res = [i.strip() for i in text.split(",")]
    return res


#获取需要监控的参数组列表对应的币
all_coin = {}
all_coin_list = []
for i in read_txt(txt_file="./data/param_monitor_info_{}.txt".format(parmName)):
    coin_true = read_txt(txt_file="./data/{}.txt".format(i)) #读取币种列表
    all_coin_list += coin_true
    for j in coin_true:
        all_coin[j] = i



all_coin_t ={vv:[] for kk,vv in all_coin.items()}

for kkk,vvv in all_coin.items():
    if vvv == parmName:
        all_coin_t[vvv].append(kkk)

r = read_txt(txt_file="pid_info.txt")[0]

if r:
    coin_pid = []
    coin_pid_temp= [i for i in r.split("\n") if i]

    for j in range(0,len(coin_pid_temp),2):
        if coin_pid_temp[j+1] == parmName:
            coin_pid.append(coin_pid_temp[j])

    if all_coin_t[parmName] != coin_pid:
        for k in all_coin_t[parmName]:
            if k not in coin_pid:
                #这个币掉线了，需要重启。
                os.system("nohup /root/anaconda3/bin/python -u runBot_0914.py {} {} >/dev/null 2>&1 &".format(k,all_coin[k]))
                FeiShuMessage.send_text(Text="【进程管理消息：】{} 币种重新启动".format(k),bot_id=bot_id)

elif r == "" and len(all_coin_t[parmName])>0:
    for k in all_coin_t[parmName]:

        os.system("nohup /root/anaconda3/bin/python -u runBot_0914.py {} {} >/dev/null 2>&1 &".format(k, all_coin[k]))
        FeiShuMessage.send_text(Text="【进程管理消息：】{} 币种刚才掉线，现在已重新启动".format(k), bot_id=bot_id)












