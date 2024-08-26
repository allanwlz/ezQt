import os
import datetime
import pymongo
import pandas as pd
from ezQt.setting import EzQtSETTING, DATABASE
from ezQt.utils import ds2float, date_conver_to_new_format, json_from_pandas

class EzQtDataFetch():
    def __init__(self):
        pass
    
    def check_date_valid(self, date):
        '''
        检查日期是否有效
        :param date: 日期
        :return: bool
        '''
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            return True
        except:
            return False
        
    def fetch_stock_fund_day(self, 
                             code,
                             start='all',
                             end=None,
                             collections=DATABASE.stock_fund_day):
        '''
        获取股票基金日线数据
        :param code: 股票代码
        :param start: 开始日期
        :param end: 结束日期
        :param collection: 集合名称
        :return: DataFrame
        '''
        end = start if end is None else end
        start = str(start)[0:10]
        end = str(end)[0:10]
        if start == 'all':
            start = '1990-01-01'
            end = str(datetime.date.today())
        if isinstance(code, str):
            code = [code]
        res = None
        print(start, end)
        if self.check_date_valid(end) and self.check_date_valid(start):
            cursor = collections.find(
                {
                    'ts_code': {
                        '$in': code
                    }, 
                    'date': {
                        '$lte': end,
                        '$gte': start
                    }
                }
            )
            res = pd.DataFrame([item for item in cursor])
            try:
                res = res.assign(
                    date=pd.to_datetime(res.date, utc=False)
                ).drop_duplicates(
                    (
                        [ 'date', 
                         'code']
                        )
                ).query('volume>1'
                ).set_index('date', drop=False)
                res = res.loc[:,
                    [
                        'code',
                        'open',
                        'high',
                        'low',
                        'close',
                        'volume',
                        'amount',
                        'turnover_rate',
                        'date'
                    ]]
            except:
                res = None
        return res

ezQtFetcher = EzQtDataFetch()