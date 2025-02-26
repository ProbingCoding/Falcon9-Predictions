# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                
                                # Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    ],
                                    value='ALL',
                                    placeholder="Select a launch site",
                                    searchable=True
                                ),
                                
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                # Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        100: '100'},
                                    value=[min_payload, max_payload])

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
""" 
Function to adapt data set and hence the related pie chart according to site-dropdown input 
"""  
    if entered_site == 'ALL':
        data = spacex_df.groupby('Launch Site')['Class'].sum().reset_index()   
        fig = px.pie(data, values='class', 
        names='Launch Site', 
        title='Pie Chart Visualising Successful Falcon 9 Launches By Launch Site')
        return fig
    
    else:
        data = spacex_df[spacex_df['Launch Site'] == entered_site]
        data = data.groupby(['Launch Site', 'class']).size().reset_index(name='Class Count')
        fig = px.pie(data, value='Class Count',
                    names='class',
                    title=f'Pie Chart Visualising Successful Falcon 9 Launches From Site {entered_site}')
        return fig
      
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
""" 
Function to adapt data set and hence the related scatter chart according to site-dropdown & payload-slider inputs 
"""
    # Filter data by payload range
    data = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                      (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    if entered_site == 'ALL':
        fig = px.scatter(data, x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Scatter Graph Visualising Payload Mass vs. Success For All Sites'
        return fig
    
    else:
      data = data[data['Launch Site'] == entered_site]
      fig = px.scatter(data, x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Scatter Graph Visualising Payload Mass vs. Success For Site {entered_site}'
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
