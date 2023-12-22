# Import packages
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State  # Updated import
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objs as go



# Initialize the app
app = Dash(__name__)
server = app.server

# Initialize an empty DataFrame
df = pd.DataFrame()

try:
    # Read data from formatted_data.txt with explicit encoding
    df = pd.read_csv("formatted_data.txt", encoding='utf-8-sig', parse_dates=[0, 7, 8], dayfirst=True,
                     names=["Last Updated Date", "Location", "Type", "Task", "Phase", "PM", "Tier", "Start", "Finish"],
                     skipinitialspace=True)

    # Sort the DataFrame by 'Start' date
    df.sort_values(by="Start", ascending=False, inplace=True)

    # Check if the DataFrame is not empty and columns exist
    if not df.empty and {'Last Updated Date', 'Start', 'Finish', 'Task'}.issubset(df.columns):
        # Aggregate start and finish times for each task and merge
        project_timeframes = df.groupby('Task').agg({'Start': 'min', 'Finish': 'max'}).reset_index()
        df = df.merge(project_timeframes, on='Task', suffixes=('', '_Project'))
        # Update the last updated date in the app layout
        last_updated_date_str = df['Last Updated Date'].max().strftime("%Y-%m-%d")
    else:
        last_updated_date_str = "N/A"

except Exception as e:
    last_updated_date_str = "N/A"
    print(f"An error occurred: {e}")

# Initialize the app
app = Dash(__name__)
server= app.server

# Define custom color maps
phase_colors = {
    'Stage 0': '#5c9977', #
    'Stage 1': '#faca78', #
    'Stage 2': '#a163a2', #
    'Stage 3': '#BB8B3F', #Gullfaxi
    'Stage 4': '#DB2A12', #Hekla
    'Procurement':'#00969e',
    'Stage 5': '#004DF4', #Geysir
    'Stage 6': '#e0dd1b'  #
}

pm_colors = {
    'Ingvar Baldursson': '#1a2c79',  # Light Salmon
    'Benedikt Magnússon': '#e6a26e',     # Pale Green
    'Daníel Hólmgrímsson': '#7eed94',    # Light Blue
    'Mike McGarvey': '#a163a2',  # Light Green
    'Guttormur Guttormsson': '#64a6ea',     # Light Pink
    'Sigurður Jens': '#f28322',  # Plum
    'Gísli Guðmundsson': '#f2e291',     # Pale Turquoise
    'Brynjar Vatnsdal': '#FFFF99',     # Light Yellow
    'Jóhannes B': '#d94b2b',    # Peach Puff
    'Hartmann Rúnarsson': '#15aebf',     # Powder Blue
    'Siggi Kristó': '#4988bf',   # Pink
    'Bjarni Jakob': '#f5d698',   # 
    'xx': '#cfcfcf'   # 
    # ... add more PMs/colors as needed
}

# Get current date
current_date_str = datetime.now().strftime("%Y-%m-%d")

type_options = [{'label': t, 'value': t} for t in df['Type'].unique()]
# Define a CSS style for the filter div containers
filter_container_style = {
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'flex-start',  # Align items to the top
    'paddingRight': '10px',
    'minWidth': '110px',
    #'maxWidth': '120px'
}



# Filters and sorting options container style
filter_sort_container_style = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'alignItems': 'flex-start',
    'justifyContent': 'space-between',
    'marginBottom': '20px',
    'padding': '0 20px',
    'zIndex': '5'  # Ensure this is lower than the dropdown z-index
}

# Dropdown container style
dropdown_container_style = {
    'position': 'absolute',  # Position it absolutely to place it on top of other elements
    'right': '1%',  # Adjust this value as needed to position from the right
    'top': '170px',  # Adjust top as needed to clear the header
    'zIndex': '10',  # Higher z-index to stack above the graph
    'width': 'auto',  # Adjust width as necessary
    #'width': '200px',
    'display': 'flex',  # Using flex to align side by side
    'overflowY': 'visible',  # Allow the dropdown content to overflow
    'marginBottom': '10px',
    'marginLeft': '20px',
    'marginRight': '10px'
}
# Individual dropdown details style
dropdown_details_style = {
    'display': 'inline-block',  # Using inline-block for side by side layout
    'width': 'auto',  # Set to auto or specific width as per design requirement
    'verticalAlign': 'top',  # To align at the top if they have different heights
    'marginRight': '10px',  # Space between dropdowns
    'border': '1px solid #d3d3d3',
    'borderRadius': '4px',
    'padding': '5px',
    'background-color': '#f8f9fa'
}
# Sort the project list alphabetically
project_options = [{'label': project, 'value': project} for project in sorted(df['Task'].unique())]

# Options for stages
stage_options = [{'label': stage, 'value': stage} for stage in df['Phase'].unique()]

# Options for PMs
pm_options = [{'label': pm, 'value': pm} for pm in sorted(df['PM'].unique())]



#isavia blue : #4396a7 orange:#e65500
# App layout
app.layout = html.Div(style={'backgroundColor': 'white', 'color': '#101010', 'fontFamily': 'Arial'}, children=[
    
    # Header
    html.Div([
        html.Div([
            html.H1([
                html.Span('Projects', style={"color": "#101010", "fontWeight": "bold"}),
                html.Span('Timeline', style={"color": "#004DF4", "fontWeight": "bold"})
            ], style={
                "marginLeft": "20px",  # Ensure some space on the left
                "fontSize": "48px",  # Maintain large font size for visibility
                "padding": "10px"  # Add some padding around the text
            }),
        ], style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'middle'}),
        
        # Logo container
        html.Div([
            html.Img(src="/assets/isavia_logo.png",
                    style={
                        "height": "80px",  # Adjusted height for the logo
                        "marginRight": "30px",  # Space between logos
                        "verticalAlign": "middle",  # Aligns the image vertically in the middle
                        "filter": "grayscale(100%)"  # Converts the image to black and white
                    }),
            html.Img(src="/assets/KEF-EN-svart.png",
                    style={
                        "height": "80px",  # Adjusted height for the logo
                        "verticalAlign": "middle",  # Aligns the image vertically in the middle
                        "filter": "grayscale(100%)"  # Converts the image to black and white
                    }),
        ], style={'display': 'inline-block', 'width': '50%', 'textAlign': 'right'}),

        
    ], style={"textAlign": "left", "padding": "20px 0", "lineHeight": "30px"}),  # lineHeight helps vertically center the text and logos

    # New Div for Last Updated Date
    html.Div([
        html.P("Last Updated: " + last_updated_date_str, style={
            'textAlign': 'right',
            'color': '#101010',
            'fontSize': '14px',
            'marginRight': '20px',
            'marginTop': '20px'
        })
    ], style={'position': 'absolute', 'top': 0, 'right': 0}),  # Adjust positioning as needed

    # Filters and sorting options
    html.Div(style=filter_sort_container_style, children=[
        # Filter by PM/Phase
        html.Div([
            html.Label('Color by:', style={'paddingRight': '10px'}),
            dcc.RadioItems(
                options=[
                    {'label': 'Stages', 'value': 'Phase'},
                    {'label': 'PM', 'value': 'PM'}
                ],
                value='Phase',
                id='color-radio-items',
                inline=True,
                style={"color": "black"}
            ),
        ], style=filter_container_style),

        # Filter Data by Location
        html.Div([
            html.Label('Location:', style={'paddingRight': '10px'}),
            dcc.Checklist(
                options=[
                    {'label': 'Terminals', 'value': 'Terminals'},
                    {'label': 'Airfield', 'value': 'Airfield'},
                    {'label': 'Landside', 'value': 'Landside'}
                ],
                value=['Terminals', 'Airfield'],  # All options selected by default
                id='location-checklist-items',
                style={"color": "black"}
            ),
        ], style=filter_container_style),

        # Filter Data by Type
        html.Div([
            html.Label('Type:', style={'paddingRight': '10px'}),
            dcc.Checklist(
                options=[
                    {'label': 'Building', 'value': 'Building'},
                    {'label': 'Civil', 'value': 'Civil'},
                    {'label': 'Utilities', 'value': 'Utilities'},
                    {'label': 'Strategies and Plans', 'value': 'Strategies and Plans'},
                    {'label': 'MOI', 'value': 'MOI'}
                ],
                value=['Building', 'Civil'],  # All options selected by default
                id='type-checklist-items',
                style={"color": "black"}
            ),
        ], style=filter_container_style),

        # Filter Data by Tier
        html.Div([
            html.Label('Filter by Tier:', style={'paddingRight': '10px'}),
            dcc.Checklist(
                options=[
                    {'label': 'Tier 1', 'value': '1'},
                    {'label': 'Tier 2', 'value': '2'},
                    {'label': 'Tier 3', 'value': '3'}
                ],
                value=['1', '2', '3'],  # All options selected by default
                id='tier-checklist-items',
                style={"color": "black"}
            ),
        ], style=filter_container_style),
        
        # Dropdown for sorting options
        html.Div([
            html.Label('Sort Projects By:', style={'paddingRight': '10px'}),
            dcc.Dropdown(
                id='sort-dropdown',
                options=[
                    {'label': 'Project Start', 'value': 'Project_Start'},
                    {'label': 'Project Finish', 'value': 'Project_Finish'},
                    {'label': 'Start of Stage 3', 'value': 'Stage_3_Start'},  
                    {'label': 'Start of Procurement', 'value': 'Procurement_Start'},  
                    {'label': 'Start of Construction', 'value': 'Stage_5_Start'},
                    {'label': 'Project Manager (PM)', 'value': 'PM'},
                    {'label': 'Alphabetically', 'value': 'Task'},  # Added this line

                    # ... (add other stages as needed)
                ],
                value='Project_Start',
                clearable=False,
                style={"width": "100%"}
            ),
        ], style=filter_container_style),

        # Button for toggling range slider
        html.Div([
            html.Button('Timeline Slider', id='toggle-slider-button', n_clicks=0, style={
                'backgroundColor': '#004DF4',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'padding': '10px 20px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'outline': 'none',
                'marginRight': '10px',  # Add space to the right of the button
            })
            
        ], style=filter_container_style),


        # An invisible container that still takes up space
        html.Div(style={
            #'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'flex-start',  # Align items to the top
            'paddingRight': '10px',
            'height': '150px', 
            'width': '400',
            'visibility': 'hidden',
            'minWidth': '400px'
            }),



        # Dropdown container
        html.Div(style=dropdown_container_style, children=[
            # Your dropdown details/checklists here
            html.Details([
                html.Summary('Select Stages:', style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='stage-checklist-items',
                    options=stage_options,
                    value=[],
                    style={"color": "black"}
                )
            ], style=dropdown_details_style),
            html.Details([
                html.Summary('Select PMs:', style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='pm-checklist-items',
                    options=pm_options,
                    value=[],
                    style={"color": "black"}
                )
            ], style=dropdown_details_style),
            # New dropdown for filtered projects
            html.Details([
                html.Summary('Select Projects:', style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='filtered-project-list-checklist',
                    options=[],  # Initially empty, will be populated dynamically
                    value=[],
                    #multi=True,  # Allows selection of multiple projects
                    style={"color": "black"}
                )
            ], style=dropdown_details_style),
        ]),
    ]),

    # Graph container with lower z-index
    dcc.Graph(id='gantt-chart-placeholder', style={
        "height": "1000px",
        "backgroundColor": "#4396a7",
        'zIndex': '1'  # Ensure this is lower than the dropdown z-index
    }),
])


# Refactored function for filtering DataFrame
def filter_dataframe(df, selected_tiers, selected_location_categories, selected_types, selected_stages):
    # Apply Location filter
    if selected_location_categories:
        df = df[df['Location'].isin(selected_location_categories)]

    # Apply Type filter
    if selected_types:
        df = df[df['Type'].isin(selected_types)]

    # Apply Tier filter
    if selected_tiers and 'All' not in selected_tiers:
        df = df[df['Tier'].isin(selected_tiers)]

    # Apply Stage filter
    if selected_stages:
        df = df[df['Phase'].isin(selected_stages)]

    return df




# Function to aggregate and merge data
def aggregate_and_merge_data(filtered_df):
    # Calculate the minimum start date and maximum finish date for each task
    project_start_finish = filtered_df.groupby('Task').agg(Project_Start=('Start', 'min'), 
                                                           Project_Finish=('Finish', 'max')).reset_index()

    # Merge the project_start_finish dataframe with the filtered_df
    filtered_df = filtered_df.merge(project_start_finish, on='Task')

    # Additional aggregation and merging for different stages
    # Stage 5 Start
    stage_5_start_df = filtered_df[filtered_df['Phase'] == 'Stage 5'].groupby('Task')['Start'].min().reset_index()
    stage_5_start_df = stage_5_start_df.rename(columns={'Start': 'Stage_5_Start'})
    filtered_df = filtered_df.merge(stage_5_start_df, on='Task', how='left')

    # Procurement Start
    procurement_start_df = filtered_df[filtered_df['Phase'] == 'Procurement'].groupby('Task')['Start'].min().reset_index()
    procurement_start_df = procurement_start_df.rename(columns={'Start': 'Procurement_Start'})
    filtered_df = filtered_df.merge(procurement_start_df, on='Task', how='left')

    # Stage 3 Start
    stage_3_start_df = filtered_df[filtered_df['Phase'] == 'Stage 3'].groupby('Task')['Start'].min().reset_index()
    stage_3_start_df = stage_3_start_df.rename(columns={'Start': 'Stage_3_Start'})
    filtered_df = filtered_df.merge(stage_3_start_df, on='Task', how='left')

    return filtered_df


# Function for sorting DataFrame
def sort_dataframe(filtered_df, sort_column):
    if sort_column == 'Task':
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=False)
    else:
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=False, na_position='first')
    return sorted_df.reset_index(drop=True)


# Function to create Gantt Chart
def create_gantt_chart(sorted_df, color_column, task_order, pm_colors, phase_colors):
    # Set the figure size or layout properties to adjust the width
    fig = go.Figure()
    fig.update_layout(
        # ... (your existing layout updates)
        width=900,  # Adjust width as necessary to fit the sidebar
        # ... (other layout properties)
    )
        # Check if the DataFrame is empty
    if sorted_df.empty:
        return None
        # Check the value of color_column and create the Plotly timeline accordingly
    if color_column == 'PM':
        fig = px.timeline(sorted_df, x_start="Start", x_end="Finish", y="Task", 
                        color="PM", hover_name="Phase", 
                        labels={"Task": "Projects", "Phase": "Project Phase", "PM": "Project Manager"},
                        color_discrete_map=pm_colors,  # Use the PM color map
                        category_orders={"Task": task_order},  # Specify the order of tasks
                        hover_data={"Start": True, "Finish": True, "Tier": True, "Location": True, "Type": True})  # Include 'Tier' in hover data
        # Disable legend interactivity
        fig.update_layout(legend=dict(itemclick=False, itemdoubleclick=False))

    else:
        fig = px.timeline(sorted_df, x_start="Start", x_end="Finish", y="Task", 
                        color="Phase", hover_name="PM", 
                        labels={"Task": "Projects", "Phase": "Project Phase", "PM": "Project Manager"},
                        color_discrete_map=phase_colors,  # Use the Phase color map
                        category_orders={"Task": task_order},  # Specify the order of tasks
                        hover_data={"Start": True, "Finish": True, "Tier": True, "Location": True, "Type": True})  # Include 'Tier' in hover data

            # Turn off the default legend
        fig.update_layout(showlegend=False)

        # Use the phase_colors dictionary directly to create custom legend items
        legend_items = list(phase_colors.items())
        legend_items.reverse()

        # Define starting positions
        legend_x_start = 1.02  # X position of legend start (right of the graph)
        legend_y_start = 1  # Y position of legend start (top of the graph)

        # Define legend aesthetics
        color_block_width = 0.03  # Width of the color block
        color_block_height = 0.025  # Height of the color block
        text_padding_from_block = 0.01  # Space between color block and text
        vertical_space_between_items = 0.01  # Space between legend items

        # Create the custom legend
        for i, (label, color) in enumerate(legend_items):
            # Determine the y position for the current item
            current_y_position = legend_y_start - i * (color_block_height + vertical_space_between_items)

            # Add the color block
            fig.add_shape(
                type="rect",
                xref="paper", yref="paper",
                x0=legend_x_start, y0=current_y_position,
                x1=legend_x_start + color_block_width, y1=current_y_position - color_block_height,
                fillcolor=color,
                line=dict(color=color),
            )

            # Add the label text
            fig.add_annotation(
                xref="paper", yref="paper",
                x=legend_x_start + color_block_width + text_padding_from_block, y=current_y_position - (color_block_height / 2),
                text=label,
                showarrow=False,
                align="left",
                font=dict(size=12, color="black"),
                xanchor="left",
                yanchor="middle",
            )

        # Update the layout to accommodate the custom legend
        fig.update_layout(
            margin=dict(r=160),  # Adjust right margin to fit the legend
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    return fig


# Function to add a current date line to the figure
def add_current_date_line(fig):
    current_date = datetime.now().date()
    fig.add_shape(
        type="line",
        x0=current_date,
        x1=current_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="Black", width=2),
    )
    fig.add_annotation(
        x=current_date,
        y=1.025,
        yref="paper",
        showarrow=False,
        xanchor="right",
        text="Today",
        bgcolor="black",
        opacity=0.7,
        font=dict(color="white")
    )

# Function to toggle range slider visibility
def toggle_range_slider(fig, n_clicks):
    fig.update_layout(xaxis_rangeslider_visible=(n_clicks % 2 == 1))


    
@app.callback(
    Output('filtered-project-list-checklist', 'options'),
    [
        Input('location-checklist-items', 'value'),
        Input('type-checklist-items', 'value'),
        Input('tier-checklist-items', 'value'),
        Input('stage-checklist-items', 'value'),
        Input('pm-checklist-items', 'value')
    ]
    #[State('project-list-checklist', 'value')]  # Include the full project list state if needed
)
def update_filtered_project_checklist(selected_locations, selected_types, selected_tiers, selected_stages, selected_pms):
    # Perform filtering based on the checklist values
    filtered_df = filter_dataframe(df, selected_tiers, selected_locations, selected_types, selected_stages)
    
    # Further filter based on selected PMs
    if selected_pms:
        filtered_df = filtered_df[filtered_df['PM'].isin(selected_pms)]

    # If no data to display after filters, prevent the update
    if filtered_df.empty:
        raise PreventUpdate

    # Create project checklist options based on the filtered dataframe
    project_checklist_options = [{'label': project, 'value': project} for project in sorted(filtered_df['Task'].unique())]

    return project_checklist_options

@app.callback(
    Output('gantt-chart-placeholder', 'figure'),
    [
        Input('color-radio-items', 'value'),
        Input('location-checklist-items', 'value'),
        Input('type-checklist-items', 'value'),
        Input('tier-checklist-items', 'value'),
        Input('stage-checklist-items', 'value'),
        Input('pm-checklist-items', 'value'),
        Input('toggle-slider-button', 'n_clicks'),
        Input('sort-dropdown', 'value'),
        Input('filtered-project-list-checklist', 'value')  # New input for the filtered project list
    ]
)
def update_graph(color_column, selected_location_categories, selected_types, selected_tiers, selected_stages, 
                 selected_pms, n_clicks, sort_column, filtered_projects):
    # Proceed with filtering if location categories are selected
    if not selected_location_categories:
        return go.Figure()

    # Filter the DataFrame based on the selected filters
    filtered_df = filter_dataframe(df, selected_tiers, selected_location_categories, selected_types, selected_stages)

    # Filter based on selected PMs
    if selected_pms:
        filtered_df = filtered_df[filtered_df['PM'].isin(selected_pms)]

    # Further filter the dataframe based on selected projects from the filtered checklist
    if filtered_projects:
        filtered_df = filtered_df[filtered_df['Task'].isin(filtered_projects)]

    # Aggregate and merge data
    filtered_df = aggregate_and_merge_data(filtered_df)

    # Sort the DataFrame
    sorted_df = sort_dataframe(filtered_df, sort_column)

    # Determine the order of tasks
    task_order = sorted_df['Task'].unique().tolist()
    task_order.reverse()
    
    # Create the Gantt chart
    fig = create_gantt_chart(sorted_df, color_column, task_order, pm_colors, phase_colors)

    # Add current date line and toggle range slider if the figure is not None
    if fig is not None:
        add_current_date_line(fig)
        toggle_range_slider(fig, n_clicks)

    # If there's no data to display after filtering
    else:
        fig = go.Figure()
        fig.update_layout(title="No Data to Display")

    return fig




# This is just for demonstration, you can integrate it with your main app script.
if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=True, host='0.0.0.0')

