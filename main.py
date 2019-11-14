from flask_bootstrap import Bootstrap
import dash
from dash.dependencies import Input, Output, State
import app_layout
import graph_server
from flask import Flask, render_template
import map


def save_list_to_file(value_list, file_name):
    # write columns to file
    f = open(file_name, "w")
    f.write("1,2")
    f.close()

    # append values from hash tags to file
    with open(file_name, "a") as f:
        f.write("\n{},{}".format(value_list[0], value_list[1]))
    f.close()

    f = open(file_name, "r")
    map_data = map.pd.read_csv(file_name)

    # sum of all columns
    val1 = map_data['1'].sum()
    set;val2 = map_data['2'].sum()
    f.close()


def get_figure(val1, val2, input1, input2):
    return {
            'data': [
                {'x': [10], 'y': [val1], 'type': 'bar', 'name': input1},
                {'x': [10], 'y': [val2], 'type': 'bar', 'name': input2},
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


# app init
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'https://codepen.io/amyoshino/pen/jzXypZ.css']
server = Flask(__name__, static_folder="/Users/orshulrufer/PycharmProjects/Flask/static")
Bootstrap(server)
app = dash.Dash(__name__,  server=server, routes_pathname_prefix='/dash/', external_stylesheets=external_stylesheets)
app.layout = app_layout.layout


@app.callback(
        dash.dependencies.Output('graph', 'figure'),
        [Input("input1", "value"), Input("input2", "value")])
def update_selected_row_indices(input1, input2):
    # input1 is hash_tag1 input2 is hash_tag2
    value_list = [0, 0]
    # check if there are two inputs

    if not input1 is "":
        if not input2 is "":
            # get list of values from hash tags
            value_list = graph_server.turn_on_graph_app([input1, input2])
    return get_figure(value_list[0], value_list[1], input1, input2)

'''
@server.route('/my_home_page')
def index():
    return render_template('index.html')
'''

@server.route("/")
def graph_example():
    return app.index()


if __name__ == "__main__":
    index = True
    server.run(debug=True, port=5000)

