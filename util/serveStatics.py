from util.request import Request
from util.database import *

def send404():
    message = b'The path you request does not exist, you not loading anything bruh, try again'
    response = 'HTTP/1.1 404 PAGE NOT FOUND\r\nX-Content-Type-Options: nosniff\r\n' 
    contentType = 'Content-Type: text/plain'
    contentLen = 'Content-Length: ' + str(len(message))
    response  = (response + contentType + '\r\n' + contentLen + '\r\n\r\n').encode() + message
    return response

def serve_js(request: Request):
    #TODO : Read js files and serve response
    path = request.path
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'

    if 'functions' in path:
        with open('./public/functions.js', 'rb') as f:
            content = f.read()
            contentLen = 'Content-Length: ' + str(len(content))
            contentType = 'Content-Type: text/javascript; charset=utf-8'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + content
    elif 'webrtc' in path:
         with open('./public/webrtc.js', 'rb') as f:
            content = f.read()
            contentLen = 'Content-Length: ' + str(len(content))
            contentType = 'Content-Type: text/javascript; charset=utf-8'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + content
    else:
         with open('./public/authenticate.js', 'rb') as f:
            content = f.read()
            contentLen = 'Content-Length: ' + str(len(content))
            contentType = 'Content-Type: text/javascript; charset=utf-8'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + content
    return response

def serve_html(request: Request):
    #TODO : Read html files and serve response

    # genereate XSRF token on page load
    authToken = request.cookies.get("token", None)
    if authToken != None:
        xsrf = generateXSRF(authToken)
    else:
         xsrf = 'none'

    counterAge = 3600
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    # check the cookie dictionary if visits exits, if it doesnt, create it
    visitsCookie = request.cookies.get("visits", 1)
    if visitsCookie != 0:
        visitsCookie = int(visitsCookie)+1
    with open('./public/index.html', 'rb') as f:
        # changes the visits on the page to the value stored in visits cookie
        content = f.read()
        content = content.decode().replace('{{visits}}', str(visitsCookie)).replace('{{ xsrf }}', xsrf)
        content = content.encode()
        contentLen = 'Content-Length: ' + str(len(content))
        contentType = 'Content-Type: text/html; charset=utf-8'
        cookie = 'Set-Cookie: ' + 'visits=' + str(visitsCookie) +'; Max-Age=' + str(counterAge)
        response = (response + contentLen + '\r\n' + contentType + '\r\n' + cookie + '\r\n\r\n').encode() + content
    return response

def serve_css(request: Request):
    #TODO : Read css files and serve response
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    with open('./public/style.css', 'rb') as f:
                content = f.read()
                contentLen = 'Content-Length: ' + str(len(content))
                contentType = 'Content-Type: text/css; charset=utf-8'
                response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + content
    return response

def serveMedia(request: Request):
    #TODO : Read image files and serve response
    proto = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    path = request.path
    securePath = ''
    print(path)
    pathParts = request.path.split("/", 3)
    imageName = pathParts[-1]
    print(imageName)
    secureName = imageName.replace("/", "")
    pathParts[-1] = secureName
    for part in pathParts:
         securePath+=part
         if part != secureName:
              securePath+= '/'
    print(securePath)

    try:
        responseBody = open("." + securePath, "rb").read()
    except:
        response = send404()
        return response

    if path.endswith(".jpg"):
        contentLen = 'Content-Length: ' + str(len(responseBody))
        contentType = 'Content-Type: image/jpg'
        response = (proto + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + responseBody
    if path.endswith(".jpeg"):
        contentLen = 'Content-Length: ' + str(len(responseBody))
        contentType = 'Content-Type: image/jpeg'
        response = (proto + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + responseBody
    if path.endswith(".png"):
        contentLen = 'Content-Length: ' + str(len(responseBody))
        contentType = 'Content-Type: image/png'
        response = (proto + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + responseBody
    if path.endswith(".gif"):
        contentLen = 'Content-Length: ' + str(len(responseBody))
        contentType = 'Content-Type: image/gif'
        response = (proto + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + responseBody
    if path.endswith(".mp4"):
        contentLen = 'Content-Length: ' + str(len(responseBody))
        contentType = 'Content-Type: video/mp4'
        response = (proto + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + responseBody
        
    return response

def serve_fav(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'

    with open('./public/favicon.ico', 'rb') as f:
            content = f.read()
            contentLen = 'Content-Length: ' + str(len(content))
            contentType = 'Content-Type: image/ico'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n' ).encode() + content
    return response

