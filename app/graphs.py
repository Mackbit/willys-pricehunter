import plotly.graph_objs as _pl_go
import plotly
import json



def create_scatter_plot(names, x, y, x_title, y_title, title):
    hovertext = []
    for label, _x, _y in zip(names, x, y):
        hovertext.append('<b>{}:</b><br>{}={}, {}={}'.format(label, x_title, _x, y_title, _y))
    return json.dumps([_pl_go.Scatter(x=x, y=y, mode='markers+text', name=title, text=names, textposition="top center", marker={'color': 'rgb(55, 83, 109)', 'size': 20},
                      hoverinfo='text', hovertext=hovertext,
                      hoverlabel={'bgcolor': 'rgba(0, 0, 0, 0.82)', 'bordercolor': 'rgba(0, 0, 0, 0.92)', 'font': {'color': "#ffffff"}}, )],cls=plotly.utils.PlotlyJSONEncoder)


def create_multiline_plot(dates, values, title, fillcolor, linecolor):
    data = []
    for v, t, fc, lc in zip(values, title, fillcolor, linecolor):
        data.append(_pl_go.Scatter(x=dates, y=v, mode='lines+markers', fill='tozeroy', name=t,
                      fillcolor=fc, line={'color': lc, 'shape': 'hv'}, cliponaxis=False))

    return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)