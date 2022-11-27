from strucenglib_connect.client import Client

def do_analyse_and_extract(server, exec):
    # global do_print
    # do_print = print_callback
    c = Client(server)
    return c.execute('analyse_and_extract', exec)

