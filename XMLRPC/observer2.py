from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8011),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Register a function under a different name
    def notify(insult):
        print(f"Se ha añadido el insulto {insult} correctamente")
        return 1
    server.register_function(notify, 'notify')
    # Register recive insult function
    def recive(insult):
        print(f"Recived {insult}")
        return 1
    server.register_function(recive, 'recive')

    # Run the server's main loop
    server.serve_forever()