import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from server import app

from views.industry_revenue import industry_revenue_page
from views.ml_cluster import ml_cluster_page
from views.latest_revenue import latest_revenue_page
from views.predict_revenue import predict_revenue_page


app.layout = html.Div(
    [
        # 监听url变化
        dcc.Location(id='url'),
        html.Div(
            [
                # 标题区域
                html.Div([
                    html.Img(src=app.get_asset_url("logo.png"), 
                                 style={
                                     "width":"5rem", 
                                     "height":"3rem", 
                                     }
                                 ),
                    html.H1(
                        id='header',
                        children=['小飛鷹報表'],
                        style={
                            'color':'black', 
                            'marginTop': '20px',
                            'fontFamily': '"Open Sans", sans-serif',
                            'fontWeight': 'bold'
                        }
                    ),
                ], 
                         style={
                             'textAlign': 'center',
                             'margin': '0 10px 0 10px',
                             'borderBottom': '2px solid black'
                             }
                         )
                ,

                # 子页面区域
                html.Div(
                    [
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink('上市櫃產業合併營收報表', href='/industry_revenue', active="exact")),
                                dbc.NavItem(dbc.NavLink('最新營收公告', href='/latest_revenue', active="exact")),
                                dbc.NavItem(dbc.NavLink('預估次月營收', href='/predict_revenue', active="exact")),
                                dbc.NavItem(dbc.NavLink('台股分群表現', href='/ml_cluster', active="exact")),
                                ],
                            vertical='md',
                            pills=True
                            )
                    ]
                )
            ],
            style={
                'padding':'2rem 3rem',
                'width': '25%',
                # 'display': 'flex',
                # 'flex-direction': 'column',
                'backgroundColor': '#ededed'
            }
        ),
        html.Div(
            id='page-content',
            style={
                'display': 'flex',
                'width': '75%',
                'flex-direction': 'column',
            }
        )
    ],
    style={
        'display': 'flex',
        'flex-direction': 'row',
        'font-family': '"Open Sans", sans-serif'
    }
)


 

# 路由总控
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page_content(pathname):
    if pathname == '/industry_revenue':
        return industry_revenue_page
    
    elif pathname == '/latest_revenue':
        return latest_revenue_page

    elif pathname == '/predict_revenue':
        return predict_revenue_page
    
    elif pathname == '/ml_cluster':
        return ml_cluster_page

    return html.H1('您访问的页面不存在！')


if __name__ == '__main__':
    app.run_server( debug=True)