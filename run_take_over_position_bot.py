# -*- coding: utf-8 -*-

# Author : 'hxc'

# Time: 2024/10/31 11:15 AM

# File_name: 'run_take_over_position_bot.py'

"""
Describe: this is a demo!
"""
import os
import time
from datetime import datetime
import logging.config
from os import path
from exchange.okk_swap import OkkSwap
from utils.send_message import FeiShuMessage
from utils.runBetData import RunBetData


# 导入日志配置文件
log_file_path = path.join(path.dirname(path.abspath(__file__)), "configs/logging.conf")
logging.config.fileConfig(log_file_path)
# 创建日志对象
logger = logging.getLogger()
loggerInfo = logging.getLogger("TimeInfoLogger")
Consolelogger = logging.getLogger("ConsoleLogger")


class MultiAssetTradingBot(OkkSwap):
    """多币种仓位管理机器人"""

    def __init__(self, apiKey, secretKey, passphrase, paramName):
        self.apiKey = apiKey
        self.paramName = paramName
        self.update_config_file()
        self.feishu_bot = FeiShuMessage()
        super().__init__(api_key=apiKey, secret_key=secretKey, passphrase=passphrase)
        logger.info("仓位接管工具初始化成功！！！")


    def update_config_file(self):
        """更新参数"""

        with open(param_path + self.paramName + '.json', 'r') as f:
            tmp_json = json.load(f)
            self.leverage = tmp_json['leverage'] #杠杆
            self.stop_loss_pct = tmp_json['stop_loss_pct'] #触发止损阈值
            self.trail_stop_loss_pct = tmp_json['trail_stop_loss_pct'] #触发第一档移动止盈阈值
            self.higher_trail_stop_loss_pct = tmp_json['higher_trail_stop_loss_pct'] #触发第二档移动止盈
            self.profit_activate_1 = tmp_json['profit_activate_1'] #利润低档位阈值
            self.profit_activate_2 = tmp_json['profit_activate_2']  # 利润第一档位阈值
            self.profit_activate_3 = tmp_json['profit_activate_3']  # 利润第二档位阈值
            self.profit_activate_1_pao = tmp_json['profit_activate_1_pao']
            self.symbols = tmp_json['symbols'] #只监控币种的列表 如果没有写，默认就是全币种监控，好处就是可以节约一些时间
            self.black_coin_list = tmp_json['black_coin_list'] #黑名单，加入后就不进行监控该币种的仓位了
            self.feishu_bot_id = tmp_json['messageInfo']['feishu']

    def generate_json_file(self):
        """生成json文件记录所有币种的"""

        temp_dict = {"local_position_info":[],
                     "detected_positions":[],
                     "highest_profits":{}}
        with open("./temp/" + self.apiKey + "/temp_" + self.paramName + ".json", "w") as f:
            json.dump(temp_dict, f)

    def get_tier(self, profit):
        if profit >= self.profit_activate_3:
            return "第二档移动止盈"
        elif profit >= self.profit_activate_2:
            return "第一档移动止盈"
        elif profit >= self.profit_activate_1:
            return "低档保护止盈"
        else:
            return "无"

    def check_position(self,runbet,profit_pct, highest_profits, tier, symbol, td_mode):

        """检查仓位"""
        highest_profit = highest_profits[symbol]
        if tier == "低档保护止盈":
            logger.info(f"回撤到{self.profit_activate_1_pao}% 止盈")
            if profit_pct <= self.profit_activate_1_pao:
                msg = f"{symbol} 触发低档保护止盈，当前盈亏回撤到: {profit_pct:.2f}%，执行平仓"
                logger.info(msg)
                self.set_pingall_order(symbol=symbol,mgnMode=td_mode)
                highest_profits[symbol] = 0
                runbet.modify_highest_profits(highest_profits=highest_profits)
                return

        elif tier == "第一档移动止盈":
            trail_stop_loss = highest_profit * (1 - self.trail_stop_loss_pct)
            logger.info(f"回撤到 {trail_stop_loss:.2f}% 止盈")
            if profit_pct <= trail_stop_loss:
                logger.info(f"{symbol} 达到利润回撤阈值，当前档位：第一档移动止盈，最高盈亏: {highest_profit:.2f}%，当前盈亏: {profit_pct:.2f}%，执行平仓")
                self.set_pingall_order(symbol=symbol,mgnMode=td_mode)
                highest_profits[symbol] = 0
                runbet.modify_highest_profits(highest_profits=highest_profits)
                return

        elif tier == "第二档移动止盈":
            trail_stop_loss = highest_profit * (1 - self.higher_trail_stop_loss_pct)
            logger.info(f"回撤到 {trail_stop_loss:.2f}% 止盈")
            if profit_pct <= trail_stop_loss:
                logger.info(f"{symbol} 达到利润回撤阈值，当前档位：第二档移动止盈，最高盈亏: {highest_profit:.2f}%，当前盈亏: {profit_pct:.2f}%，执行平仓")
                self.set_pingall_order(symbol=symbol, mgnMode=td_mode)
                highest_profits[symbol] = 0
                runbet.modify_highest_profits(highest_profits=highest_profits)
                return

        if profit_pct <= -self.stop_loss_pct * 100:
            logger.info(f"{symbol} 触发止损，当前盈亏: {profit_pct:.2f}%，执行平仓")
            self.set_pingall_order(symbol=symbol,mgnMode=td_mode)
            runbet.modify_highest_profits(highest_profits=highest_profits)
            highest_profits[symbol] = 0
            runbet.modify_highest_profits(highest_profits=highest_profits)




    def monitor_positions(self,runbet):
        """监控仓位"""

        if self.black_coin_list:
            self.black_coin_list = [i.upper() + "-USDT-SWAP" for i in self.black_coin_list]

        #获取本地记录的监控的币种
        detected_positions = runbet.get_detected_positions()

        highest_profits = runbet.get_highest_profits()
        if self.symbols == [] :
            position_info, symbols = self.updatePosition()
        else:
            # 更新仓位
            position_info, symbols = self.updatePosition_coins(coins=self.symbols)

        symbols = [i for i in symbols if i not in self.black_coin_list] #去掉黑名单的仓位币种


        if position_info == {}:
            return

        #处理平仓与新增
        if symbols != detected_positions:
            #如果2个集合不一致，说明有平仓或者新增
            #处理平仓
            for symbol in detected_positions:
                if symbol not in symbols:
                    ping_msg = "【平仓币种通知:】\n"
                    ping_msg += f"{symbol}币种已经平仓！\n" + "{}".format(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    logger.info(ping_msg)
                    self.feishu_bot.send_text(Text=ping_msg,bot_id=self.feishu_bot_id)
            #处理新增
            for symbol in symbols:
                if symbol not in detected_positions:
                    highest_profits[symbol] = 0.0
                    ping_msg ="【新增监控币种通知:】\n" + \
                              "新增币种：{}\n".format(symbol) +\
                              "仓位数量：{}\n".format(position_info[symbol]['position_amt']) + \
                              "开仓价格：{}\n".format(position_info[symbol]['entry_price']) + \
                              "开仓方向：{}\n".format(position_info[symbol]['side']) + \
                              "新增时间：{}\n".format(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                    logger.info(ping_msg)
                    self.feishu_bot.send_text(Text=ping_msg, bot_id=self.feishu_bot_id)

                    #更新本地监控币种
            runbet.modify_local_position_info(local_position_info=position_info)
            runbet.modify_detected_positions(detected_positions=symbols)
            runbet.modify_highest_profits(highest_profits=highest_profits)

        highest_profits = runbet.get_highest_profits()
        #监控现有仓位币种的行情
        for symbol, pos_info in position_info.items():
            if symbol in self.black_coin_list:
                continue
            position_amt = pos_info['position_amt']
            current_price = float(pos_info['current_price'])
            entry_price = float(pos_info['entry_price'])
            side = pos_info['side']
            td_mode = pos_info['td_mode']
            if side == 'long':
                profit_pct = (current_price - entry_price) / entry_price * 100
            elif side == 'short':
                profit_pct = (entry_price - current_price) / entry_price * 100
            else:
                continue

            if profit_pct > highest_profits[symbol]:
                highest_profits[symbol] = profit_pct
                runbet.modify_highest_profits(highest_profits=highest_profits)

            current_tier = self.get_tier(highest_profits[symbol])
            logger.info(
                f"监控 {symbol}，仓位: {position_amt}，方向: {side}，开仓价格: {entry_price}，当前价格: {current_price}，浮动盈亏: {profit_pct:.2f}%，最高盈亏: {highest_profits[symbol]:.2f}%，当前档位: {current_tier}")
            self.check_position(runbet,profit_pct, highest_profits, current_tier, symbol, td_mode)




    def schedule_task(self):
        """运行"""
        logger.info("启动主循环，开始执行任务调度...")
        try:
            while 1:
                self.update_config_file() #支持热更新参数
                # 如果没有文件夹就创建文件夹
                if not os.path.exists("./temp/" + self.apiKey):
                    os.mkdir("./temp/" + self.apiKey)
                if not os.path.exists("./temp/" + self.apiKey + "/temp_" + self.paramName + ".json"):
                    self.generate_json_file()
                runbet = RunBetData(file_name=self.paramName,name=self.apiKey)
                self.monitor_positions(runbet=runbet)
                time.sleep(4)
        except KeyboardInterrupt:
            logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            logger.error(error_message)
            self.feishu_bot.send_text(Text=error_message,bot_id=self.feishu_bot_id)


if __name__ == "__main__":
    import sys, json
    paramName = sys.argv[1]
    param_path = "./configs/param_"
    logging.info("-------欢迎使用仓位接管工具v1.0版本----------")
    # 加载账户信息进行实例化跟踪机器人
    with open(param_path + paramName + '.json', 'r') as f:
        tmp_json = json.load(f)
        api_key = tmp_json['apiInfo']['apiKey']
        api_secret = tmp_json['apiInfo']['secretKey']
        passphrase = tmp_json['apiInfo']['passphrase']

    bot = MultiAssetTradingBot(api_key, api_secret, passphrase, paramName)
    bot.schedule_task()



