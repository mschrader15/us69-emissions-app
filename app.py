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

data_dict = pickle.load(open(os.path.join(APP_PATH, os.path.join("data", "emissions_data_binned.pkl")), 'rb'))

data_date = data_dict['params']['start_time']
data_date_dt = datetime.datetime.strptime(data_date, '%m/%d/%Y %H:%M:%S.%f')
data_time_string = str(data_date_dt.month) + '/' +  str(data_date_dt.day) + '/' + str(data_date_dt.year)

max_plot_value = data_dict['params']['max_plot_value']
max_plot_value_sum = data_dict['params']['max_plot_value_summed']

summed_array = data_dict['data']['summed_array']
inst_array = data_dict['data']['inst_array']
step_time_values = data_dict['data']['time_array']
step_num = range(len(step_time_values))

animation_step_duration = 1000
#sigma = 1.5
#gaussian = False
plot_radius = 10
#summed = True

colorbar_font = dict(color="black",
                     family="Courier New, monospace",
                     size=14)

colorscale_log = [
    [0.0, "rgba(0, 255, 204, 0)"],
    [0.2, "rgb(0, 255, 51)"],
    [0.4, "rgb(204, 255, 0)"],
    [0.6, "rgb(255, 204, 51)"],
    [0.8, "rgb(255, 102, 51)"],
    [1.0, "rgb(204,0,0)"],
             ]

colorscale = [
                      [0.0, "rgba(0, 255, 204, 0)"],
                      [0.2, "rgb(0, 255, 51)"],
                      [0.4, "rgb(204, 255, 0)"],
                      [0.6, "rgb(255, 204, 51)"],
                      [0.8, "rgb(255, 102, 51)"],
                      [1.0, "rgb(204,0,0)"],
                 ]

tickvals_log = np.round(np.linspace(np.log10(1e-4), np.log10(max_plot_value_sum), 7), 3)
tickvals_log[0] = -4
ticktext_log = ['{:g}'.format(float('{:.1g}'.format((10 ** exp)*60))) for exp in tickvals_log]
ticktext_log[0] = "0.0"

#max_plot_value = 1.5 # np.amax(inst_array[30][2]) - 6.9
tickvalues = np.around(np.linspace(0, np.round(max_plot_value, 0), 7), 3)
ticktext = [str(val) for val in tickvalues]


log_color_axis = dict(
            cmin=tickvals_log[0],
            cmax=tickvals_log[-1],
            showscale=True,
            colorscale=colorscale_log,
            colorbar=dict(
                outlinecolor="black",
                outlinewidth=2,
                ticks="outside",
                tickfont=colorbar_font,
                tickvals=tickvals_log,
                ticktext=ticktext_log,
                title="[gal]<br /> <br />",
                titlefont=colorbar_font,
            )
)

color_axis = dict(
            cmin=0,
            cmax=max_plot_value,
            showscale=True,
            colorscale=colorscale,
            colorbar=dict(
                outlinecolor="black",
                outlinewidth=2,
                ticks="outside",
                tickfont=colorbar_font,
                tickvals=tickvalues,
                ticktext=ticktext,
                title="[gal/hr]<br /> <br />",
                titlefont=colorbar_font,
            )
)


def geo_located_heatmap(sum):
    
    fig_dict = dict(data=go.Densitymapbox(
        lat=summed_array[0][0] if sum else inst_array[0][0],
        lon=summed_array[0][1] if sum else inst_array[0][1],
        z=np.log10(summed_array[0][2]) if sum else inst_array[0][2],
        customdata=summed_array[0][2],
        hovertemplate='%{customdata}' if sum else None,
        radius=plot_radius,
        hoverinfo='z' if not sum else None,
        coloraxis="coloraxis"),
        layout={},
        frames=[go.Frame(data=go.Densitymapbox(
            lat=summed_array[i][0] if sum else inst_array[i][0],
            lon=summed_array[i][1] if sum else inst_array[i][1],
            z=np.log10(summed_array[i][2]) if sum else inst_array[i][2],
            customdata=summed_array[i][2],
            hovertemplate='%{customdata}' if sum else None,
            radius=plot_radius,
            hoverinfo='z' if not sum else None,
            showscale=False,
        ),
            name=step_time_values[i],
        ) for i in step_num]
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
            zoom=14.1,
        ),
        coloraxis=log_color_axis if sum else color_axis
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
            html.H5('Cumulative Fuel Consumption',
                    style={
                        "text-align": "center",
                        "font-family": colorbar_font['family'],
                        'padding': 10,
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
                      figure=geo_located_heatmap(sum=True),
                      config={'displayModeBar': False},
                      )
        ], className="six columns"),

        html.Div([
            html.H5('Instantaneous Fuel Consumption',
                    style={
                        "text-align": "center",
                        "font-family": colorbar_font['family'],
                        'padding': 10,
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
                      figure=geo_located_heatmap(sum=False),
                      config={'displayModeBar': False},
                      )
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

