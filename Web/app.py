import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from server import app

# from views.industry_revenue import industry_revenue_page
from views.latest_revenue import latest_revenue_page
from views.predict_revenue import predict_revenue_page
from views.ml_cluster import ml_cluster_page

app.layout = html.Div(
    [
        # 监听url变化
        dcc.Location(id='url'),
        html.Div(
            [
                # 标题区域
                html.Div(
                    [
                        html.Img(src=app.get_asset_url("logo.png"), 
                                 style={
                                     "width":"5rem", 
                                     "height":"3rem", 
                                     'fontFamily': 'Open Sans'
                                     }
                                 ),
                        html.H3(id='header', children=["小飛鷹"], style={'color':'black', 'fontFamily': 'Open Sans'})
                    ],style={"padding": "2rem 2rem"}
                ),

                # 子页面区域
                html.Hr(),

                dbc.Nav(
                    [
                        dbc.NavLink('上市櫃產業年度合併報表', href='/industry_revenue', active="exact"),
                        dbc.NavLink('最新公告營收', href='/latest_revenue', active="exact"),
                        dbc.NavLink('預估營收', href='/predict_revenue', active="exact"),
                        dbc.NavLink('台股分群表現', href='/ml_cluster', active="exact"),
                    ],
                    vertical=True,
                    pills=True
                )
            ],
            style={
                # 'flex': '0.5 10%',
                'width': '30rem',
                'padding': '7rem 4rem',
                'display': 'flex',
                'flex-direction': 'column',
                'justify-content': 'start',
                'backgroundColor': '#ededed'
            }
        ),
        html.Div(
            id='page-content',
            style={
                # 'flex': '0.5 10%',
                'width': '70rem',
                'display': 'flex',
                'fontFamily': 'Open Sans',
            }
        )
    ],
    style={
        'width': '100%',
        'height': '100%',
        'display': 'flex',
        'font-family': 'Open Sans',
        'flex-direction': 'row',
        'justify-content': 'stretch'
    }
)


# 路由总控
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page_content(pathname):
    # if pathname == '/industry_revenue':
    #     return industry_revenue_page

    if pathname == '/latest_revenue':
        return latest_revenue_page

    elif pathname == '/predict_revenue':
        return predict_revenue_page

    elif pathname == '/ml_cluster':
        return ml_cluster_page

    return html.H1('您访问的页面不存在！')


if __name__ == '__main__':
    app.run_server(debug=False)