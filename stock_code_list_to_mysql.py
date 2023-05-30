from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd
import requests


# JPXから銘柄コードのリストをExcelとして入手し、それをDFに変換してMySQLに入力する関数
def get_stock_code_list_from_excel():
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    r = requests.get(url)

    with open('data_j.xls', 'wb') as output:
        output.write(r.content)

    stocklist = pd.read_excel("./data_j.xls")
    stocklist.loc[stocklist["市場・商品区分"] == "市場第一部（内国株）",
                  ["コード", "銘柄名", "33業種コード", "33業種区分", "規模コード", "規模区分"]
                  ]
    return stocklist


def input_df_to_mysql(table_name):
    # .env ファイルをロードして環境変数へ反映
    load_dotenv()

    # MySQLの接続情報
    user = os.getenv('MYSQL_USER')
    host = os.getenv('MYSQL_HOST')
    password = os.getenv('MYSQL_PASSWORD')
    database = 'scraping_stock_data'

    url = f'mysql+pymysql://{user}:{password}@{host}/{database}'

    # MySQLに接続するためのエンジン
    # 記述テンプレ: engine = create_engine('mysql://<user>:<password>@<host>/<database>?charset=utf8')
    engine = create_engine(url, echo=False)

    # DFを用意
    df = get_stock_code_list_from_excel()

    # DFをMySQLに入力
    # ! ここのテーブル名の指定を既存のもので実行すると接続エラーが吐かれる（１時間悩んだ）
    df.to_sql(table_name, url, index=None)


# 格納したいテーブルを指定
table_name = 'stock_code_list'
input_df_to_mysql(table_name)
