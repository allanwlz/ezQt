import os
import datetime
import pymongo
import pandas as pd
from ezQt.setting import EzQtSETTING, DATABASE
from ezQt.utils import ds2float, date_conver_to_new_format, json_from_pandas, code_assetType_convert

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
                            adj='bfq',  # 新参数，指定复权类型
                            collections=DATABASE.stock_fund_day,
                            adj_collections=DATABASE.stock_fund_adj):  # 复权信息的集合
        '''
        获取股票基金日线数据，并根据复权类型调整价格
        :param code: 股票代码
        :param start: 开始日期
        :param end: 结束日期
        :param adj: 复权类型 ('qfq', 'hfq', 'bfq')
        :param collection: 集合名称
        :param adj_collections: 复权信息的集合名称
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
        if not self.check_date_valid(start):
            print("Invalid Start Data", start)
            return res
        
        if not self.check_date_valid(end):
            print("Invalid End Data", end)
            return res
        
        cursor = collections.find(
            {
                'code': {
                    '$in': code
                }, 
                'date': {
                    '$lte': end,
                    '$gte': start
                }
            }
        ).sort('date', pymongo.ASCENDING)
        res = pd.DataFrame([item for item in cursor])
        if res.empty:
            return res
        # 获取复权因子
        if adj != 'bfq':
            adj_cursor = adj_collections.find(
                {
                    'code': {
                        '$in': code
                    },
                    'date': {
                        '$lte': end,
                        '$gte': start
                    }
                }
            ).sort('date', pymongo.ASCENDING)
            adj_df = pd.DataFrame([item for item in adj_cursor])
            if not adj_df.empty:
                adj_df['date'] = pd.to_datetime(adj_df['date'], format='%Y-%m-%d')
                res['date'] = pd.to_datetime(res['date'], format='%Y-%m-%d', utc=False)
                res = res.merge(adj_df[['code', 'date', 'adj_factor']], on=['code', 'date'], how='left')
                if adj == 'qfq':
                    # 对价格进行前复权调整
                    res['adj_factor'] = res.groupby('code')['adj_factor'].transform(lambda x: x / x.iloc[-1])
                elif adj == 'hfq':
                    # 对价格进行后复权调整
                    res['adj_factor'] = res.groupby('code')['adj_factor'].transform(lambda x: x / x.iloc[0])
                # 计算复权后的价格
                for col in ['open', 'high', 'low', 'close']:
                    res[col] = (res[col] * res['adj_factor']).round(3)
                res.drop(columns=['adj_factor'], inplace=True)
        
        try:
            
            res = res.assign(
                date=pd.to_datetime(res['date'], format='%Y-%m-%d', utc=False)
            ).drop_duplicates(
                ['date', 'code']
            ).query('volume>1'
            ).set_index('date', drop=False).sort_index()
            columns_to_select = [
                'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'date'
            ]
            if 'turnover_rate' in res.columns:
                columns_to_select.append('turnover_rate')
            res = res.loc[:, columns_to_select]
        except Exception as e:
            print(e)
            res = None
        return res

ezQtFetcher = EzQtDataFetch()