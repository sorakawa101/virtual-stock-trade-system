import streamlit as st
import numpy as np
import datetime
import pandas as pd


st.title('Virtual Stock Trade System')
st.header('MyPage')


# DF：JPXから取得した銘柄コード一覧
df_stock_code = pd.read_excel("./data_j.xls")


# タブごとに表示分け
tab1, tab2, tab3, tab4 = st.tabs(
    ["Buying & Selling", "Confirm & Change", "Result", "Ranking"])


df = pd.DataFrame(
    np.random.randn(50, 20),
    columns=('col %d' % i for i in range(20)))


# 情報を見たい銘柄コード・開始日・最終日を入力
with tab1:
    today = datetime.date.today()
    today = str(today).split('-')
    st.write(f'{today[0]}年{today[1]}月{today[2]}日現在の売買データ')

    # 銘柄コードに一致する企業名
    # コードが一致する行のみを抽出したDF
    df_corp = df_stock_code[df_stock_code['コード'] == 9984]

    # DFから銘柄名の絡むだけを抽出したseries（DFの最小単位）
    series_corp = df_corp['銘柄名']

    # seriesから企業名の値だけを抽出
    corp = series_corp.iloc[-1]

    with st.form("売買データ入力"):

        # 銘柄コード入力
        text_val = st.text_input('銘柄コード', '0000.JP')
        # 売買選択
        radio_val = st.radio("売買選択", ('売', '買'))
        # 株数量入力
        # TODO 銘柄コードと株数量からかかる金額を表示したい
        number_val = st.number_input('株数量', min_value=int(100), step=int(100))

        # TODO ここの入力からInformationのページで情報を確認できるようにしたい

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f'{text_val}の株を{number_val}株{radio_val}った')
