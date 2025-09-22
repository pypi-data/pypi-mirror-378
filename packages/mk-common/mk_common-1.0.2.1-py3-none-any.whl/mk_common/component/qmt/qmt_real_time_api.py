import pandas as pd
from loguru import logger
from xtquant import xtdata


# 获取股票实时行情数据
# stockStatus 0 新股  7 停牌 5 正常交易
# askPrice 是卖价
# bidPrice 是买价
def get_qmt_real_time_quotes(symbol_list):
    try:
        res = xtdata.get_full_tick(symbol_list)
        records = []
        for symbol, stock_data in res.items():
            record = stock_data.copy()  # 创建字典副本避免修改原始数据
            record['symbol'] = symbol  # 添加股票代码列
            records.append(record)  # 添加到列表
        # 一次性转换为DataFrame
        real_time_quotes_df = pd.DataFrame(records)
        return real_time_quotes_df
    except BaseException as e:
        logger.error("获取实时行情出现异常:{}", e)


if __name__ == '__main__':

    while True:
        symbol_one_test = ['002067.SZ']
        df = get_qmt_real_time_quotes(symbol_one_test)
        logger.info(df['askPrice'])
        df[['sell_1', 'sell_2', 'sell_3', 'sell_4', 'sell_5']] = (
            df['askPrice']
            .apply(lambda x: sorted(x))  # 排序
            .apply(pd.Series)  # 拆分
        )
        df[['buy_1', 'buy_2', 'buy_3', 'buy_4', 'buy_5']] = (
            df['bidPrice']
            .apply(pd.Series)  # 拆分
        )
        logger.info(df)
