### 						仓位接管工具

### 0、介绍

​	最近布欧老师更新了一个神器：仓位管理工具脚本，可以半自动接管自己的仓位，一旦有币种下单就会接管进行监控，按照设置的移动止盈止损比例进行无情绪化的止盈和止损，大家都知道，做交易时候就怕自己上头造成巨大的亏损，并打乱自己交易节奏。现在这个机器人🤖️接管自己的仓位后，就不用担心了，我们只负责看机会下单就可以了。目前我在okx交易所做交易，我就开发了这个okx版本的仓位接管工具，免费开源给粉丝朋友们，进群可享受免费部署，包教包会，群中也附带一些pine 语言写的策略（电报群获取）可以仅供学习参考，不作为投资建议！！！欢迎star。

​	主要功能：

​	1）监控okx合约市场的所有币种

​    2）支持程序运行的过程中修改自己的参数

​    3）支持程序暂停、退出等操作，可以再次重启不影响监控

​	4）支持飞书群消息通知

​	使用工具需要1个条件：是要有非大陆的服务器或者电脑。

​	需要购买服务器的可以去这里：

https://www.ucloud.cn/active/ulhost.html?invitation_code=C1x61A89E959B77

### 1、安装部署工具步骤

​	以linux 服务器为例

​		1)、购买境外服务器（至少2核1g，系统centos7以上即可，一年100多块钱）

​		2)、下载安装anaconda（不会登陆linux系统服务器的可以百度一下，或者进群咨询😄）

```python
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-2021.05-Linux-x86_64.sh
```

​		安装anaconda参考链接：https://blog.csdn.net/Lin1169404361/article/details/123288482

​		

### 2、交易所设置

​	1）okx交易所交易设置：买卖模式

​	2）以“张”为单位下单，没有小数点的事情。

### 3、启动脚本

启动脚本命令：

```python
cd take_over_position_bot 
source source_run.sh start  #启动服务
source source_run.sh status  #查看启动状态，出现pid进程编号基本上启动成功啦
source source_run.sh stop  #停止服务
taif -f logs/info.log #查看日志，不想查看了就ctrl +c 取消即可
```

### 4、机器人内在原理

​		当你账户上有个币下单后，该仓位的结果有2个。一个止盈一个止损。止损就不必说了，设置一个比例，当价格到达这个比例时就止损。至于止盈，这边有3个档位。当机器人监控到这个币的时候，它会计算利润率，当达到0.3百分比的时候（当然0.3我也做了参数可以调节修改），达到 低档位（也就是第一档位），这个利润率如果再回到0.2百分点时候，就执行平仓。（其实这里时为了测试行情是否有个突发情况，如果没有那果断就不做这一单，其实这一点很重要，如果人来进行交易没有那么果断。）当有突发行情，利润率达到1百分点的时候，就来到了第二档位，然后再持续监控第二档位的利润率是否有回落，如果有回落，且回落的比例大于20%，那么我们也平仓出局，如果没有就继续拿着，当利润率来到3个百分点的时候，就来到了第三档位，同样如果利润率回落比例大于25%的时候就要出局了 ，否则继续拿着，这样的好处就是可以让利润持续奔跑，尤其是一波行情的时候 至少能吃80%的行情。

### 5、机器人参数说明

```josn
{
    "leverage": 5, #杠杆
    "stop_loss_pct": 0.02, #止损比例
    "profit_activate_1_pao": 0.2, #第一档位回落到0.2百分点的时候跑，需要和第一档的激活值配合使用
    "trail_stop_loss_pct": 0.2, # 第二档回落20%时，触发止盈
    "higher_trail_stop_loss_pct": 0.25,# 第三档回落50%时，触发止盈
    "profit_activate_1": 0.3, #当利润率达到激活值为0.3%时为第一档位。
    "profit_activate_2": 1,#当利润率达到激活值为1%时为第二档位。
    "profit_activate_3": 3,#当利润率达到激活值为3%时为第三档位。
    "apiInfo": {"apiKey": "1e6021f8-e5ef1bbcd5df",
        "secretKey": "9420717505C848C",
        "passphrase": "H@"},
    "messageInfo": {"feishu": "015e67df-04cb-47bc5b46a869a4"} #飞书群里的机器人的id,可以再设置里找到机器人的id，也就是链接后面的id
}
```
### 6、todo

​	1、支持监控币种设置黑名单列表；
​	2、新增客户端，支持windows、mac用户；
​	3、新增coinank.con网站的情绪化自动交易。



### 7、免责声明

​		本工具不保证策略收益，一切盈亏损失自行承担！禁止商用，仅供学习使用！如果违反，出了一切法律后果自负。

### 8、学习与交流

​	Telegram群：https://t.me/+bRIWTkW0RjAzYjc9

​	币圈二哥量化的口号是：免费开源、暴富向前！！！	



