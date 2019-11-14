import dash_core_components as dcc
import dash_html_components as html



colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#999999"
}


layout = html.Div(
    html.Div([
        html.Div(
            [
                html.H1(children='Compare two things by tweets',
                        className='nine columns'),
                html.Img(
                    src="https://www.quotewerks.com/images/FeatureImages/CompareConsumerPricing.png",
                    className='three columns',
                    style={
                        'height': '15%',
                        'width': '15%',
                        'float': 'right',
                        'position': 'relative',
                        'margin-top': 10,
                    },
                ),
                html.Div(html.H1(style={'color': 'yellow', 'fontSize': 30}, children='''
                        Enter two hash tags for compare them on twitter.
                        '''), className='ten columns'
                         )
            ], className="row"
        ),

        # text input
        html.Div(
            [
                dcc.Input(id="input1", type="text", placeholder="first hashtag"),
                dcc.Input(id="input2", type="text", placeholder="second hashtag", debounce=True),
            ], className="column"
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(style={"color": "gray",  'backgroundColor': 'gray'},
                            id='graph',
                            figure={
                                'data': [
                                    {'x': [1], 'y': [5], 'type': 'bar', 'name': 'one'},
                                    {'x': [1], 'y': [5], 'type': 'bar', 'name': 'two'},
                                ],
                                'layout': {
                                    'title': 'compare graph',

                                    'yaxis': dict(
                                        title='Difference in the amount of tweets',
                                        titlefont=dict(
                                            family='Helvetica, monospace',
                                            size=20,
                                            color='#7f7f7f'
                                        ))
                                }
                            }
                        )
                    ], className='ten columns'
                ),
            ], className="row"
        )
    ], className='twelve columns', style={'backgroundColor': 'gray'})
)


