from statistics import mode
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go

######################################################Data##############################################################

path = 'https://raw.githubusercontent.com/foazul/Data-visualization-Project_1/main/'

df = pd.read_csv(path + 'CO2_Emission_Continent_2.csv')
df.loc[df.CO2_emission == 994160327,'continent'] = 'South America' #updating one of the entries, due to a dataset error

df_pivot = pd.read_excel('C:/Users/HP/Downloads/CO2_Emission_Continent_2.xlsx') #this dataframe was created based on the original one in order to calculate variations and means


######################################################Interactive Components############################################

continent_options = [dict(label=continent, value=continent) for continent in df['continent'].unique()]


dropdown_country = dcc.Dropdown(
        id='continent_drop',
        options=continent_options,
        value=['Europe', 'North America'],
        multi=True
    )


slider_year = dcc.RangeSlider(
        id='year_slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],
        marks={str(i): '{}'.format(str(i)) for i in
               [2011, 2014, 2017, 2020]},
        step=1,
        pushable=1,
        allowCross=False
    )

radio_sum_mean = dcc.RadioItems(
        id='sum_mean',
        options=[dict(label='Cumulative', value=0), dict(label='Mean', value=1)],
        value=0
    )




##################################################APP###################################################################

app = dash.Dash(__name__)


server = app.server

app.layout = html.Div ( [

    html.Div([
        html.H1('CO2 Emissions Dashboard'),
    ], id='1st row', className='pretty_box'),
    html.Div([
        html.Div([
            html.Br(),
            html.Label('Continent Choice'),
            dropdown_country,
            html.Br(),
            html.Br(),
            html.Label('Year Slider'),
            slider_year,
            html.Br(),
            html.Br(),
            html.Label('Cumulative Sum or Mean'),
            radio_sum_mean,
            html.Br(),
            html.Br(),
            html.Button('Submit', id='button')
        ], id='Iteraction', style={'width': '40%'}, className='pretty_box'),
        html.Div([
            dcc.Graph(id='bar_graph2')
        ]
        , id='Graph3', style={'width': '50%'}, className='pretty_box')
    ], id='2nd row', style={'display': 'flex'}),
    html.Div([
        html.Div([
            dcc.Graph(id='scatter_graph'),
        ], id='Graph1', style={'width': '50%'}, className='pretty_box'),
        html.Div([
            dcc.Graph(id='bar_graph')
        ], id='Graph2', style={'width': '50%'}, className='pretty_box'),
    ], id='3th row', style={'display': 'flex'})
])

######################################################Callbacks#########################################################


@app.callback(
    [
        Output("scatter_graph", "figure"),
        Output("bar_graph", "figure"),
        Output("bar_graph2", "figure"),
    ],
    [
        Input("button", "n_clicks")
    ],
    [
        State("year_slider", "value"),
        State("continent_drop", "value"),
        State("sum_mean", "value"),
    ]
)
def plots(n_clicks, years, continents, calc):
    ############################################Scatter plot##########################################################
    data_scatter = []
    for continent in continents:
        df_loc = df.loc[(df['continent'] == continent)]
        data_scatter.append(dict(type='scatter',
                             x=df_loc['year'].unique(), 
                             y=df_loc['CO2_emission'], 
                             name=continent,
                             mode='markers'))

   
    layout_scatter = dict(title=dict(text='CO2 Emissions from 2011 until 2020'),
                      yaxis=dict(title='Emissions'),
                      paper_bgcolor='rgba(0, 0, 0, 0)',
                      plot_bgcolor='rgba(222, 254, 255, 0.8)'
                      )

    
    ############################################Bar Plot 1######################################################

    df_pivot.columns = df_pivot.columns.astype(str)
    df_pivot_indexed = df_pivot.set_index('continent')
    year1 = str(years[0])
    year2 = str(years[1])
    df_pivot_indexed = df_pivot.loc[:, year1:year2]
    means_list = df_pivot_indexed.mean(axis=1)
    sums_list = df_pivot_indexed.sum(axis=1)


    data_bar = []


    x_bar= df_pivot['continent']

    data_bar.append(dict(type='bar', x=x_bar, y=[sums_list, means_list][calc], name=continent))


    layout_bar = dict(title=dict(text=['Cumulative Emissions in selected years', 'Mean CO2 Emissions by continent'][calc]),
                      yaxis=dict(title=['CO2 Emissions', 'Mean CO2 Emissions'][calc]),
                      xaxis=dict(title='Continent'),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(222, 254, 255, 0.8)'
                      )

 ############################################Bar Plot 2######################################################

    data_bar2 = []

    x_bar2 = df_pivot['continent']

    result = []
    for i in range(len(df_pivot['continent'])):
        result.append(((df_pivot[str(years[1])][i] - df_pivot[str(years[0])][i])/df_pivot[str(years[1])][i])*100)

    data_bar2.append(dict(type='bar', x=x_bar2, y=result, name=continent))


    layout_bar2 = dict(title=dict(text='Percentual Variation along the years'),
                      yaxis=dict(title='Percentual Variation'),
                      xaxis=dict(title='Continent'),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(222, 254, 255, 0.8)'
                      )                  

                      

    return go.Figure(data=data_scatter, layout=layout_scatter), \
           go.Figure(data=data_bar, layout=layout_bar), \
           go.Figure(data=data_bar2, layout=layout_bar2)



if __name__ == '__main__':
    app.run_server(debug=True)
