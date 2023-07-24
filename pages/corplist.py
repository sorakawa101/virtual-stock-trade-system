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


st.header('銘柄一覧')


# DF：JPXから取得した銘柄コード一覧をMySQLから取得
df_stock_code = mod.ConnectMySQL_and_GetTable('stock_code_list')


# df_stock_code = pd.read_excel("./src/data_j.xls")# 表の生成
# ! st.dataframeは通常だと千区切りのコンマが入ってしまうのでフォーマットを変更
st.dataframe(df_stock_code.style.format(
    thousands=''), use_container_width=False, height=600)