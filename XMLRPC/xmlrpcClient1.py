import xmlrpc.client

# Servidores de Insultos 
server_urls = [
    'http://localhost:8000',  
    'http://localhost:8001',  
    'http://localhost:8002'   
]

# Conectar al servidor de insultos en el puerto 8000
s = xmlrpc.client.ServerProxy(server_urls[0])

print(s.system.listMethods())

# Suscribir los observadores (8001 y 8002) al servidor de insultos (8000)
for url in server_urls[1:]:
    try:
        print(f"Suscribiendo a {url}...")
        s.subscribe(url.split('//')[1])  
    except Exception as e:
        print(f"No se pudo suscribir a {url}: {e}")

# Añadir un insulto al servidor principal
print(s.add_insults("cul d'olla"))
print(s.get_insults())

s = xmlrpc.client.ServerProxy(server_urls[1])
print(s.get_insults())

s = xmlrpc.client.ServerProxy(server_urls[2])
print(s.get_insults())