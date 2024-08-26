import sys
sys.path.append('..')
from ezQt.saver import ezQtSaver


if __name__ == '__main__':
    ezQtSaver.save_stock_fund_day()
    ezQtSaver.save_stock_fund_adj()