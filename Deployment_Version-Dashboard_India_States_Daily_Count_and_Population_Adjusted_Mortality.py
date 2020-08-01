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

def incremental_active():
	dates = []
	totalconfirmed = []
	dailydeceased = []
	dailyrecovered = []

	url = 'https://api.covid19india.org/data.json'
	response = requests.get(url)

	data = json.loads(response.text)
	cases_time_series = data.get('cases_time_series')

	for item in cases_time_series:
		dates.append(item.get('date'))
		totalconfirmed.append(int(item.get('totalconfirmed')))
		dailyrecovered.append(int(item.get('totalrecovered')))
		dailydeceased.append(int(item.get('totaldeceased')))

	focus = [(confirmed - recovered - deceased) for confirmed, recovered, deceased in zip(totalconfirmed, dailyrecovered, dailydeceased)]
	focus = [focus[i+1] - focus[i] for i in list(range(len(focus)-1))]

	return focus

def incremental_testing():
	cumulative_tested = []
	daily_tested = []

	url = 'https://api.covid19india.org/data.json'
	response = requests.get(url)

	data = json.loads(response.text)
	testing_data = data.get('tested')

	for item in testing_data:
		cumulative_tested.append(item.get('testspermillion').strip())

	#Removing empty strings
	cumulative_tested = list(filter(None, cumulative_tested))

	index = 0
	while index <= len(cumulative_tested)-2:
		daily_tested.append(int(cumulative_tested[index+1])-int(cumulative_tested[index]))
		index = index+1

	focus = daily_tested
	return focus

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

def create_scatter_plot_pop_adjusted():
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

def create_scatter_plot_aggregate():
	x,y,z = [], [], []

	state_list = ['AP', 'AS', 'BR', 'CH', 'CT', 'DL', 'GJ', 'HP', 'HR', 'JH', 'JK', 'KA', 'KL', 'MP', 'OR', 'PB', 'RJ', 'TG', 'TN', 'UP', 'UT', 'WB', 'MH']

	url = 'https://api.covid19india.org/v3/timeseries.json'
	response = requests.get(url)
	data = json.loads(response.text)

	for state in state_list:
		state_data = data.get(state)
		latest = state_data.get(list(state_data)[-1])
		x.append(latest.get('total').get('tested'))
		z.append(latest.get('total').get('deceased')/latest.get('total').get('confirmed'))
		y.append(latest.get('total').get('confirmed'))

	fig = go.Figure(data=[go.Scatter(
	    x=x, y=y,
	    mode='markers+text',
	    marker_size=[2000*size for size in z],
	    text=[state+" {:.1%}".format(penetration) for penetration, state in zip(z, state_list)]),
	], layout=layout)

	# fig.layout.yaxis.tickformat = ',.1%'
	# fig.layout.xaxis.tickformat = ',.1%'
	fig.layout.height = 800
	fig.update_layout(xaxis_title = "Total cases tested", yaxis_title = "Total confirmed cases",
		xaxis = dict(
			# tickmode = 'linear',
			# dtick = 0.02,
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
        style={"border":"2px black solid", "margin": "12px"}

    ),

    dcc.Graph(
        id='deceased_cases',
        figure=Create_Figure(dailydeceased, "Daily Deceased"),
        style={"border":"2px black solid", "margin": "12px"}
    ),
    ]),

    html.H2(children='Active Cases and Incremental Testing', style = {'textAlign': 'center', "border":"2px black solid", "margin": "12px"}),

    html.Div(children=[
    dcc.Graph(
        id='incremental_active_cases',
        figure=Create_Figure(incremental_active(), "Daily Net New Active Cases"),
        style={"border":"2px black solid", "margin": "12px"}

    ),

    dcc.Graph(
        id='incremental_testing',
        figure=Create_Figure(incremental_testing(), "Daily Increase in Number of Tests Per Million"),
        style={"border":"2px black solid", "margin": "12px"}
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
        style={ "border":"2px black solid", "margin": "12px"}
    ),

	dcc.Graph(
    id='state-deceased-output',
    style={ "border":"2px black solid", "margin": "12px"}
    ),
    ]),

    html.Div(children = [

    	html.H2(children='State-wise Population Adjusted Data', style = {'textAlign': 'center'}),

    	html.H6(children='Note: Size of circle indicates proportion of population tested, denoted by number inside the circle', style = {'textAlign': 'center'}),

    	dcc.Graph(
    	id='state-scatter-output-population-adjusted',
    	figure = create_scatter_plot_pop_adjusted(),
    	),

    	], style={"border":"2px black solid", "margin": "12px"}),

    html.Div(children = [

    	html.H2(children='State-wise Aggregate Data', style = {'textAlign': 'center'}),

    	html.H6(children='Note: Percentage figures inside the circles denote mortality, depicted by the size of the circle', style = {'textAlign': 'center'}),

    	dcc.Graph(
    	id='state-scatter-output-aggregate',
    	figure = create_scatter_plot_aggregate(),
    	),

    	], style={"border":"2px black solid", "margin": "12px"}),

    html.Div(children = [

    	html.H2(children='State-wise Mortality Data', style = {'textAlign': 'center'}),

    	html.H6(children='Note: Mortality defined as aggregate deceased cases so far, divided by aggregate confirmed cases so far', style = {'textAlign': 'center'}),

    	dcc.Dropdown(
					id = 'states-mortality-multiple-dropdown',
				    options=[
				        {'label': label, 'value':value} for label,value in zip(state_names, state_codes)
				    ],
				    value=['AP', 'MH', 'TN', 'DL', 'GJ',],
				    multi=True,
				    placeholder="Select a state",
				),

		dcc.Graph(
			id='states-comparison-mortality',
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

@app.callback(
    Output(component_id='states-comparison-mortality', component_property='figure'),
    [Input(component_id='states-mortality-multiple-dropdown', component_property='value')]
)
def create_chart_statewise_mortality(value):

	state_list = value

	fig = go.Figure(layout=layout)

	url = 'https://api.covid19india.org/v3/timeseries.json'
	response = requests.get(url)
	data = json.loads(response.text)

	for state in state_list:
		data_series = []
		Seven_DMA = []
		cumulative_confirmed_list = []
		daily_deceased_list = []
		state_data = data.get(state)
		for key in state_data.keys():
			try:
				cumulative_confirmed = state_data[key].get('total').get('confirmed')
				daily_deceased = state_data[key].get('total').get('deceased')
			except:
				pass
			cumulative_confirmed_list.append(cumulative_confirmed)
			daily_deceased_list.append(daily_deceased)
		for (conf, dece) in zip(cumulative_confirmed_list, daily_deceased_list):
			try:
				data_series.append(dece/conf)
			except:
				pass	
		# try:
		# 	data_series.remove(1409) #Removes outlier deaths from Maharashtra
		# except:
		# 	pass

		focus = data_series

		fig.add_trace(go.Scatter(x=list(range(0, len(focus))), y=focus,
                     name=state,
                     opacity=1,
                     line=dict(width=5)
                     ))

	fig.update_layout(
					autosize=True,
					# width=800,
					height=800,
					title='Statewise Mortality Progression',title_x=0.5,
	                xaxis_title='Days',
	                yaxis_title='Mortality',
	                legend=dict(orientation="h", xanchor='center', x=0.5, yanchor = 'bottom', y=-0.2),
	                xaxis = dict(
					# tickmode = 'linear',
					# dtick = 0.02,
					linecolor = 'grey'
				    ),
					yaxis = dict(
					# tickmode = 'linear',
					dtick = 0.01,
					linecolor = 'grey'
					)
					)

	fig.layout.yaxis.tickformat = ',.1%'
	# fig.layout.xaxis.tickformat = ',.1%'

	return fig

if __name__ == '__main__':
    app.run_server(debug=True)