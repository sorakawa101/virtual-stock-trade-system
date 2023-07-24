import streamlit as st
import numpy as np
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# SoftBank Stock data from Stooq.com
# reference https://seanmemo.com/234/

from pandas_datareader import data

import mod


# st.title('Virtual Stock Trade System')
# st.header('Information')


# DF：JPXから取得した銘柄コード一覧をMySQLから取得
df_stock_code = mod.ConnectMySQL_and_GetTable('stock_code_list')
# df_stock_code = pd.read_excel("./src/data_j.xls")

with st.sidebar:
    # 銘柄コードを入力
    stock_code = st.text_input(
        '銘柄コード',
        '9984.JP'
    )

    # 銘柄コードを入力
    stock_code2 = st.text_input(
        '銘柄コード',
        ''
    )

    # データ取得の開始日
    start = st.date_input(
        '開始日',
        # デフォルト値は約3ヶ月前の日付
        datetime.date.today() - datetime.timedelta(weeks=132)
    )

    # データ取得の最終日
    end = st.date_input(
        '終了日',
        # デフォルト値は今日の日付
        datetime.date.today()
    )

    corp = mod.StockCodeStr_to_CorpName(stock_code)

    if stock_code2:
        corp2 = mod.StockCodeStr_to_CorpName(stock_code2)

    # 現在洗濯中の情報を表示
    st.info(f'現在、\"{corp}\"\tの\t{start}〜{end}\tにおける株価データを表示中', icon=None)

    # DF：指定した銘柄の株式データ
    # ! ここでiloc[::-1]でDFを逆順にしておくことでグラフ表示がうまくいく
    df_stock_data = data.DataReader(stock_code, 'stooq', start, end).iloc[::-1]
    df_stock_data2 = data.DataReader(stock_code2, 'stooq', start, end).iloc[::-1]



# 比較対象の企業を設定した場合（2社の比較表示）
if stock_code2:
    data_col1, data_col2 = st.columns(2)

    with data_col1:

        # 選択中の企業名を表示
        st.subheader(f'{corp}（{start}~{end}）')

        # 各データの前日比
        st.write(f'前日比')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Open",     df_stock_data.iat[0, 0], int(
            df_stock_data.iat[0, 0]-df_stock_data.iat[1, 0]))
        col2.metric("High",     df_stock_data.iat[0, 1], int(
            df_stock_data.iat[0, 1]-df_stock_data.iat[1, 1]))
        col3.metric("Low",      df_stock_data.iat[0, 2], int(
            df_stock_data.iat[0, 2]-df_stock_data.iat[1, 2]))
        col4.metric("Close",    df_stock_data.iat[0, 3], int(
            df_stock_data.iat[0, 3]-df_stock_data.iat[1, 3]))
        col5.metric("Volume",   df_stock_data.iat[0, 4], int(
            df_stock_data.iat[0, 4]-df_stock_data.iat[1, 4]))


        with st.expander("前週・前月比"):
            # 各データの前週比
            st.write(f'前週比')
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Open",     df_stock_data.iat[0, 0], int(
                df_stock_data.iat[0, 0]-df_stock_data.iat[5, 0]))
            col2.metric("High",     df_stock_data.iat[0, 1], int(
                df_stock_data.iat[0, 1]-df_stock_data.iat[5, 1]))
            col3.metric("Low",      df_stock_data.iat[0, 2], int(
                df_stock_data.iat[0, 2]-df_stock_data.iat[5, 2]))
            col4.metric("Close",    df_stock_data.iat[0, 3], int(
                df_stock_data.iat[0, 3]-df_stock_data.iat[5, 3]))
            col5.metric("Volume",   df_stock_data.iat[0, 4], int(
                df_stock_data.iat[0, 4]-df_stock_data.iat[5, 4]))


            # 各データの前月比
            st.write(f'前月比')
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Open",     df_stock_data.iat[0, 0], int(
                df_stock_data.iat[0, 0]-df_stock_data.iat[23, 0]))
            col2.metric("High",     df_stock_data.iat[0, 1], int(
                df_stock_data.iat[0, 1]-df_stock_data.iat[23, 1]))
            col3.metric("Low",      df_stock_data.iat[0, 2], int(
                df_stock_data.iat[0, 2]-df_stock_data.iat[23, 2]))
            col4.metric("Close",    df_stock_data.iat[0, 3], int(
                df_stock_data.iat[0, 3]-df_stock_data.iat[23, 3]))
            col5.metric("Volume",   df_stock_data.iat[0, 4], int(
                df_stock_data.iat[0, 4]-df_stock_data.iat[23, 4]))




        # 出来高のエリアチャート

        # figを定義
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.2, 0.2, 0.7])


        # ローソク足チャートを表示
        fig.add_trace(
            go.Candlestick(x=df_stock_data.index, open=df_stock_data["Open"], high=df_stock_data["High"], low=df_stock_data["Low"], close=df_stock_data["Close"], showlegend=False),
            row=1, col=1
        )
        mod.Get_Buy_or_Sell_Timing(df_stock_data)
        fig.add_trace(go.Scatter(x=df_stock_data.index,
                                y=df_stock_data["engulfing_marker"],
                                mode="markers+text",
                                text=df_stock_data["engulfing_text"],
                                textposition="top center",
                                name="ENGULFING BAR",
                                marker = { "size": 8, "color": "blue", "opacity": 0.6 },
                                textfont = {"size": 8, "color": "black" }))


        # 移動平均線
        mod.Get_SimpleMovingAverage(df_stock_data)
        fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["SMA20"], name="SMA20", mode="lines"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["SMA50"], name="SMA50", mode="lines"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["SMA200"], name="SMA200", mode="lines"), row=1, col=1)

        # mod.Get_Date(df_stock_data)
        # mod.Get_PerfectOrder(df_stock_data)
        # df_po = mod.Get_When_PerfectOrder(df_stock_data)
        # for i in range(len(df_po)):
        #     row = df_po.iloc[i]
        #     fig.add_vrect(x0=row["Date"], x1=row["end_date"], line_width=0, fillcolor="blue", opacity=0.1, row=1, col=1)


        # MACD
        mod.Get_TechnicalIndex(df_stock_data)
        fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["MACD"], mode="lines", showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["Signal"], mode="lines", showlegend=False), row=3, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["RSI"], mode="lines", showlegend=False), row=4, col=1)


        # 出来高の棒グラフを表示
        fig.add_trace(
            go.Bar(x=df_stock_data.index, y=df_stock_data["Volume"], showlegend=False),
            row=2, col=1
        )
        # Layout
        fig.update_layout(
            # title={
            #     "text": "トヨタ自動車(7203)の日足チャート",
            #     "y":0.9,
            #     "x":0.5,
            # },
            height=700
        )

        fig.update_xaxes(
            rangebreaks=[dict(values=mod.Get_Unnecessary_DateList(df_stock_data))], # 非営業日を非表示設定
            tickformat='%Y/%m/%d' # 日付のフォーマット変更
        )

        # 日付のフォーマット変更
        fig.update_xaxes(tickformat='%Y/%m/%d')

        # ラベル名の設定とフォーマット変更（カンマ区切り）
        fig.update_yaxes(separatethousands=True, title_text="株価", row=1, col=1)
        fig.update_yaxes(title_text="出来高", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="RSI", row=4, col=1)

        # 棒グラフを非表示にする場合は以下を適用
        fig.update(layout_xaxis_rangeslider_visible=False)
        # 描画
        st.plotly_chart(fig, use_container_width=True)




        # 取得した株価データの表
        # 選択中の企業名を表示
        # 表の生成
        with st.expander('表'):
            # st.table(df_stock_data.loc[:, :'Volume'])
            st.dataframe(df_stock_data)








    # 比較対象の2社目
    with data_col2:

        # 選択中の企業名を表示
        st.subheader(f'{corp2}（{start}~{end}）')

        # 各データの前日比
        st.write(f'前日比')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Open",     df_stock_data2.iat[0, 0], int(
            df_stock_data2.iat[0, 0]-df_stock_data2.iat[1, 0]))
        col2.metric("High",     df_stock_data2.iat[0, 1], int(
            df_stock_data2.iat[0, 1]-df_stock_data2.iat[1, 1]))
        col3.metric("Low",      df_stock_data2.iat[0, 2], int(
            df_stock_data2.iat[0, 2]-df_stock_data2.iat[1, 2]))
        col4.metric("Close",    df_stock_data2.iat[0, 3], int(
            df_stock_data2.iat[0, 3]-df_stock_data2.iat[1, 3]))
        col5.metric("Volume",   df_stock_data2.iat[0, 4], int(
            df_stock_data2.iat[0, 4]-df_stock_data2.iat[1, 4]))


        with st.expander("前週・前月比"):
            # 各データの前週比
            st.write(f'前週比')
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Open",     df_stock_data2.iat[0, 0], int(
                df_stock_data2.iat[0, 0]-df_stock_data2.iat[5, 0]))
            col2.metric("High",     df_stock_data2.iat[0, 1], int(
                df_stock_data2.iat[0, 1]-df_stock_data2.iat[5, 1]))
            col3.metric("Low",      df_stock_data2.iat[0, 2], int(
                df_stock_data2.iat[0, 2]-df_stock_data2.iat[5, 2]))
            col4.metric("Close",    df_stock_data2.iat[0, 3], int(
                df_stock_data2.iat[0, 3]-df_stock_data2.iat[5, 3]))
            col5.metric("Volume",   df_stock_data2.iat[0, 4], int(
                df_stock_data2.iat[0, 4]-df_stock_data2.iat[5, 4]))


            # 各データの前月比
            st.write(f'前月比')
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Open",     df_stock_data2.iat[0, 0], int(
                df_stock_data2.iat[0, 0]-df_stock_data2.iat[23, 0]))
            col2.metric("High",     df_stock_data2.iat[0, 1], int(
                df_stock_data2.iat[0, 1]-df_stock_data2.iat[23, 1]))
            col3.metric("Low",      df_stock_data2.iat[0, 2], int(
                df_stock_data2.iat[0, 2]-df_stock_data2.iat[23, 2]))
            col4.metric("Close",    df_stock_data2.iat[0, 3], int(
                df_stock_data2.iat[0, 3]-df_stock_data2.iat[23, 3]))
            col5.metric("Volume",   df_stock_data2.iat[0, 4], int(
                df_stock_data2.iat[0, 4]-df_stock_data2.iat[23, 4]))




        # 出来高のエリアチャート

        # figを定義
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.2, 0.2, 0.7])


        # ローソク足チャートを表示
        fig.add_trace(
            go.Candlestick(x=df_stock_data2.index, open=df_stock_data2["Open"], high=df_stock_data2["High"], low=df_stock_data2["Low"], close=df_stock_data2["Close"], showlegend=False),
            row=1, col=1
        )
        mod.Get_Buy_or_Sell_Timing(df_stock_data2)
        fig.add_trace(go.Scatter(x=df_stock_data2.index,
                                y=df_stock_data2["engulfing_marker"],
                                mode="markers+text",
                                text=df_stock_data2["engulfing_text"],
                                textposition="top center",
                                name="ENGULFING BAR",
                                marker = { "size": 8, "color": "blue", "opacity": 0.6 },
                                textfont = {"size": 8, "color": "black" }))


        # 移動平均線
        mod.Get_SimpleMovingAverage(df_stock_data2)
        fig.add_trace(go.Scatter(x=df_stock_data2.index, y=df_stock_data2["SMA20"], name="SMA20", mode="lines"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_stock_data2.index, y=df_stock_data2["SMA50"], name="SMA50", mode="lines"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_stock_data2.index, y=df_stock_data2["SMA200"], name="SMA200", mode="lines"), row=1, col=1)

        # MACD
        mod.Get_TechnicalIndex(df_stock_data2)
        fig.add_trace(go.Scatter(x=df_stock_data2.index, y=df_stock_data2["MACD"], mode="lines", showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_stock_data2.index, y=df_stock_data2["Signal"], mode="lines", showlegend=False), row=3, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df_stock_data2.index, y=df_stock_data2["RSI"], mode="lines", showlegend=False), row=4, col=1)


        # 出来高の棒グラフを表示
        fig.add_trace(
            go.Bar(x=df_stock_data2.index, y=df_stock_data2["Volume"], showlegend=False),
            row=2, col=1
        )
        # Layout
        fig.update_layout(
            # title={
            #     "text": "トヨタ自動車(7203)の日足チャート",
            #     "y":0.9,
            #     "x":0.5,
            # },
            height=700
        )

        fig.update_xaxes(
            rangebreaks=[dict(values=mod.Get_Unnecessary_DateList(df_stock_data2))], # 非営業日を非表示設定
            tickformat='%Y/%m/%d' # 日付のフォーマット変更
        )

        # 日付のフォーマット変更
        fig.update_xaxes(tickformat='%Y/%m/%d')

        # ラベル名の設定とフォーマット変更（カンマ区切り）
        fig.update_yaxes(separatethousands=True, title_text="株価", row=1, col=1)
        fig.update_yaxes(title_text="出来高", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="RSI", row=4, col=1)

        # 棒グラフを非表示にする場合は以下を適用
        fig.update(layout_xaxis_rangeslider_visible=False)
        # 描画
        st.plotly_chart(fig, use_container_width=True)




        # 取得した株価データの表
        # 選択中の企業名を表示
        # 表の生成
        with st.expander('表'):
            st.table(df_stock_data2.loc[:, :'Volume'])








# 基本画面（1社分だけ表示）
else:

    # 選択中の企業名を表示
    st.subheader(f'{corp}（{start}~{end}）')

    # 各データの前日比
    st.write(f'前日比')
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Open",     df_stock_data.iat[0, 0], int(
        df_stock_data.iat[0, 0]-df_stock_data.iat[1, 0]))
    col2.metric("High",     df_stock_data.iat[0, 1], int(
        df_stock_data.iat[0, 1]-df_stock_data.iat[1, 1]))
    col3.metric("Low",      df_stock_data.iat[0, 2], int(
        df_stock_data.iat[0, 2]-df_stock_data.iat[1, 2]))
    col4.metric("Close",    df_stock_data.iat[0, 3], int(
        df_stock_data.iat[0, 3]-df_stock_data.iat[1, 3]))
    col5.metric("Volume",   df_stock_data.iat[0, 4], int(
        df_stock_data.iat[0, 4]-df_stock_data.iat[1, 4]))


    with st.expander("前週・前月比"):
        # 各データの前週比
        st.write(f'前週比')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Open",     df_stock_data.iat[0, 0], int(
            df_stock_data.iat[0, 0]-df_stock_data.iat[5, 0]))
        col2.metric("High",     df_stock_data.iat[0, 1], int(
            df_stock_data.iat[0, 1]-df_stock_data.iat[5, 1]))
        col3.metric("Low",      df_stock_data.iat[0, 2], int(
            df_stock_data.iat[0, 2]-df_stock_data.iat[5, 2]))
        col4.metric("Close",    df_stock_data.iat[0, 3], int(
            df_stock_data.iat[0, 3]-df_stock_data.iat[5, 3]))
        col5.metric("Volume",   df_stock_data.iat[0, 4], int(
            df_stock_data.iat[0, 4]-df_stock_data.iat[5, 4]))


        # 各データの前月比
        st.write(f'前月比')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Open",     df_stock_data.iat[0, 0], int(
            df_stock_data.iat[0, 0]-df_stock_data.iat[23, 0]))
        col2.metric("High",     df_stock_data.iat[0, 1], int(
            df_stock_data.iat[0, 1]-df_stock_data.iat[23, 1]))
        col3.metric("Low",      df_stock_data.iat[0, 2], int(
            df_stock_data.iat[0, 2]-df_stock_data.iat[23, 2]))
        col4.metric("Close",    df_stock_data.iat[0, 3], int(
            df_stock_data.iat[0, 3]-df_stock_data.iat[23, 3]))
        col5.metric("Volume",   df_stock_data.iat[0, 4], int(
            df_stock_data.iat[0, 4]-df_stock_data.iat[23, 4]))




    # 出来高のエリアチャート

    # figを定義
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.2, 0.2, 0.7])


    # ローソク足チャートを表示
    fig.add_trace(
        go.Candlestick(x=df_stock_data.index, open=df_stock_data["Open"], high=df_stock_data["High"], low=df_stock_data["Low"], close=df_stock_data["Close"], showlegend=False),
        row=1, col=1
    )
    mod.Get_Buy_or_Sell_Timing(df_stock_data)
    fig.add_trace(go.Scatter(x=df_stock_data.index,
                            y=df_stock_data["engulfing_marker"],
                            mode="markers+text",
                            text=df_stock_data["engulfing_text"],
                            textposition="top center",
                            name="ENGULFING BAR",
                            marker = { "size": 8, "color": "blue", "opacity": 0.6 },
                            textfont = {"size": 8, "color": "black" }))


    # 移動平均線
    mod.Get_SimpleMovingAverage(df_stock_data)
    fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["SMA20"], name="SMA20", mode="lines"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["SMA50"], name="SMA50", mode="lines"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["SMA200"], name="SMA200", mode="lines"), row=1, col=1)

    mod.Get_Date(df_stock_data)
    mod.Get_PerfectOrder(df_stock_data)
    df_po = mod.Get_When_PerfectOrder(df_stock_data)
    #! len(df_po)-1 にしないと，end_dateが空の行が含まれてしまうので，表示がおかしくなる
    for i in range(len(df_po)-1):
        row = df_po.iloc[i]
        fig.add_vrect(x0=row["Date"], x1=row["end_date"], annotation_text="PERFECT ORDER", annotation_position="top left", line_width=0, fillcolor="cyan", opacity=0.1, row=1, col=1)


    # MACD
    mod.Get_TechnicalIndex(df_stock_data)
    fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["MACD"], mode="lines", showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["Signal"], mode="lines", showlegend=False), row=3, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df_stock_data.index, y=df_stock_data["RSI"], mode="lines", showlegend=False), row=4, col=1)


    # 出来高の棒グラフを表示
    fig.add_trace(
        go.Bar(x=df_stock_data.index, y=df_stock_data["Volume"], showlegend=False),
        row=2, col=1
    )
    # Layout
    fig.update_layout(
        # title={
        #     "text": "トヨタ自動車(7203)の日足チャート",
        #     "y":0.9,
        #     "x":0.5,
        # },
        height=700
    )

    fig.update_xaxes(
        rangebreaks=[dict(values=mod.Get_Unnecessary_DateList(df_stock_data))], # 非営業日を非表示設定
        tickformat='%Y/%m/%d' # 日付のフォーマット変更
    )

    # 日付のフォーマット変更
    fig.update_xaxes(tickformat='%Y/%m/%d')

    # ラベル名の設定とフォーマット変更（カンマ区切り）
    fig.update_yaxes(separatethousands=True, title_text="株価", row=1, col=1)
    fig.update_yaxes(title_text="出来高", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="RSI", row=4, col=1)

    # 棒グラフを非表示にする場合は以下を適用
    fig.update(layout_xaxis_rangeslider_visible=False)
    # 描画
    st.plotly_chart(fig, use_container_width=True)




    # 取得した株価データの表
    # 選択中の企業名を表示
    # 表の生成
    with st.expander('表'):
        st.table(df_stock_data.loc[:, :'Volume'])
        # mod.Get_Date(df_stock_data)
        # st.dataframe(df_stock_data)

