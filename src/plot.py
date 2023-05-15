import plotly.graph_objects as go
import plotly.express as px
import networkx as nx

import utils

############################################################
# S: droppedPlot ###########################################

def droppedPlot(dropNa, dropDrtt):
  fig = go.Figure(go.Histogram(
    # x = [total for total, _ in dropNa]
    x = [100 * pct for _, pct in dropNa]
  ))
  fig.update_layout(
    xaxis_title = 'Porcentaje de paquetes no respondidos',
    yaxis_title = 'Cantidad',
  )
  utils.saveFig(fig, 'dropNa')

  fig = go.Figure(go.Histogram(
    # x = [total for total, _ in dropDrtt]
    x = [100 * pct for _, pct in dropDrtt]
  ))
  fig.update_layout(
    xaxis_title = 'Porcentaje de RTT que dieron negativo',
    yaxis_title = 'Cantidad',
  )
  utils.saveFig(fig, 'dropDrtt')

############################################################
# S: graphPlot #############################################

def graphPlot(G, dfNodes, dfEdges):
  pos = nx.spring_layout(G)
  node_x, node_y = [], []
  for v in dfNodes.index:
    x, y = pos[v]
    node_x.append(x)
    node_y.append(y)

  node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    text = dfNodes.index,
    marker=dict(
      showscale=True,
      # colorscale options
      #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
      #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
      #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
      colorscale = 'Bluered',
      color = dfNodes['count'],
      size=10,
      colorbar=dict(
        thickness=15,
        title='Apariciones',
        xanchor='left',
        titleside='right'
      ),
      line_width=2
    )
  )

  edge_x, edge_y = [], []
  for (v, u) in dfEdges.index:
    (x0, y0), (x1, y1) = pos[v], pos[u]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

  edge_trace = go.Scatter(
    x = edge_x, y = edge_y,
    line = dict(
      width = 0.5,
      color = '#888',
    ),
    hoverinfo = 'none',
    mode = 'lines',
  )

  fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
    title='Grafo de todas las rutas',
    titlefont_size=16,
    showlegend=False,
    hovermode='closest',
    margin=dict(b=20,l=5,r=5,t=40),
    # annotations=[dict(
      # text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
      # showarrow=False,
      # xref="paper", yref="paper",
      # x=0.005, y=-0.002,
    # )],
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
  ))
  utils.saveFig(fig, 'graph')

############################################################
# S: worldPlot #############################################

def _worldPlot(name, dfNodes, dfEdges, getOpacity, nodeColor = 'red', edgeColor = 'red'):
  fig = go.Figure()

  for _, row in dfEdges.iterrows():
    fig.add_trace(go.Scattergeo(
      lat = row['lat'],
      lon = row['long'],
      # lat = (row['start_lat'], row['end_lat']),
      # long = (row['start_long'], row['end_long']),
      mode = 'lines',
      line = dict(width = 1, color = edgeColor),
      opacity = getOpacity(row)
    ))

  fig.add_trace(go.Scattergeo(
    lat = dfNodes['lat'],
    lon = dfNodes['long'],
    hoverinfo = 'text',
    text = dfNodes.index,
    mode = 'markers',
    marker = dict(
      size = 2,
      color = nodeColor,
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

  utils.saveFig(fig, name)

def worldPlot(dfNodes, dfEdges):
  _worldPlot('world_count', dfNodes, dfEdges, lambda row: float(row['count'] / dfEdges['count'].max()))

  _worldPlot('world_naive', dfNodes, dfEdges[dfEdges['naive_pred']], lambda row: float(1))
  _worldPlot('world_cimbala', dfNodes, dfEdges[dfEdges['cimbala_pred']], lambda row: float(1))
  _worldPlot('world_cimbalaAlt', dfNodes, dfEdges[dfEdges['cimbalaAlt_pred']], lambda row: float(1))

  _worldPlot('world_naive_mean', dfNodes, dfEdges, lambda row: float(row['naive_pred_mean']))
  _worldPlot('world_cimbala_mean', dfNodes, dfEdges, lambda row: float(row['cimbala_pred_mean']))
  _worldPlot('world_cimbalaAlt_mean', dfNodes, dfEdges, lambda row: float(row['cimbalaAlt_pred_mean']))
