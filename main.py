import socket

from pubsub.server import Server

hostname = socket. gethostname()
local_ip = socket. gethostbyname(hostname)
Server.start_server(host=local_ip)

