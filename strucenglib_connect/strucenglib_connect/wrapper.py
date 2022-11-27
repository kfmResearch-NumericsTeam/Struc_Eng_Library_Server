from strucenglib_connect.client import Client

# RPC wrapper to use with compas.rpc
def do_analyse_and_extract(server, data):
    c = Client(server)
    return c.execute('analyse_and_extract', data)

