import requests
import time
import datetime
import tushare as ts
import pandas as pd
import pymongo
import sys
import dateutil.parser
from tqdm import tqdm
from bs4 import BeautifulSoup
from ezQt.config import TsConfig
from ezQt.setting import EzQtSETTING, DATABASE
from ezQt.utils import ds2float, date_conver_to_new_format, json_from_pandas


class EzQtDataSaver():
    def __init__(self) -> None:
        pass
    
    def set_token(self, token=None):
        try:
            if token is None:
                token = EzQtSETTING.get_config('TSPRO', 'token', "none")
                if token == "none":
                    response = requests.get(TsConfig.TOKEN_URL)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        token = soup.prettify().split('"')[1]
                    else:
                        raise Exception('Failed to retrieve the web page. Status code: {response.status_code}')
                    print("set token: ", token)
                    EzQtSETTING.set_config('TSPRO', 'token', token)
            else:
                EzQtSETTING.set_config('TSPRO', 'token', token)
            ts.set_token(token)
        except:
            if token is None:
                print('请设置tushare的token')
            else:
                print('请升级tushare 至最新版本 pip install tushare -U')
        
    def get_pro(self):
        try:
            self.set_token()
            pro = ts.pro_api()
        except Exception as e:
            if isinstance(e, NameError):
                print('请设置tushare pro的token凭证码')
            else:
                print('请升级tushare 至最新版本 pip install tushare -U')
                print(e)
            pro = None
        return pro
    
    def code_assetType_convert(self, code):
        """ 根据代码自动判断类型及交易所
        """
        asset_type = 'E'
        if code[:2] in ['00', '30']:
            code += '.SZ'
        elif code[:2] in ['60', '68']:
            code += '.SH'
        elif code[:2] in ['15', '16', '18']:
            asset_type = 'FD'
            code += '.SZ'
        elif code[:2] in ['50', '51', '52']:
            asset_type = 'FD'
            code += '.SH'
        return code, asset_type

    def _get_subscription_type(self, if_fq):
        if str(if_fq) in ['qfq', '01']:
            if_fq = 'qfq'
        elif str(if_fq) in ['hfq', '02']:
            if_fq = 'hfq'
        elif str(if_fq) in ['bfq', '00']:
            if_fq = None
        else:
            print('wrong with fq_factor! using qfq')
            if_fq = 'qfq'
        return if_fq

    def get_tushare_time(self, t):
        date = dateutil.parser.parse(t)
        data_stamp = date.strftime("%Y%m%d")
        return data_stamp

    def time_split(self, start, end):
        """
        由于TUSHARE对每次查询对查询上线有限制，所以需要分批查询，这里需要按年分别查询结果
        """
        start = start.replace('-', '')
        end = end.replace('-', '')
        assert len(start) == 8
        assert len(end) == 8
        start_year, start_mon, start_day = start[:4], start[4:6], start[6:8]
        end_year, end_mon, end_day = end[:4], end[4:6], end[6:8]
        if start_mon + start_day < end_mon + end_day:
            starts = [start]
            ends = [start_year+end_mon+end_day]
        else:
            starts = [start]
            start_year=str(int(start_year) + 1)
            ends = [start_year+end_mon+end_day]
        init_mon = end_mon
        init_day = "%02d" % (int(end_day) + 1,)
        for year in range(int(start_year), int(end_year)):
            batch_start = str(year) + init_mon + init_day
            batch_end = str(year + 1) + end_mon + end_day
            starts.append(batch_start)
            ends.append(batch_end)
        return starts, ends

    def fetch_stock_fund_list(self):
        def fetch_basic_list():
            stock_basic = None
            fund_basic = None
            try:
                pro = self.get_pro()
                stock_basic = pro.stock_basic(
                    exchange='',
                    list_status='L',
                    fields='ts_code,'
                    'symbol,'
                    'name,'
                    'area,industry,list_date'
                )
                fund_basic = pro.fund_basic(market='E')
            except Exception as e:
                print(e)
                print('except when fetch stock basic')
                time.sleep(4)
                stock_basic = fetch_basic_list()
            stock_list = [x.split('.')[0] for x in list(stock_basic.ts_code)]
            fund_list = [x.split('.')[0] for x in list(fund_basic.ts_code)]
            return stock_list, fund_list
        return fetch_basic_list()
    
    def fetch_stock_fund_day(self, name, start='', end='', if_fq='bfq', type_='pd'):
        data_list = []
        if not isinstance(name, list):
            name = [name]     
        for code in name:
            ts_code, asset_type = self.code_assetType_convert(code)
            starts, ends = self.time_split(start, end)
            code_data = []
            for _start, _end in zip(starts, ends):
                def fetch_data():
                    data = None
                    try:
                        time.sleep(0.1)
                        pro = self.get_pro()
                        data = ts.pro_bar(
                            api=pro,
                            ts_code=ts_code,
                            asset=asset_type,
                            adj=self._get_subscription_type(if_fq),
                            start_date=_start,
                            end_date=_end,
                            freq='D',
                            factors=['tor',
                                    'vr']
                        ).sort_index()
                    except Exception as e:
                        print(e)
                        print('except when fetch data of ' + str(name))
                    return data                      
                data = fetch_data()
                code_data.append(data)
            code_data = pd.concat(code_data[::-1], axis=0)
            data_list.append(code_data)
        data = pd.concat(data_list)
        data['volume'] = data['vol']
        data = data.drop('vol', axis=1)
        data['code'] = data['ts_code'].apply(lambda x: str(x)[0:6])
        data['fqtype'] = if_fq
        if type_ in ['json']:
            data_json = json_from_pandas(data)
            return data_json
        elif type_ in ['pd', 'pandas', 'p']:
            data['date'] = pd.to_datetime(data['trade_date'], utc=False, format='%Y%m%d')
            data = data.set_index('date', drop=False)
            data['date'] = data['date'].apply(lambda x: str(x)[0:10])
            return data        
    
    def fetch_stock_fund_adj(self, codes, start='', end='', if_qfq=False):
        pro = self.get_pro()
        if not isinstance(codes, list):
            codes = [codes]
        start = self.get_tushare_time(start)
        end = self.get_tushare_time(end)
        adj_list = []
        for code in codes:
            ts_code, asset_type = self.code_assetType_convert(code)
            if asset_type == 'E':
                adj = pro.adj_factor(
                    ts_code=ts_code,
                    start_date=start,
                    end_date=end
                )
                if if_qfq:
                    end_adj = pro.adj_factor(
                        ts_code=ts_code,
                        trade_date=end
                    ).loc[0, 'adj_factor']
                    adj['adj'] = adj['adj_factor'].apply(lambda x: x / end_adj)
            elif asset_type == 'FD':
                adj = pro.fund_adj(
                    ts_code=ts_code,
                    start_date=start,
                    end_date=end
                )
                if if_qfq:
                    end_adj = pro.fund_adj(
                        ts_code=ts_code,
                        trade_date=end
                    ).loc[0, 'adj_factor']
                    adj['adj'] = adj['adj_factor'].apply(lambda x: x / end_adj)
            else:
                adj = None
            adj_list.append(adj)
        adj = pd.concat(adj_list)
        adj['code'] = adj['ts_code'].apply(lambda x: str(x)[0:6])
        adj['date'] = pd.to_datetime(adj['trade_date'], utc=False, format='%Y%m%d')
        adj['date'] = adj['date'].apply(lambda x: str(x)[0:10])
        adj = adj.set_index(['date', 'code'])
        return adj
    
    def save_stock_fund_list(self, client=DATABASE):
        stock_list, fund_list = self.fetch_stock_fund_list()
        date = str(datetime.date.today())
        date_stamp = ds2float(date)
        coll = client.stock_info_tushare
        coll.insert(
            {
                'date': date,
                'date_stamp': date_stamp,
                'stock': {
                    'code': stock_list
                }
            }
        )
        coll = client.fund_info_tushare
        coll.insert(
            {
                'date': date,
                'date_stamp': date_stamp,
                'stock': {
                    'code': fund_list
                }
            }
        )
    
    def save_stock_fund_day(self, client=DATABASE):
        stock_list, fund_list = self.fetch_stock_fund_list()
        coll_stock_fund_day = client.stock_fund_day
        coll_stock_fund_day.create_index(
            [("code",
            pymongo.ASCENDING),
            ("date_stamp",
            pymongo.ASCENDING)]
        )
        end_date = self.now_time
        err = []
        for ts_code in tqdm(stock_list + fund_list):
            try:
                ref_count = coll_stock_fund_day.count_documents({'code': str(ts_code)[0:6]})
                # 增量更新
                if ref_count > 0:
                    last_document = coll_stock_fund_day.find({'code': str(ts_code)[0:6]}).sort('date', pymongo.DESCENDING).limit(1)[0]
                    start_date_new_format = last_document['trade_date']
                    start_date = last_document['date']
                    if start_date_new_format != end_date:
                        coll_stock_fund_day.insert_many(
                            json_from_pandas(
                                self.fetch_stock_fund_day(
                                    str(ts_code),
                                    start_date,
                                    end_date,
                                    'bfq'
                                )
                            )
                        )
                        print(f"Saving {ts_code} from {start_date} to {end_date}")
                        time.sleep(1.0)
                else:
                    start_date = '1990-01-01'
                    if start_date != end_date:
                        coll_stock_fund_day.insert_many(
                            json_from_pandas(
                                self.fetch_stock_fund_day(
                                    str(ts_code),
                                    start_date,
                                    end_date,
                                    'bfq'
                                )
                            )
                        )
                        print(f"Saving {ts_code} from {start_date} to {end_date}")
                        time.sleep(1.0)
            except Exception as e:
                print(e)
                err.append(str(ts_code))
                time.sleep(10.0)
            sys.stdout.flush()
            
    def save_stock_fund_adj(self, client=DATABASE):
        stock_list, fund_list = self.fetch_stock_fund_list()
        coll_stock_fund_adj = client.stock_fund_adj
        coll_stock_fund_adj.create_index(
            [("code",
            pymongo.ASCENDING),
            ("date_stamp",
            pymongo.ASCENDING)]
        )
        end_date = self.now_time
        err = []
        for ts_code in tqdm(stock_list + fund_list):
            try:
                ref_count = coll_stock_fund_adj.count_documents({'code': str(ts_code)[0:6]})
                # 增量更新
                if ref_count > 0:
                    last_document = coll_stock_fund_adj.find({'code': str(ts_code)[0:6]}).sort('date', pymongo.DESCENDING).limit(1)[0]
                    start_date_new_format = last_document['trade_date']
                    start_date = last_document['date']
                    if start_date_new_format != end_date:
                        coll_stock_fund_adj.insert_many(
                            json_from_pandas(
                                self.fetch_stock_fund_adj(
                                    str(ts_code),
                                    start_date,
                                    end_date
                                )
                            )
                        )
                        print(f"Saving {ts_code} from {start_date} to {end_date}")
                        time.sleep(1.0)
                else:
                    start_date = '1990-01-01'
                    if start_date != end_date:
                        coll_stock_fund_adj.insert_many(
                            json_from_pandas(
                                self.fetch_stock_fund_adj(
                                    str(ts_code),
                                    start_date,
                                    end_date
                                )
                            )
                        )
                        print(f"Saving {ts_code} from {start_date} to {end_date}")
                        time.sleep(1.0)
            except Exception as e:
                print(e)
                time.sleep(10.0)
                err.append(str(ts_code))
        
    @property
    def trade_date_sse(self):
        pro = self.get_pro()
        df = pro.trade_cal(exchange='', start_date='19901219', end_date=datetime.datetime.now().strftime("%Y%m%d"))
        df = df.sort_values('cal_date', ascending=True)
        trade_date_sse = []
        for i in range(len(df)):
            if df['is_open'][i] == 1:
                trade_date_sse.append(datetime.datetime.strptime(df['cal_date'][i], "%Y%m%d").strftime("%Y-%m-%d"))
        trade_date_sse.sort()
        return trade_date_sse
    
    def get_real_date(self, date, towards=-1):
        date = str(date)[0:10]
        if towards == 1:
            if pd.Timestamp(date) >= pd.Timestamp(self.trade_date_sse[-1]):
                return self.trade_date_sse[-1]
            while date not in self.trade_date_sse:
                date = str(
                    datetime.datetime.strptime(str(date)[0:10], "%Y-%m-%d")
                    + datetime.timedelta(days=1)
                )[0:10]
            else:
                return str(date)[0:10]
        elif towards == -1:
            if pd.Timestamp(date) <= pd.Timestamp(self.trade_date_sse[0]):
                return self.trade_date_sse[0]
            while date not in self.trade_date_sse:
                date = str(
                    datetime.datetime.strptime(str(date)[0:10], "%Y-%m-%d")
                    - datetime.timedelta(days=1)
                )[0:10]
            else:
                return str(date)[0:10]
    
    @property
    def now_time(self):
        real_date = str(self.get_real_date(str(datetime.date.today() -
                                            datetime.timedelta(days=1)),
                                            -1))
        str_now = real_date + ' 17:00:00' if datetime.datetime.now().hour < 15 \
            else str(self.get_real_date(str(datetime.date.today()),
                                        -1)) + ' 15:00:00'
        return date_conver_to_new_format(str_now)    

ezQtSaver = EzQtDataSaver()