import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import json
from datetime import date
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://bootswatch.com/4/flatly/bootstrap.min.css']

layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

#Nation wide data

dates = []
dailyconfirmed = []
dailydeceased = []
dailyrecovered = []

url = 'https://api.covid19india.org/data.json'
response = requests.get(url)

data = json.loads(response.text)
cases_time_series = data.get('cases_time_series')

for item in cases_time_series:
    dates.append(item.get('date'))
    dailyconfirmed.append(int(item.get('dailyconfirmed')))
    dailyrecovered.append(int(item.get('dailyrecovered')))
    dailydeceased.append(int(item.get('dailydeceased')))

# Nation wide data block ends

#State wide data

state_codes = ['AP', 'AS', 'BR', 'CT', 'DL', 'GJ', 'HP', 'HR', 'JH', 'JK', 'KA', 'KL', 'MP', 'OR', 'PB', 'RJ', 'TG', 'TN', 'UP', 'UT', 'WB', 'MH']

state_names = ['Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Delhi', 'Gujarat', 'Himachal Pradesh', 'Haryana', 'Jharkhand', 'Jammu and Kashmir', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Odisha', 'Punjab', 'Rajasthan', 'Telangana', 'Tamil Nadu', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Maharashtra']

def get_state_data(state_name, metric):
    data_list = []
    Seven_DMA = []
    state = state_name
    focus = []

    url = 'https://api.covid19india.org/v3/timeseries.json'
    response = requests.get(url)

    data = json.loads(response.text)
    state_data = data.get(state)

    for key in state_data.keys():
        data_list.append(state_data[key].get('delta'))

    focus = [0 if item == None else item.get(metric) for item in data_list]
    focus = [0 if item == None else item for item in focus]

    return focus

# Scatter Plot Data

def create_scatter_plot():
    x,y,z,color = [], [], [], []

    state_list = state_codes
    state_pop = [49577103, 31205576, 104099452, 25545198, 16787941, 60439692, 6864602, 25351462, 32988134, 12267032, 61095297, 33406061, 72626809, 41974219, 27743338, 68548437, 35003674, 72147030, 199812341, 10086292, 91276115, 112374333]

    url = 'https://api.covid19india.org/v3/timeseries.json'
    response = requests.get(url)
    data = json.loads(response.text)

    for state, pop in zip(state_list, state_pop):
        state_data = data.get(state)
        latest = state_data.get(list(state_data)[-1])
        x.append(latest.get('total').get('confirmed')/latest.get('total').get('tested'))
        y.append(latest.get('total').get('deceased')/latest.get('total').get('confirmed'))
        z_value = latest.get('total').get('tested')/pop
        z.append(latest.get('total').get('tested')/pop)
        if z_value >=0.02:
            color.append('green')
        elif z_value>=0.01:
            color.append('grey')
        else: color.append('red')

    fig = go.Figure(data=[go.Scatter(
        x=x, y=y,
        mode='markers+text',
        marker_size=[2000*size for size in z], marker_color=color,
        text=[state+" {:.1%}".format(penetration) for penetration, state in zip(z, state_list)]),
    ], layout=layout)

    fig.layout.yaxis.tickformat = ',.1%'
    fig.layout.xaxis.tickformat = ',.1%'
    fig.layout.height = 800
    fig.update_layout(xaxis_title = "Percentage confirmed out of total tested", yaxis_title = "Percentage deceased out of total confirmed",
        xaxis = dict(
            tickmode = 'linear',
            dtick = 0.02,
            linecolor = 'grey'
                    ),
        yaxis = dict(
            # tickmode = 'linear',
            # dtick = 0.02,
            linecolor = 'grey'
                    )
)
    
    return fig

# 7 day moving average calculation

def Seven_DMA_Calculation(focus):
    Seven_DMA = []
    end = len(focus)-1
    begin = end-7
    while begin >= 0:
        sliced = focus[begin:end]
        end = end-1
        begin = end-7
        Seven_DMA.append(int(sum(sliced)/7))
    Seven_DMA.reverse()
    
    return(Seven_DMA)

# Function to generate the figures
def Create_Figure(parameter, title):

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Bar(x=list(range(0, len(parameter))), y=parameter,
                         name=title,
                         marker_color = 'red',
                         opacity=0.3,
                         # marker_line_color='rgb(8,48,107)',
                         # marker_line_width=2
                         ))

    fig.add_trace(go.Scatter(x=list(range(7, len(parameter)+7)), y=Seven_DMA_Calculation(parameter),
                         name='Seven DMA '+str(title),
                         opacity=1,
                         line=dict(color='red', width=5)
                         ))

    fig.update_layout(
                    autosize=True,
                    # width=800,
                    height=800,
                    title=title,title_x=0.5,
                    xaxis_title='Days',
                    yaxis_title='Number of cases',
                    legend=dict(orientation="h", xanchor='center', x=0.5, yanchor = 'bottom', y=-0.2)
)

    return fig

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

page_title = 'Dashboard: Covid19 in India - ' + str(date.today().strftime("%d %b %Y"))

app.layout = html.Div(children=[
    html.H1(children=page_title, style = {'textAlign': 'center', "border":"2px black solid", "margin": "12px"}),

    html.Div(children=['By Pranshumaan ', dcc.Link('Github', href='https://github.com/MadHatter92/covid19india')], style = {'textAlign': 'center'}),

    html.H2(children='National Tally', style = {'textAlign': 'center', "border":"2px black solid", "margin": "12px"}),

    html.Div(children=[
    dcc.Graph(
        id='confirmed_cases',
        figure=Create_Figure(dailyconfirmed, "Daily Confirmed"),
        style={'width': '48%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}

    ),

    dcc.Graph(
        id='deceased_cases',
        figure=Create_Figure(dailydeceased, "Daily Deceased"),
        style={'width': '48%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}
    ),
    ]),

    html.Div(children=[

    html.Div(children=[

    html.H2(children='State-wise Tally', style = {'textAlign': 'center'}),

    dcc.Dropdown(
        id='states-dropdown',
        options= [{'label': state_name, 'value': state_code} for(state_name, state_code) in zip(state_names, state_codes)],
        value='AP',
        style={'verticalAlign': "middle", 'color':'green'},

    ),
    ], style={"border":"2px black solid", "margin": "12px"}),

    dcc.Graph(
        id='state-confirmed-output',
        style={'width': '48%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}
    ),

    dcc.Graph(
    id='state-deceased-output',
    style={'width': '48%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}
    ),
    ]),

    html.Div(children = [

        html.H2(children='State-wise Population Adjusted Data', style = {'textAlign': 'center'}),

        html.H6(children='Note: Size of circle indicates proportion of population tested, denoted by number inside the circle', style = {'textAlign': 'center'}),

        dcc.Graph(
        id='state-scatter-output',
        figure = create_scatter_plot(),
        ),

        ], style={"border":"2px black solid", "margin": "12px"}) 
])

@app.callback(
    Output(component_id='state-confirmed-output', component_property='figure'),
    [Input(component_id='states-dropdown', component_property='value')]
)
def update_state_confirmed_output_div(state_code):
    state_data = get_state_data(state_code, 'confirmed')
    fig = Create_Figure(state_data, "Daily confirmed cases: "+str(state_code))
    return fig

@app.callback(
    Output(component_id='state-deceased-output', component_property='figure'),
    [Input(component_id='states-dropdown', component_property='value')]
)
def update_state_deceased_output_div(state_code):
    state_data = get_state_data(state_code, 'deceased')
    fig = Create_Figure(state_data, "Daily deceased cases: "+str(state_code))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
