import json
import time
import pandas as pd


def ds2float(date):
    """
    explanation:
        转换日期时间字符串为浮点数的时间戳

    params:
        * date->
            含义: 日期时间
            类型: str
            参数支持: []

    return:
        time
    """
    if not date:
        return date
    datestr = pd.Timestamp(date).strftime("%Y-%m-%d")
    date = time.mktime(time.strptime(datestr, '%Y-%m-%d'))
    return date

def date_conver_to_new_format(date_str):
    time_now = time.strptime(date_str[0:10], '%Y-%m-%d')
    return '{:0004}{:02}{:02}'.format(
        int(time_now.tm_year),
        int(time_now.tm_mon),
        int(time_now.tm_mday)
    )
    
def json_from_pandas(data):
    """
    explanation:
        将pandas数据转换成json格式		

    params:
        * data ->:
            meaning: pandas数据
            type: null
            optional: [null]

    return:
        dict

    demonstrate:
        Not described

    output:
        Not described
    """

    """需要对于datetime 和date 进行转换, 以免直接被变成了时间戳"""
    if 'datetime' in data.columns:
        data.datetime = data.datetime.apply(str)
    if 'date' in data.columns:
        data.date = data.date.apply(str)
    return json.loads(data.to_json(orient='records'))