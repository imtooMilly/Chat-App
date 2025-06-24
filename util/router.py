import re
from util.request import Request

# Create helper functions for add_route below for each route in the app
def send404():
    message = b'The path you request does not exist, you not loading anything bruh, try again'
    response = 'HTTP/1.1 404 PAGE NOT FOUND\r\nX-Content-Type-Options: nosniff\r\n' 
    contentType = 'Content-Type: text/plain'
    contentLen = 'Content-Length: ' + str(len(message))
    response  = (response + contentType + '\r\n' + contentLen + '\r\n\r\n').encode() + message
    return response

class Router:

    def __init__(self):
        # Create an initializer for router
        self.routes = []
        return

        

    def add_route(self, method, path, function):
        rePath = re.compile(path)
        self.routes.append([method, rePath, function])
        return

    
    def route_request(self, request: Request) -> bytes:
        # store the request method and path
        method = request.method
        path = request.path

        for element in self.routes:
            rePath = element[1]
            function = element[2]

            if method == element[0] and rePath.match(path):
                response = function(request)
                return response
        response = send404()
        return response
