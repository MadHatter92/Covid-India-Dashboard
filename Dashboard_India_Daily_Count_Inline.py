import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
import json
from datetime import date
import plotly.graph_objects as go

external_stylesheets = ['https://bootswatch.com/4/flatly/bootstrap.min.css']

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

layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

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
	                legend=dict(orientation="h", xanchor='center', x=0.5)
)

	return fig


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

page_title = 'Dashboard: Covid19 in India - ' + str(date.today().strftime("%d %b %Y"))

app.layout = html.Div(children=[
    html.H1(children=page_title, style = {'textAlign': 'center', "border":"2px black solid", "margin": "12px"}),

    html.Div(children=['By Pranshumaan ', dcc.Link('Github', href='https://github.com/MadHatter92/covid19india')], style = {'textAlign': 'center'}),

    dcc.Graph(
        id='confirmed_cases',
        figure=Create_Figure(dailyconfirmed, "Daily Confirmed"),
        style={'width': '32%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}

    ),

    dcc.Graph(
        id='deceased_cases',
        figure=Create_Figure(dailydeceased, "Daily Deceased"),
        style={'width': '32%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}
    ),

    dcc.Graph(
        id='recovered_cases',
        figure=Create_Figure(dailyrecovered, "Daily Recovered"),
        style={'width': '32%','display': 'inline-block', "border":"2px black solid", "margin": "12px"}

    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)