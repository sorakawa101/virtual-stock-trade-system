import streamlit as st
from sqlalchemy import text
import numpy as np
import pandas as pd
import datetime
import talib as ta

df_stock_code = pd.read_excel("./src/data_j.xls")


# 銘柄コードの数字（文字列）を企業名に変換する関数
def StockCodeStr_to_CorpName(s):

    # 銘柄コードに一致する企業名
    # コードが一致する行のみを抽出したDF
    df_corp = df_stock_code[df_stock_code['コード']
                            == int(s.split('.JP')[0])]

    # DFから銘柄名のカラムだけを抽出したseries（DFの最小単位）
    series_corp = df_corp['銘柄名']

    # seriesから企業名の値だけを抽出
    corp_name = series_corp.iloc[-1]

    return corp_name


# MySQLから指定したテーブルをDFとして取得する関数
def ConnectMySQL_and_GetTable(table):
    # MySQLと接続
    # Initialize connection.
    connection = st.experimental_connection('mysql', type='sql')

    df_stock_code_list = connection.query(
        f'SELECT * from {table};')

    return df_stock_code_list



# MySQLにクエリとデータを渡して、クエリを実行する関数
def ConnectMySQL_and_ExecuteQuery(query):
    # MySQLと接続
    # Initialize connection.
    connection = st.experimental_connection('mysql', type='sql')

    with connection.session as s:
        s.execute(query)
        s.commit()


def Reset_ConnectionMySQL():
    connection = st.experimental_connection('mysql', type='sql')
    connection.reset()


# Dateカラムを生成する関数
def Get_Date(df):
    # df["Date"] = df.index
    # df["Date"].str.split(" ").str.get(0)
    # ! series.str.~ はシリーズをまとめて操作できるので便利．ただし，シリーズの中身がstrでないと使えない．変換方法はstr()は使えなかった
    # ! df["Date"] = df.index.astype~ とまとめると最遠の日付一つが全てのシリーズに格納されてしまったので2行に分割
    df["Date"] = df.index
    df["Date"] = df["Date"].astype(str).str.split(pat=' ', expand=True)[0]

# 非表示にしたい日付（＝株式市場が閉場している日付）リストを取得する関数
def Get_Unnecessary_DateList(df):
    #日付一覧を取得
    d_all = pd.date_range(start=df.index[0],end=df.index[-1])

    #株価データの日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in df.index]

    # 株価データの日付データに含まれていない日付を抽出
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs]

    return d_breaks

# ローソク足チャート上で売買タイミングを取得する関数
def Get_Buy_or_Sell_Timing(df):
    engulfing = ta.CDLENGULFING(df["Open"], df["High"], df["Low"], df["Close"])
    df["engulfing_text"] = engulfing.replace({ 100: "Buy", -100: "Sell", 0: "" })
    df["engulfing_marker"] = (engulfing/100 * df["High"]).abs().replace({ 0: np.nan })
    df.tail()


# 平均移動線を取得する関数
def Get_SimpleMovingAverage(df):
    # SMAを計算
    # df["SMA20"] = df["Close"].rolling(window=20).mean()
    # df["SMA50"] = df["Close"].rolling(window=50).mean()
    # df["SMA200"] = df["Close"].rolling(window=200).mean()

    df["SMA20"] = ta.SMA(df["Close"], timeperiod=20)
    df["SMA50"] = ta.SMA(df["Close"], timeperiod=50)
    df["SMA200"] = ta.SMA(df["Close"], timeperiod=200)

    df.tail()


# パーフェクトオーダーを取得する関数
def Get_PerfectOrder(df):
    df["PerfectOrder"] = np.where((df["SMA20"]>df["SMA50"]) & (df["SMA50"] > df["SMA200"]), 1, 0)
    df.tail()


# パーフェクトオーダーの期間を取得する関数
def Get_When_PerfectOrder(df):
    df["PerfectOrder_diff"] = df["PerfectOrder"].diff()

    # PerfectOrder_diffが１あるいは-1のデータのみを抽出してShiftでデータを1日ずらす --> これが終了日となる
    df["end_date"] = df[df["PerfectOrder_diff"].isin([1, -1])]["Date"].shift(-1)

    # PerfectOrder_diffが1となっている部分を抽出 --> パーフェクトオーダーが始まった日のデータだけを抽出
    df_po = df[df["PerfectOrder_diff"]==1]

    return df_po.head()[["Date", "end_date"]]


# MACDを計算する関数
def Calc_MACD(df):
    FastEMA_period = 12  # 短期EMAの期間
    SlowEMA_period = 26  # 長期EMAの期間
    SignalSMA_period = 9  # SMAを取る期間
    df["MACD"] = df["Close"].ewm(span=FastEMA_period).mean() - df["Close"].ewm(span=SlowEMA_period).mean()
    df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
    return df


# RSIを計算する関数
def Calc_RSI(df):
    # 前日との差分を計算
    df_diff = df["Close"].diff(1)

    # 計算用のDataFrameを定義
    df_up, df_down = df_diff.copy(), df_diff.copy()

    # df_upはマイナス値を0に変換
    # df_downはプラス値を0に変換して正負反転
    df_up[df_up < 0] = 0
    df_down[df_down > 0] = 0
    df_down = df_down * -1

    # 期間14でそれぞれの平均を算出
    df_up_sma14 = df_up.rolling(window=14, center=False).mean()
    df_down_sma14 = df_down.rolling(window=14, center=False).mean()

    # RSIを算出
    df["RSI"] = 100.0 * (df_up_sma14 / (df_up_sma14 + df_down_sma14))

    return df


def Get_TechnicalIndex(df):
    df = Calc_MACD(df)
    df = Calc_RSI(df)
    df.head()