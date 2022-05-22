from dash import Dash, dcc, html, Input, Output
import os
import plotly.express as px
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

con = sqlite3.connect('data/gcashdata_db.gnucash')
df_expense_names = pd.read_sql("select name from accounts where account_type=='EXPENSE'", con)
start_date = '2022-01-01'
con.close()

server = app.server

app.layout = html.Div([
    html.H2('GnuDash'),
    dcc.Dropdown(
        df_expense_names['name'],
        'Groceries',
        id='expense-dropdown'
        ),
    dcc.Graph(
       id='example-graph',
    ),
])


@app.callback(Output('example-graph', 'figure'),
              [Input('expense-dropdown', 'value')])
def update_graph(expense_type):
    con = sqlite3.connect('data/gcashdata_db.gnucash')

    q_groceries = f"""
    select post_date, t.description, CAST (value_num as real)/ value_denom as value from transactions t
    join splits s on s.tx_guid = t.guid
    join accounts a on a.guid = s.account_guid
    where a.name="{expense_type}" order by post_date asc"""

    df = pd.read_sql_query(q_groceries, con)
    df['post_date'] = pd.to_datetime(df['post_date'])
    df.set_index('post_date', inplace=True)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df.loc[start_date:].index,
                   y=df.loc[start_date:]['value'],
                   name=f"{expense_type}",
                   customdata=df.loc[start_date:]['description'],
                   hovertemplate='<br>'.join([
                       '%{x}',
                       '$%{y:.2f}',
                       '%{customdata}',
                   ])
                   ),
        secondary_y=False,
    )

    # fig = px.line(df.loc[start_date:], x=, y="value", hover_data=["description"])
    fig.add_trace(
        go.Scatter(
            x=df.loc[start_date:].index,
            y=df.loc[start_date:]['value'].cumsum(),
            mode="lines",
            line=go.scatter.Line(color="gray"),
            name='cumulative'
        ),
        secondary_y=True
    )
    # fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
    con.close()

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
