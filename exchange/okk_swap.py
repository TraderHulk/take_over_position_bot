# -*- coding: utf-8 -*-

# Author : 'hxc'

# Time: 2022/10/15 11:09 AM

# File_name: 'okk_swap.py'

"""
Describe: this is a demo!
"""
import logging
import sys
sys.path.append("../")
from decimal import  Decimal
from exchange.okx import Public_api as Public
from exchange.okx import Trade_api as Trade
from exchange.okx import Account_api as Account
from exchange.okx import Funding_api as Funding


class OkkSwap(object):

    def __init__(self, api_key, secret_key, passphrase):
        self.publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag="0")
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag="0")
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag="0")
        # funding api
        self.fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag="0")



    def get_uid(self):
        """获取用户的uid"""
        uid = '-1'
        try:
            r = self.accountAPI.get_account_config()
            uid = r['data'][0]['uid']
        except Exception as e:
            print("获取uid失败")
            print(e)

        return uid

    def get_standard_qty(self, qty, symbol):
        """标准化qty"""
        qty_s = qty

        try:
            r = self.publicAPI.convert_contract_coin(type='1', instId=symbol, sz=qty)
            qty_s = r['data'][0]['sz']

        except Exception as e:

            print("ok标准化qty失败")
            print(e)
        return qty_s

    def updatebalance(self):
        """更新一下资产信息"""
        usdt = '-1'
        try:
            result = self.accountAPI.get_account(ccy='USDT')

            u = result['data'][0]['details'][0]['availEq']
            usdt = u
        except Exception as e:
            print("获取资产失败！！！")
            print(e)

        return float(usdt)

    def get_cz_info(self):
        """获取充值的信息"""
        check_list = []
        try:
            r = self.fundingAPI.get_deposit_history(ccy="USDT", limit=50)

            cz_list = r['data']
            for i in cz_list:
                if i['from'] == "":
                    check_list.append({i['txId']: [i['ts'], i['amt'],"out"]})
                else:
                    check_list.append({i['from']: [i['ts'],i['amt'], "in"]})
        except Exception as e:
            print(e)

        return check_list

    def set_order(self,symbol, qty,side, ordType="market",posSide=None, px=None,reduceOnly=None):
        """设置订单"""

        try:
            self.tradeAPI.place_order(instId=symbol,
                                          tdMode="cross",
                                          side=side,
                                          posSide=posSide,
                                          ordType=ordType,
                                          px = px,
                                          sz=qty,
                                         reduceOnly=reduceOnly)




        except Exception as e:
            print("下多单失败")
            print(e)

    def set_pingall_order(self, symbol, mgnMode="cross",posSide=None):
        """市场价全平"""
        try:
            r = self.tradeAPI.close_positions(instId=symbol,
                                              mgnMode=mgnMode,
                                              posSide=posSide,
                                              ccy='')
            print(r)

        except Exception as e:
            print("市价全平失败", symbol)
            print(e)



    def updatePosition(self):
        """获取有仓位的单向持仓的仓位"""

        position_info = {}
        symbols = []
        try:
            result = self.accountAPI.get_positions('SWAP')
            for pos in result['data']:
                if abs(float(pos['pos'])) > 0:
                    position_dict = {"symbol": "", "position_amt": 0, "entry_price": 0.0, "current_price": 0.0, "side": "","td_mode":""}
                    position_dict["symbol"] = pos['instId']
                    position_dict['position_amt'] = pos['pos']
                    position_dict['entry_price'] = pos['avgPx']
                    position_dict['current_price'] = pos['markPx']
                    position_dict['side'] = "short" if float(pos['pos']) < 0 else "long"
                    position_dict['td_mode'] = pos['mgnMode']
                    position_info[pos['instId']] = position_dict
                    symbols.append(pos['instId'])
        except Exception as e:
            print("okx，获取{}币种的仓位失败！！！".format(symbol))
            print(e)

        return position_info,symbols


    def get_history_trades(self,symbol):
        """获得历史成交"""
        try:
            result = self.tradeAPI.get_orders_history(instType="SWAP",instId=symbol)
            print(result['data'][:1])
        except Exception as e:
            print("获取历史订单")


    def do_market(self,signal,symbol,qty):
        """市场价进行交易"""
        try:
            position = self.updatePosition(symbol=symbol)
            logging.info("okx_position:{}".format(position))
            if signal == "long" and float(position)<=0:
                # 平空单
                if float(position) != 0:
                    self.set_pingall_order(symbol=symbol)
                self.set_order(symbol=symbol, qty=str(qty), side="buy")
            elif signal == "short" and float(position)>=0:
                # 平多单
                if float(position) != 0:
                    self.set_pingall_order(symbol=symbol)

                self.set_order(symbol=symbol, qty=str(qty), side="sell")

            elif signal == "long" and float(position)>0:
                # 加多仓
                self.set_order(symbol=symbol, qty=str(qty), side="buy")

            elif signal == "short" and float(position) < 0:
                # 加空仓
                self.set_order(symbol=symbol, qty=str(qty), side="sell")

            elif signal == "tp_long_batch" and float(position)>0:
                #平多一份订单
                self.set_order(symbol=symbol, qty=str(qty), side="sell",reduceOnly=True)

            elif signal == "tp_short_batch" and float(position)<0:
                #平空一份订单
                self.set_order(symbol=symbol, qty=str(qty), side="buy",reduceOnly=True)

            elif signal == "tp_long":
                self.set_pingall_order(symbol=symbol)

            elif signal == "tp_short":
                self.set_pingall_order(symbol=symbol)

        except Exception as e:
            logging.error(msg='okk api出问题' + str(e))


if __name__=="__main__":
    flag = 'c'
    coins = ["IOTA", "ZIL"]
    api_key = "1e602d7b-6665-434e-a1f8-e5ef1bbcd5df"
    secret_key = "942071DFA8B7CD9F30B89397505C848C"
    passphrase = "Huang1018@"
    o = OkkSwap(api_key, secret_key, passphrase)
    for coin in coins:
        symbol = coin + "-USDT-SWAP"
        o.set_pingall_order(symbol=symbol)











