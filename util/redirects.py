from util.request import Request
from util.auth import *
from util.database import *

def serveRegister(request: Request):
    credentials = extract_credentials(request)
    username, password = credentials
    valid = validate_password(password)
    if valid:
        createUser(username, password)
    else:
        # if valid == false print message to console
        print("invalid password")
    message = b'Redirecting'
    response =  "HTTP/1.1 302 Found redirect\r\nX-Content-Type-Options: nosniff"
    contentLen = 'Content-Length: ' + str(0)
    loc = 'Location: ' + '/'
    response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n\r\n').encode() + message
    return response


def serveLogin(request: Request):
    counterAge = 3600

    credentials = extract_credentials(request)
    username, password = credentials

    valid, hashNSalt = validateUser(username, password)

    message = b'Redirecting'
    response =  "HTTP/1.1 302 Found redirect\r\nX-Content-Type-Options: nosniff"
    contentLen = 'Content-Length: ' + str(0)
    loc = 'Location: ' + '/'

    if valid:
        token = loginUser(username, hashNSalt)
        if token != False:
            print("Login successful dude :D")
            # set the token as a cookie for the user
            cookie = 'Set-Cookie: ' + 'token=' + str(token) +'; Max-Age=' + str(counterAge) + "; HttpOnly; Secure"
            response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n' + cookie + '\r\n\r\n').encode()
        else:
            print("Something happened during login process, please try again")
            response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n\r\n').encode()
        return response
    else:
        print("invalid username or password, try again")
        # message = b'Redirecting'
        response =  "HTTP/1.1 302 Found redirect\r\nX-Content-Type-Options: nosniff"
        contentLen = 'Content-Length: ' + str(0)
        loc = 'Location: ' + '/'
        response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n\r\n').encode()
    return response

def serveLogout(request: Request):
    # try to log user out
    token  = request.cookies.get("token", None)
    valid = logoutUser(token)

    # message = b'Redirecting'
    response =  "HTTP/1.1 302 Found redirect\r\nX-Content-Type-Options: nosniff"
    contentLen = 'Content-Length: ' + str(0)
    loc = 'Location: ' + '/'

    if valid:
        cookie = 'Set-Cookie: ' + 'token=' + ' ' +'; Max-Age=' + str(0)
        response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n' + cookie + '\r\n\r\n').encode()
        print("User should be logged out")
    else:
        response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n\r\n').encode()
        print("user couldn't be logged out for some reason")
    return response