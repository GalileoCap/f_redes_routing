import plotly.graph_objects as go
import plotly.express as px
import networkx as nx

import utils

############################################################
# S: Plots #################################################

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
