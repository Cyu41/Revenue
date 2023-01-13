import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
import numpy as np
from Upload_git import upload


upload.execute('Update_file')
# pd.read_csv('db.csv', low_memory=False)