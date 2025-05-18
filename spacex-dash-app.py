# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

#cosas auxialires
dropdown_launch_site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout      #Task 1 add dropdown para site launches (Launch Site)
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard', 
                                    style={'textAlign': 'center', 'color': '#503D36','font-size': 40}), 
                                    dcc.Dropdown(id='site-dropdown',
                                    options= dropdown_launch_site_options,
                                    value= 'ALL', placeholder= "Select or Type Launch Site <3",
                                    searchable= True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
# TASK 3: Add a slider to select payload range
                                html.P("Payload range (Kg):"), 
                                dcc.RangeSlider(id='payload-slider', 
                                min=0, max=10000, step=1000, 
                                marks={i: str(i) for i in range(0, 10001, 1000)}, 
                                value=[0, 10000], 
                                tooltip ={"placement": "bottom", "always_visible": True}),
                                

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'), 
                Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    group_by_data = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Success Count')
    if entered_site == 'ALL': 
        fig = px.pie(data_frame= group_by_data, values='Success Count', 
        names='Launch Site', 
        title='Total Successful Launches')
        return fig
    else:
        specific_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = specific_data[specific_data['class'] == 1].shape[0]
        failure_count = specific_data[specific_data['class'] == 0].shape[0]
        pie_data = pd.DataFrame({'Outcome': ['Success', 'Failure'], 
        'Count': [success_count, failure_count]})
        fig = px.pie(data_frame= pie_data, values='Count', names='Outcome', 
        title=f'Outcome of launches at {entered_site}', color='Outcome', 
        color_discrete_map={'Success': 'blue', 'Failure': 'red'})
        return fig
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-chart', component_property='figure'), 
                [Input(component_id='site-dropdown', component_property='value'), 
                Input(component_id='payload-slider', component_property='value')])
####definiendo funcion 
def get_payload_chart(entered_site, payload_range):
    #first filter for payload_range
    payload_range_df= spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    if entered_site == 'ALL':
        ###grafico
        fig2 = px.scatter(data_frame= payload_range_df, 
            x= 'Payload Mass (kg)', y= 'class', 
            color= "Booster Version Category", 
            title='Success vs. Payload for All Sites', 
            hover_data=['Launch Site'])
        return fig2 # use fig2 cause is easier for the reader to understand the code
        #you cna use fig, but i prefer this way for now.
    else: 
        #filter for entered_site
        specific_data2 = payload_range_df[payload_range_df['Launch Site'] == entered_site]
        fig2 = px.scatter(data_frame= specific_data2, 
            x= 'Payload Mass (kg)', y= 'class', 
            color= "Booster Version Category", 
            title= f'Success vs. Payload at {entered_site}', 
            hover_data=['Launch Site'])
        return fig2

# Run the app 
if __name__ == '__main__':
    app.run()