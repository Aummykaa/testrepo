# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
launch_site = spacex_df['Launch Site']
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                        html.H2('Select Launch Site:', style={'margin-right': '2em'}),
                                        dcc.Dropdown(
                                        id='site-dropdown', 
                                        options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        *[{'label': site, 'value': site} for site in launch_site.unique()]
                                        ],
                                        placeholder="Select a Launch Site here",
                                        searchable=True)
                                        ]),
                                html.Br(),
                                html.Div([
                                        html.H3('Total Success Rate:', style={'margin-right': '4em'}),
                                        html.Div(id='output-text')]),
                                html.Br(),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                id='payload-slider',
                                min=0,
                                max=10000,
                                step=1000,
                                value=[min_payload, max_payload],  # Initial values
                                marks={
                                    0: '0',
                                    2500: '2500',
                                    5000: '5000',
                                    7500: '7500',
                                    10000: '10000'
                                },  # Marks every 2,500 units
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Output(component_id='output-text', component_property='children'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    filtered_df = spacex_df
    mean_per_size = ""
    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Total Success Launches by Site')
        return fig,mean_per_size
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site)]
        count_df = filtered_df.groupby(['class']).size().reset_index(name = 'counts')
        mean_per_size = filtered_df['class'].mean()
        fig = px.pie(count_df, values='counts', 
        names='class', 
        title='Total Success Launches for Site '+ str(entered_site))
        return fig,mean_per_size
        # return the outcomes piechart for a selected site


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),Input(component_id="payload-slider", component_property="value"))

def get_scatter_plot(entered_site,payload):
    filtered_range_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload[0]) & (spacex_df['Payload Mass (kg)'] <= payload[1])]
    if entered_site == 'ALL' or entered_site is None :
        filtered_df = filtered_range_df.groupby(['Booster Version Category','Payload Mass (kg)'])['class'].mean().reset_index()
        fig = px.scatter(filtered_df,
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category', 
        title='Scatter Plot')
    
        return fig
    else:
        filtered_df = filtered_range_df[(filtered_range_df['Launch Site'] == entered_site)]
        filtered_df_group = filtered_df.groupby(['Booster Version Category','Payload Mass (kg)'])['class'].sum().reset_index()
        fig = px.scatter(filtered_df_group, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category', 
        title='Scatter Plot')
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()

#Which site has the largest successful launches?
#>> KSC LC-39A
#Which site has the highest launch success rate?
#>> KSC LC-39A
#Which payload range(s) has the highest launch success rate?
#2-4k
#Which payload range(s) has the lowest launch success rate?
#2.5-5k
#Which F9 Booster version (v1.0, v1.1, FT, B4, B5, etc.) has the highest launch success rate?
#F10