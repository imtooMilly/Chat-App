import socketserver
import math 
import html
from util.request import Request
from util.router import Router
from util.serveStatics import *
from util.database import *
from util.auth import *
from util.redirects import *
from util.websockets import *
from util.socketFunctions import *

router = Router()
# get routes
router.add_route("GET", '/$', serve_html)
router.add_route("GET", '/public/style.css', serve_css)
router.add_route("GET", '/public/functions.js', serve_js)
router.add_route("GET", '/public/webrtc.js', serve_js)
router.add_route("GET", '/public/authenticate.js', serve_js)
router.add_route("GET", '/public/favicon.ico', serve_fav)
router.add_route("GET", '/public/image/.', serveMedia)
router.add_route("GET", '/public/video/.', serveMedia)
router.add_route("GET", '/chat-messages', getChatMessage)
router.add_route("GET", '/chat-messages/.', getChatMessage)
#router.add_route("GET", '/websocket', doHandshake)
router.add_route("GET", '/chat-history', getChatHistory)
# post routes
router.add_route("POST", '/chat-messages', postChatMessage)
router.add_route("POST", '/register', serveRegister)
router.add_route("POST", '/login', serveLogin)
router.add_route("POST", '/logout', serveLogout)
router.add_route("POST", '/media-upload', postMedia)
# delete routes
router.add_route("DELETE", '/chat-messages', deleteChatMessage)
# put routes
router.add_route("PUT", '/chat-messages', putChatMessage)

websocketConnections = {}



class MyTCPHandler(socketserver.BaseRequestHandler):


    def handle(self):
            # this code was for https, AJAX, and polling:
            received_data = self.request.recv(2048)
            print(self.client_address)
            print("--- received data ---")
            print(received_data)
            print("--- end of data ---\n\n")

            initialRequest = Request(received_data)
            if 'websocket' in initialRequest.path:
                response, username = doHandshake(initialRequest)
                websocketConnections[self] = username
                socket = runSocket(response, username, self, websocketConnections)
                websocketConnections.pop(socket)
                print(username + ' should have been disconnected')
            else:
                intialLength = len(initialRequest.body)
                totalLength = initialRequest.headers.get('Content-Length', 0)
            
                buffer = received_data

                if int(totalLength) > intialLength:
                    while True:
                        header_body = buffer.split(b"\r\n\r\n", 1)
                        if int(totalLength) == len(header_body[1]):
                            break
                        else:
                            incomingData = self.request.recv(2048)
                            buffer+=incomingData
                    request = Request(buffer)
                    response = router.route_request(request)
                else:
                    response = router.route_request(initialRequest)

                # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
                self.request.sendall(response)
                
            
                 

def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    connections = []
    # Implement threading here when adding websocket connections
    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    connections.append(server)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
    
