import plotly.graph_objects as go
import plotly.express as px

import utils

############################################################
# S: Plots #################################################

def worldPlot(dfNodes, dfEdges):
  fig = go.Figure()

  for _, row in dfEdges.iterrows():
    fig.add_trace(go.Scattergeo(
      lat = row['lat'],
      lon = row['long'],
      # lat = (row['start_lat'], row['end_lat']),
      # long = (row['start_long'], row['end_long']),
      mode = 'lines',
      line = dict(width = 1, color = 'red'),
      opacity = float(row['count'] / dfEdges['count'].max()),
    ))

  fig.add_trace(go.Scattergeo(
    lat = dfNodes['lat'],
    lon = dfNodes['long'],
    hoverinfo = 'text',
    text = dfNodes.index,
    mode = 'markers',
    marker = dict(
      size = 2,
      color = 'rgb(255, 0, 0)',
      line = dict(
        width = 3,
        color = 'rgba(68, 68, 68, 0)',
      ),
    ),
  ))

  fig.update_layout(
    showlegend = False,
    geo = dict(
      projection_type = 'natural earth',
    ),
  )

  utils.saveFig(fig, 'world')
