# 通过API转存数据
1. 通常想下载的数据都是三维。`时间`\*`票池`\*`字段`。数据量有可能是`1000*100*10`。
2. 但多数接口只提供二维的数据下载方式。在查询处理速度与查询次数之间需要平衡。
    1. 万得。按字段查询全部股票几年的数据，比按天查所有股票快，比按股票查几年的数据要快
    2. 聚宽。按股票查所有字段几年的数据快。由于聚宽低层数据组织方式就是按股票存，如果将所有数据加载，然后取出某个字段再组合，极慢，反而不好用。
3. 需要缓存一定的信息
    1. 交易日历。不需要每天下载，可节省额度
    2. 每天票池。有些api是按天下载，有些是按日期段下载，限定时间范围可节省额度
    
## 使用方法
参考`examples/tushare_api`或`examples/jqdatasdk`下的代码
1. 修改config.py中账号，并实现对应接口的认证登录认证
2. 先参考`get_trade_days.py`或`trade_cal.py`实现交易日历下载
3. 再参考`get_all_securities.py`或`stock_basic.py`实现票池下载
4. 合理利用，实现行情等一类的数据下载

```python
import time

import pandas as pd

from ddump.api.dump import Dump__date
from examples.tushare.config import DATA_ROOT, pro

if __name__ == '__main__':
    end = f"{pd.to_datetime('today'):%Y-%m-%d}"
    # 加载交易日历
    trading_day = pd.read_parquet(DATA_ROOT / 'trade_cal' / f'SSE.parquet')
    trading_day = trading_day[trading_day['is_open'] == 1]['cal_date']
    trading_day.index = pd.to_datetime(trading_day)
    # 过滤交易日
    trading_day = trading_day['2022-01-01':end]

    for func_name, m, n in [
        ('daily', 10, 1000),
        ('adj_factor', 10, 1000),
        ('suspend_d', 60, 50),  # 盘前就有，盘中有新增。每分钟只能访问50次
    ]:
        path = DATA_ROOT / func_name
        d = Dump__date(pro, path, 'trade_date')
        for i, trade_date in enumerate(trading_day):
            d.set_parameters(func_name, trade_date=trade_date)
            if not d.exists(file_timeout=3600 * 4, data_timeout=86400 * 3):
                d.download()
                d.save(save_empty=True)
                if i % n == n - 1:
                    time.sleep(m)

```

1. Dump: 基类。按任意参数转存
2. Dump__start__end: 按开始日期与结束日期转存
3. Dump__date: 开始日期等于结束日期的特例

## 数据下载步骤
一般情况下：
1. 首先，index(交易日历)。按交易所下载，数据量不多可以全量也可以增量
2. 然后，columns(票池)。板块是动态变化的
    1. 按天查的接口，需要用折半等方法减少数据量和请求次数下载
    2. 全量查询接口，按需过滤出每天的票池。一段时间更新即可
3. 最后，value(数据)。限定时段与票池，可以减少下载量

## 限额方式
1. 万得。按单元格计量，所以应当尽量减少下载时的行列。比如按年下载，取每年的票池，减少数据量
2. 聚宽。按行计量，限额大时随便下，限额小时则用宽表代替长表减少数据量，`get_price`在每日更新时用`get_bars`代替

## 文件名分类
按文件名分成了时间文件和非时间文件
1. 非时间文件，指定的参数做为文件名
2. 时间文件。
    1. 前后两个日期，文件名就是两个时间。
    2. 一个日期，是两个日期的特例
    
## 文件名中时间处理
1. 左闭右闭
    - 连续查询时，需要生成下一次的查询时间，否则数据重复
    - 文件合并时没有多大区别，直接合并即可
    - 例：[20220101, 20221231]
2. 左闭右开
    - 查询结束需要生成下一次的时间做为文件名，但实际此文件中又没有此时间，容易误解
    - 部分K线行情，使用此方案，但标签打在右，很别扭，后期处理不便
    - 例：[20220101, 20230101)
3. 左开右闭
    - 基本不可能使用此方案，不符合用户习惯
    - 例：(20211231, 20221231]
    
## 是否更新
1. 文件名中无时间信息
    - 文件修改时间太近的不更新。防重复下载
2. 文件名中有时间信息
    - 文件修改时间太近的不更新。防重复下载
    - 文件名中有时间的，结束时间半个月前了，不更新。因为内容基本不会再动了
总结：数据很老不动，数据太新也不动

## 数据种类
1. 数据量少，全查无所谓，并且历史可能被改写。比如交易日，股票基本信息等。全查即可
2. 数据量大，增量查询。历史基本不变。是否能补数？
    1. 如果按天存，想补哪天就补哪天，只要删了那天的记录，然后参数中设置一下即可
    2. 如果多天存一个文件，更新起来比较麻烦，同时没有索引了，不知道如何存进去
    3. parquet支持文件夹加载，可以将历史文件加载合并，减少文件大小

## 财务
1. 数据已经按报告期发布好了，按报告期下载即可，也按报告期存文件
3. 数据按股票存的，只能按股票下载了。但由于股票太多，只能先查询哪些股票发布了公告，然后据此进行查询。按股票存文件

## 合并与不合并的区别
1. 合并后，数据压缩效率更高，可用专业工具来进行大文件同步
2. 不合并，正好与断点续传的机制一样，方便网络不好的情况下同步
3. 不合并，可以对请求进行映射，实现类似于API的服务。

## 示例
```bash
├─tushare_api
│  ├─daily
│  │      20200123T000000__20200123T000000.parquet
│  │      20220214T000000__20220214T000000.parquet
│  ├─namechange
│  │      20180101T000000__20181231T000000.parquet
│  │      20190101T000000__20191231T000000.parquet
│  │      20200101T000000__20201231T000000.parquet
│  │      20210101T000000__20211231T000000.parquet
│  │      20220101T000000__20221231T000000.parquet
│  ├─stock_basic
│  │      SSE__D.parquet
│  │      SSE__L.parquet
│  │      SSE__P.parquet
│  │      SZSE__D.parquet
│  │      SZSE__L.parquet
│  │      SZSE__P.parquet
│  │      
│  └─trade_cal
│          SSE.parquet
│          SZSE.parquet
```