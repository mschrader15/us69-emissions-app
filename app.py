import os
import pathlib
import numpy as np
import plotly.graph_objects as go
import pickle
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime

mapbox_key = "pk.eyJ1IjoibWF4LXNjaHJhZGVyIiwiYSI6ImNrOHQxZ2s3bDAwdXQzbG81NjZpZm96bDEifQ.etUi4OK4ozzaP_P8foZn_A"

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

inst_array = pickle.load(open(os.path.join(APP_PATH, os.path.join("data", "inst_array.txt")), 'rb'))
summed_array = pickle.load(open(os.path.join(APP_PATH, os.path.join("data", "summed_array.txt")), 'rb'))

data_date = '02/14/2020 07:00:00.000'
data_date_dt = datetime.datetime.strptime(data_date, '%m/%d/%Y %H:%M:%S.%f')
data_time_string = str(data_date_dt.month) + '/' +  str(data_date_dt.day) + '/' + str(data_date_dt.day)\
                   #+ ' ' + str(data_date_dt.hour) + ":00:00"

max_plot_value = 10
max_plot_value_sum = 1000

animation_step_duration = 1000
sigma = 1.5
gaussian = False
plot_radius = 20
summed = True

colorbar_font = dict(color="black",
                     family="Courier New, monospace",
                     size=14)

def geo_located_heatmap(sum):
    
    fig_dict = dict(data=go.Densitymapbox(
        lat=summed_array[0][0] if sum else inst_array[0][0],
        lon=summed_array[0][1] if sum else inst_array[0][1],
        z=summed_array[0][2] if sum else inst_array[0][2],
        radius=plot_radius,
        hoverinfo='z',
        coloraxis="coloraxis"),
        layout={},
        frames=[go.Frame(data=go.Densitymapbox(
            lat=summed_array[i][0] if sum else inst_array[i][0],
            lon=summed_array[i][1] if sum else inst_array[i][1],
            z=summed_array[i][2] if sum else inst_array[i][2],
            radius=plot_radius,
            hoverinfo='z',
            showscale=False,
        ),
            name=(data_date_dt + datetime.timedelta(seconds=i + 150)).strftime("%H:%M:%S"),
        ) for i in range(25)]
    )

    fig_dict['layout'] = dict(
        # title={"text": "Fuel Consumption", "font": colorbar_font, 'yanchor': 'middle', 'xanchor': 'center'} if sum
        # else {"text": "Instantaneous Fuel Consumption", "font": colorbar_font, 'yanchor': 'middle', 'xanchor': 'center'},
        font=colorbar_font,
        paper_bgcolor='rgb(249, 249, 249)',
        hovermode='closest',
        margin=go.layout.Margin(
            l=20,  # left margin
            r=0,  # right margin
            b=5,  # bottom margin
            t=0  # top margin
        ),
        mapbox=dict(
            accesstoken=mapbox_key,
            bearing=0,
            style='mapbox://styles/max-schrader/ck8t1cmmc02wk1it9rv28iyte',
            center=go.layout.mapbox.Center(
                lat=33.12627,
                lon=-87.54891
            ),
            pitch=0,
            zoom=14,
        ),
        coloraxis=dict(
            cmin=0,
            cmax=max_plot_value_sum if sum else max_plot_value,
            showscale=True,
            colorbar=dict(
                outlinecolor="black",
                outlinewidth=2,
                ticks="outside",
                tickfont=colorbar_font,
                title="(g)" if sum
                else "(g/s)",
                titlefont=colorbar_font,
                # tickformatstops=[dict(dtickrange=[16, 20], )]
            ),
        )
    )

    sliders = [
        {
            "currentvalue": {
                "font": colorbar_font,
                "prefix": "Time: ",
                "visible": True,
                "xanchor": "right"
            },
            "pad": {"b": 10, "t": 20},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "visible": True,
            "steps": [
                {
                    "args": [[f.name], {"frame": {"duration": animation_step_duration, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": animation_step_duration}}
                             ],
                    "label": f.name,
                    "method": "animate",
                }
                for f in fig_dict['frames']
            ],
        }
    ]

    # noinspection PyTypeChecker
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": animation_step_duration, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": animation_step_duration,
                                                   "easing": "linear"}
                                    }
                             ],
                    "label": "&#9654;",  # play symbol
                    "method": "animate",
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "&#9724;",  # pause symbol
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 20},
            "type": "buttons",
            "x": 0.1,
            "y": 0,
        }
    ]

    fig_dict["layout"]["sliders"] = sliders

    fig = go.Figure(fig_dict)

    #fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    #fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    # return fig_dict
    return fig


# fig.write_html("visualization.html")

# geo_located_heatmap(emissions_map=emissions_map, sum=False).show()

# fig.show()
#


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.H4('US69 Fuel Consumption Estimation on {0}'.format(data_time_string),
            style={
                "text-align": "center",
                "font-family": colorbar_font['family'],
                'background-color': "#f9f9f9",
                'margin': 5,
                'padding': 10,
                'position': "relative",
                # 'bottom-border-width': 3,
                # 'bottom-border-style': 'solid',
                # 'bottom-border-color': 'lightslategray',
                'box-shadow': "2px 2px 2px darkgrey",
            }),
    html.Div([
        html.Div([
            html.H5('Cummulative Fuel Consumption (g)',
                    style={
                        "text-align": "center",
                        "font-family": colorbar_font['family'],
                    }
                    ),
            dcc.Graph(id="summed",
                      style={
                          'height': 700,
                          # "border-radius": 5,
                          'background-color': "#f9f9f9",
                          # 'margin': 5,
                          # 'padding': 10,
                          'position': "relative",
                          # 'box-shadow': "2px 2px 2px lightgrey",
                      },
                      figure=geo_located_heatmap(sum=True))
        ], className="six columns"),

        html.Div([
            html.H5('Instantaneous Fuel Consumption (g/s)',
                    style={
                        "text-align": "center",
                        "font-family": colorbar_font['family'],
                    }
                    ),
            dcc.Graph(id="instant",
                      style={
                          'height': 700,
                          # "border-radius": 5,
                          'background-color': "#f9f9f9",
                          # 'margin': 5,
                          # 'padding': 10,
                          'position': "relative",
                          # 'box-shadow': "2px 2px 2px lightgrey",
                      },
                      figure=geo_located_heatmap(sum=False))
        ], className="six columns"),
    ], style={
        'height': 800,
        "border-radius": 5,
        'background-color': "#f9f9f9",
        'margin': 5,
        'padding': 10,
        'position': "relative",
        'box-shadow': "2px 2px 2px lightgrey",
    }, ),  # className="row"),
])

if __name__ == '__main__':
    app.run_server(debug=True)

