from util.request import Request
from util.multipart import *
from pymongo import MongoClient
import json
import html
import random
import bcrypt
import hashlib
import string
import os


mongo_client = MongoClient("mongo") #change from localhost to mongo after testing
db = mongo_client["cse312"]
chatCollection = db["chat"]
accounts = db["accounts"]
fileCollection = db["files"]
dmCollection = db['DMs']

def getChatMessage(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    path = request.path
    # check if path has an id
    notFoundResponse = b'There was nothing there bruh'
    sections = path.split('/')
    numbers = 0
    try:
        numbers = int(sections[-1])
    except:
        print("path is not ended by numbers")

    # if numbers is greater than 0 then path ends in int
    if numbers > 0:
        searchResults = list(chatCollection.find({"id": str(numbers)}, {"_id": 0}))

        # send 200 if records were found, otherwise send a 404
        if searchResults != []:
            searchResults = json.dumps(searchResults).encode()
            contentLen = 'Content-Length: ' + str(len(searchResults))
            contentType = 'Content-Type: application/json'

            response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n').encode() + searchResults
        else:
            response = 'HTTP/1.1 404 PAGE NOT FOUND\r\nX-Content-Type-Options: nosniff\r\n' 
            contentType = 'Content-Type: text/plain'
            response = (response +  contentType + '\r\n\r\n').encode() + notFoundResponse

    else:
        chatHistory = list(chatCollection.find({}, {"_id": 0}))
        chatHistory = json.dumps(chatHistory).encode()
        contentLen = 'Content-Length: ' + str(len(chatHistory))
        contentType = 'Content-Type: application/json'

        # send response back
        response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n').encode() + chatHistory
    return response

def getChatHistory(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    path = request.path

    auth = request.cookies.get('token', '')
    if auth != '':
        username = checkToken(auth)
    else:
        username = 'guest'
    
    received = list(dmCollection.find({"recipient": username}, {"_id": 0}))
    sent = list(dmCollection.find({"sender": username}, {"_id": 0}))
    chatHistory = received + sent
    chatHistory = json.dumps(chatHistory).encode()
    contentLen = 'Content-Length: ' + str(len(chatHistory))
    contentType = 'Content-Type: application/json'
    # send response back
    response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n').encode() + chatHistory
    return response


def postChatMessage(request: Request):
    # check xsrf token to make sure it matches
    body = request.body.decode()
    body = json.loads(body)

    xsrf = body['xsrf']
    auth = request.cookies.get('token', None)
    if auth != None:
        valid = checkXSRF(auth, xsrf)
        if valid:
            body = request.body.decode()
            body = json.loads(body)
            text = body["message"]
            text = html.escape(text) # html escape messages before inserting them

            # implement authenticated chat here

            username = checkToken(auth)
            messageID = random.randint(1, 1000000000)

            chatCollection.insert_one({"username": username, "id": str(messageID), "message": text})
            # send a response to say everything went OK
            # message = b'message received, as you were'
            message = {"message": text, "username": username, "id": messageID}
            message = json.dumps(message).encode()
            contentLen = 'Content-Length: ' + str(len(message))
            contentType = 'Content-Type: application/json'

            response = 'HTTP/1.1 201 Created\r\nX-Content-Type-Options: nosniff\r\n'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n').encode() + message
            return response
        else:
            response = 'HTTP/1.1 403 No Permissions\r\nX-Content-Type-Options: nosniff\r\n' 
            contentType = 'Content-Type: text/plain'
            response = (response +  contentType + '\r\n\r\n').encode() + b'you do not have permission'
            return response
                
    else:
        body = request.body.decode()
        body = json.loads(body)
        text = body["message"]
        text = html.escape(text) # html escape messages before inserting them

        # implement NON-authenticated chat here
        username = checkToken(auth)
        messageID = random.randint(1, 1000000000)

        chatCollection.insert_one({"username": username, "id": str(messageID), "message": text})
        # send a response to say everything went OK
        # message = b'message received, as you were'
        message = {"message": text, "username": username, "id": messageID}
        message = json.dumps(message).encode()
        contentLen = 'Content-Length: ' + str(len(message))
        contentType = 'Content-Type: application/json'

        response = 'HTTP/1.1 201 Created\r\nX-Content-Type-Options: nosniff\r\n'
        response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n').encode() + message
        return response

def putChatMessage(request: Request):
    path = request.path

    body = request.body.decode()
    body = json.loads(body)
    text = body["message"]

    text = html.escape(text) # html escape messages before inserting them

    sections = path.split('/')
    numbers = 0
    try:
        numbers = int(sections[-1])
    except:
        print("path is not ended by numbers")

    # if numbers is greater than 0 then path ends in int
    if numbers > 0:
        searchResults = list(chatCollection.find({"id": str(numbers)}, {"_id": 0}))

        messageID = numbers
        message = body["message"]
        username = body["username"]

        # send 200 OK if records were found and updated, otherwise send a 404
        if searchResults != []:
            chatCollection.delete_one({"id": str(numbers)})
            chatCollection.insert_one({"username": username, "id": str(messageID), "message": text})
            print("record should have been updated, I would check just in case tho")

            updatedRecord = {"message": text, "username": username, "id": messageID}
            updatedRecord = json.dumps(message).encode()
            contentLen = 'Content-Length: ' + str(len(updatedRecord))
            contentType = 'Content-Type: application/json'
            response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
            response = (response + contentLen + '\r\n' + contentType + '\r\n\r\n').encode() + updatedRecord
        else:
            response = 'HTTP/1.1 404 PAGE NOT FOUND\r\nX-Content-Type-Options: nosniff\r\n' 
            contentType = 'Content-Type: text/plain'
            response = (response +  contentType + '\r\n\r\n').encode() + b'there was nothing there bruh'
    return response


def deleteChatMessage(request: Request):

    token = request.cookies.get("token", None)

    if token != None:
        username = checkToken(token)
        print(username)
    else:
        response = 'HTTP/1.1 403 No Permissions\r\nX-Content-Type-Options: nosniff\r\n' 
        contentType = 'Content-Type: text/plain'
        response = (response +  contentType + '\r\n\r\n').encode() + b'you do not have permission'
        return response


    path = request.path
    sections = path.split('/')
    numbers = 0
    try:
        numbers = int(sections[-1])
    except:
        print("path is not ended by numbers")

    # if numbers is greater than 0 then path ends in int
    if numbers > 0:
        searchResults = list(chatCollection.find({"username": username, "id": str(numbers)}, {"_id": 0}))
        print(searchResults)

        # send 204 if records were found and deleted, otherwise send a 404
        if searchResults != []:
            chatCollection.delete_one({"username": username, "id": str(numbers)})
            print("should have been deleted take a look")
            searchResults = list(chatCollection.find({"id": str(numbers)}, {"_id": 0}))
            if searchResults == []:
                response = 'HTTP/1.1 204 No Content\r\nX-Content-Type-Options: nosniff\r\n'
                response = (response + '\r\n\r\n').encode()
            else:
                print("could not delete for some reason idk bruh")
        else:
            response = 'HTTP/1.1 403 No Permissions\r\nX-Content-Type-Options: nosniff\r\n' 
            contentType = 'Content-Type: text/plain'
            response = (response +  contentType + '\r\n\r\n').encode() + b'no perms'
    return response

def createUser(username, password):
    # generate a random ID for each user
    userID = random.randint(1, 1000000000)
    
    searchResults = list(accounts.find({"id": str(userID)}, {"_id": 0}))

    # if searchResults greater than 0, userID already in use, make a new ID (collision detection)
    if searchResults != []:
        userID = random.randint(1, 1000000000)

    # salt and hash password and add new user to database
    salt = bcrypt.gensalt()
    print(salt)
    hashNSalted = bcrypt.hashpw(password.encode(), salt)
    print(hashNSalted)

    accounts.insert_one({"username": username, "id": str(userID), "password": hashNSalted, "salt": salt, "token": "", "xsrf": ""})
    print("account should have been inserted")
    return

def validateUser(username, password):
    searchResults = list(accounts.find({"username": username}, {"_id": 0}))
    print("searchResults: ", searchResults)
    # for each matching username in search results check password for match
    for record in searchResults:
        salt = record["salt"]
        hashNsalt = bcrypt.hashpw(password.encode(), salt)
        if record["password"] == hashNsalt:
            print("account found")
            return (True, record["password"])
    return (False, "bruh")

def loginUser(username, password):
    # generate a auth token for the user now that they are logged in
    letters = string.ascii_lowercase
    # length for token can be adjusted later if more entropy needed
    token = ''.join(random.choice(letters) for i in range(20))
    token = token.encode()

    # set hashing algo
    hasher = hashlib.sha256()
    hasher.update(token)

    # hash token
    hashedToken = hasher.digest()
    
    # update token value in db for user
    query = {"username": username, "password": password}
    newvalues = { "$set": { "token": hashedToken} }
    accounts.update_one(query, newvalues)
    print("token should be generated for user")

    searchResults = list(accounts.find({"token": hashedToken}, {"_id": 0}))
    print("searchResults: ", searchResults)
    if searchResults != []:
        # set plain text token for user
        return token.decode()
    else:
        return False

def logoutUser(token):
    # TODO log user out
    # update the value of the token to empty string again
        
    # reHash token to see if it matches
    hasher = hashlib.sha256()
    hasher.update(token.encode())
    hashedToken = hasher.digest()
    searchResults = list(accounts.find({"token": hashedToken}, {"_id": 0}))
    print("searchResults: ", searchResults)

    if len(searchResults) == 1:
        record = searchResults[0]
        username = record["username"]
        password = record["password"]
        valid = True
    else:
        valid = False

    if valid:
        query = {"username": username, "password": password}
        newvalues = { "$set": { "token": ""} }
        accounts.update_one(query, newvalues)
        print("token should be deleted for user")
    else:
        print("couldn't find the user, try again")
    
    searchResults = list(accounts.find({"username": username, "password": password, "token": ""}, {"_id": 0}))
    if len(searchResults) == 1:
        print("User token updated")
        return True
    else:
        return False


    
def checkToken(token):
    if token != None:
        # reHash token to see if it matches
        hasher = hashlib.sha256()
        hasher.update(token.encode())
        hashedToken = hasher.digest()

        searchResults = list(accounts.find({"token": hashedToken}, {"_id": 0}))

        if len(searchResults) == 1:
            record = searchResults[0]
            username = record["username"]
            return username
        else:
            username = "guest"
            return username
    # if token is None, then the username is guest
    else:
        username = "guest"
        return username

def generateXSRF(authToken):
    # generate a token for the user when they request page
    letters = string.ascii_lowercase
    # length for token can be adjusted later if more entropy needed
    xToken = ''.join(random.choice(letters) for i in range(20))

    if authToken != None:
        hasher = hashlib.sha256()
        hasher.update(authToken.encode())
        hashedToken = hasher.digest()
        # update xsrf token value in db for user
        query = {"token": hashedToken,}
        newvalues = { "$set": { "xsrf": xToken} }
        accounts.update_one(query, newvalues)
    return xToken

def checkXSRF(token, xsrf):
    hasher = hashlib.sha256()
    hasher.update(token.encode())
    hashedToken = hasher.digest()

    searchResults = list(accounts.find({"token": hashedToken}, {"_id": 0}))
    print(searchResults)
    if len(searchResults) == 1:
        record = searchResults[0]
        storedXSRF = record["xsrf"]
        if storedXSRF == xsrf:
            return True
        else:
            return False
    else:
        print("couldn't verify user token")
        return False

def postMedia(request: Request):
    # construct resposne
    response =  "HTTP/1.1 302 Found\r\nX-Content-Type-Options: nosniff"
    contentLen = 'Content-Length: ' + str(0)
    loc = 'Location: ' + '/'
    response = (response + '\r\n' + contentLen + '\r\n' + loc + '\r\n\r\n').encode()
    
    # begin processing request
    images = ['.jpeg', '.png', '.gif']
    messageID = random.randint(1, 1000000000)
    auth = request.cookies.get("token", None)
    username = checkToken(auth)
    
    files = list(fileCollection.find({}, {"_id": 0}))
    fileName = 'file'
    # fileName+= '0'
    if len(files) == 0:
        fileName+= '0'
        fileCollection.insert_one({'value': 0})
    else:
        fileName+= str(len(files))
        fileCollection.insert_one({'value': len(files)})

    multipart = parse_multipart(request)
    
    for part in multipart.parts:
        signature = part.content[0:10]
        print(signature)
        if b'GIF87a' in signature or b'GIF89a' in signature:
            mediaType = '.gif'
        elif b'\xff\xd8\xff' in signature:
            mediaType = '.jpeg'
        elif b'\x89PNG\r\n\x1a\n' in signature:
            mediaType = '.png'
        else:
            #b'\x00\x00\x00 ftypis' or b'\x00\x00\x00 ftypmp' in signature:
            mediaType = '.mp4'

        contentType = part.headers.get('Content-Type', '')

        # handles image uploads
        if mediaType in images:
            mediaContent = part.content
            filePath = "./public/image/" + fileName + mediaType

            # save image to disk
            with open(filePath, 'wb') as f:
                f.write(mediaContent)

            content = '<img src="./public/image/' + fileName + mediaType + '"' + '/>'
            print('media inserted into DB')
            chatCollection.insert_one({"username": username, "id": str(messageID), "message": content})
        # handles video uploads
        else:
            mediaContent = part.content
            filePath = os.path.join('public/video/', fileName + mediaType)

            # save image to disk
            with open(filePath, 'wb') as f:
                f.write(mediaContent)

            # construct html for video
            beginning = '<video width="400" controls autoplay muted>'
            src1 = '<source src="public/video/' + fileName + mediaType + '"' + ' type="video/mp4">'
            end = '</video>'
            content = beginning + src1 + end
            # ex: <video width="400" controls autoplay muted> <source src="public/video/file0.mp4"/> </video>
            print('media inserted into DB')
            chatCollection.insert_one({"username": username, "id": str(messageID), "message": content})
    print('returning resposne')
    return response

def postFrame(payload):
    chatCollection.insert_one(payload)

def postDM(payload):
    dmCollection.insert_one(payload)

# def getDM(username):
#     received = list(dmCollection.find({"recipient": username}, {"_id": 0}))
#     sent = dmCollection.find({"sender": username}, {"_id": 0})
    
# def test2():
#     request = Request(b'POST /media-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 1350009\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost:8080\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryQnEHVxamsIQVCTBB\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: visits=30\r\ndnt: 1\r\nsec-gpc: 1\r\n\r\n------WebKitFormBoundaryQnEHVxamsIQVCTBB\r\nContent-Disposition: form-data; name="upload"; filename="blink.gif"\r\nContent-Type: image/gif\r\n\r\nGIF89a\xc3\x00\xe5\x00\xf7\x00\x00\x0e\x16\x12\x13\x12\x0c\x19\x19\x17\x16\x19)\x18&\x1a\x16+1!\x1d\x1d \x0e*#\x1e"*\x1b60\x1e6#!\x1e(%\'**2!7)%482*,2-330/738\x13/L\r1o"*D%9D&<Q8)A;9D5?R&:q\x1e@;#B9\x19EP\x15Pn\x1cbx-NQ0Wj;dZ3fmW\x1b\x1bG,4K4+F8:[  Z6+T<9k85D<FB<QT<E`?Dw=BN@=XB<iE:sJ=wQ>ICIJHTKPNFWYXFGUKUYRYHLbDCzIVgGYsWLcTKzYVfWZuJiUPmreJFgLTkQKgUWuKEwMQyUHwXTbMafYee]tvZcs^snrRhdiggydyeftxvciwivtufvtz\x15:\x83\'<\x86\x16O\x86\x1dc\x86,O\x8f,o\x8cOW\x83Rr\x8aeY\x80pr\x8eo~\xa0w\x83<Y\x81xs\x85Ql\x84nM\x83\x89o\x86\x8ev\x84\xa4\x80>=\x8f>H\x82H=\x86GF\x8dFQ\x84YK\x86[T\x96GL\x98IT\x96WL\x96ZU\x85\\c\x99[`\x89cL\x89dW\x8dp]\x90iO\x94gY\x97rZ\x8age\x85ju\x87ue\x86tz\x97je\x97lt\x99th\x9aut\xa2SX\xacZg\xa4h\\\xa6p_\xb0i^\xa5kf\xa7lr\xa8ti\xa9xu\xb5ji\xb9iu\xb6wl\xb9{u\xc2jy\xc1zn\xc3{w\xd3|z\x85k\x88\x86x\x88\x85y\x96\x95o\x81\x99y\x85\x94}\x93\x83}\xa0\xa9|\x83\xa3|\x92\xb8{\x82\xc9x\x86\x85\x8fN\x8e\x8eo\xa1\x81k\xaa\x81{\xbb\x80n\xbb\x81y\xc3\x80o\xc6\x84z\xce\x90~\xd4\x87}\xd1\x90~\x87\x84\x8a\x8a\x85\x95\x80\x91\x82\x8c\x91\x94\x95\x84\x8b\x95\x86\x99\x92\x94\x9b\x85\x84\xa5\x8b\x8c\xb0\x8a\x90\xaf\x89\x91\xb1\x99\x8a\xa4\x97\x8d\xb2\x9b\x94\xa5\x97\x94\xb7\xa9\x82\x87\xa8\x87\x95\xa8\x91\x9b\xb8\x85\x85\xb9\x89\x93\xbe\x90\x8c\xba\x91\x96\xa4\x88\xa7\xa9\x8e\xb1\xa5\x97\xa9\xa9\x99\xb6\xb1\x8c\xa5\xb9\x98\xa5\xb1\x9b\xb9\xa5\xa1\xad\xab\xa2\xb5\xba\xa1\xab\xb4\xa5\xb9\xaf\x9a\xc2\xb7\x9a\xc5\xb9\xa6\xc4\xbc\xb1\xc6\xc9\x88\x84\xc8\x8b\x93\xc8\x91\x8a\xc8\x94\x93\xd6\x8b\x85\xd6\x88\x95\xd8\x92\x88\xd8\x97\x94\xc9\x8e\xa1\xc8\x95\xa5\xd6\x9a\xa7\xd9\xa1\x9d\xc6\xa2\xac\xc2\xa6\xb3\xdb\xa3\xa3\xe2\x89\x86\xe2\x8b\x96\xe4\x96\x8b\xe7\x9a\x94\xf0\x9e\x96\xe3\x91\xa1\xea\xa0\x8e\xe9\xa1\x99\xf2\xa3\x9a\xe6\xa5\xa2\xe1\xa3\xb1\xf7\xaa\xa6\xfb\xad\xb1\xfd\xb0\xad\xfe\xb2\xb4\xc0\x9f\xc8\xc0\xa7\xc9\xc3\xb4\xca\xc3\xb5\xd0\xff\xbb\xc4\xd7\xc3\xde\xf6\xc6\xca\xec\xd9\xf6\xf6\xda\xe3\x00\x00\x00!\xf9\x04\x00\x03\x00\x00\x00!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00,\x00\x00\x00\x00\xc3\x00\xe5\x00\x00\x08\xfe\x00\x03\x08\x1cHP\x80A\x83\x06\x12.`\xc0\x90\x01\x84\x87\x10#Lx\xd8\xd0!\xc4\x8b\x13R\xf0X\x92\x84\x07\x8b\x14\x1ai\x80D\xc1\xa2\x86I\x93OR6Ir\xd2d\x93\x96-\x9b<\x81\xf2\xe7\xcf\x93\x16,\x9a\x10Z\x84\x08\n\x94;\x84\x08\xfdAD\xb4fMAH\x91\x1a\xfds\xe7\x8e\x1d\xa7v\xa2>=\x8at\x90\xd5\xa4\x82\xfcH\xb5\xa35\xaa\x9f\xaf`\xc3\x8a\xfd*h\x90\xa2I\x8a\xd2\xa6\x1d\x04\xa8\xad!\xb5\x84\xac\xf8\xfc\x03%\xa5\xdd\'\x04\xf3\x068\x880aE\x86\x17/\xfe\r\x0cQ#G\x1a<x\x80LA\x83\xc5\xc7\x92&\x93\xa8d\x99$I')
#     response = postMedia(request)
#     print(response)

# def test1():
#     request = Request(b'POST /media-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 438452\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost:8080\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryeJGBvMxRMOMvEYd5\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: visits=34\r\ndnt: 1\r\nsec-gpc: 1\r\n\r\n------WebKitFormBoundaryeJGBvMxRMOMvEYd5\r\nContent-Disposition: form-data; name="upload"; filename="blocked.png"\r\nContent-Type: image/png\r\n\r\n\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\xe8\x00\x00\x02\x8e\x08\x06\x00\x00\x00\x1cB&\x94\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00_zTXtRaw profile type APP1\x00\x00\x08\x99\xe3JO\xcdK-\xcaLV((\xcaO\xcb\xccI\xe5R\x00\x03c\x13.\x13K\x13K\xa3D\x03\x03\x03\x0b\x03\x0804006\x04\x92F@\xb69T(\xd1\x00\x05\x98\x98\x9b\xa5\x01\xa1\xb9Y\xb2\x99)\x88\xcf\x05\x00O\xba\x15h\x1b-\xd8\x8c\x00\x00 \x00IDATx\x9c\xec\xddi\x90\xe4\xf7}\xdf\xf7\xf7\xe7\xf7\xef\x9e\xee\xb9vvf/\xec\x85\x05\x08\xf0\x00A\x10"\x17X\x00$\x80%q\xf0\x92\x12\xd9N1\xa9$\xae\xf8\x89\xf2 \xaeJ*\xa9\x1c\x95\xa4\xf2\xc0r\x14\xcb\xae\xb2\xabR.;.\x99.W**W\x1c+r\x1c\x1d\x91yH\xbc\x89s\x05\x12\x94x@8\x17X\xec}\xcc=\xd3\xdd\xff\xdf\'\x0f~\xbf\x99]0\x92C\x89\xd8\x9d\xc5\xe2\xfbB-\xb1\xd3\xdd\xd3\xfd?\x9a\x0f\xf0\xa9\xef\x01!\x84\x10B\x08!\x84\x10B\x08!\x84-\xa3\xad>\x80\x10B\x08!\x84\x10B\x08!\x84P\x18\xc4an\xa2\xe1\x10p\xa0\xfc\xd1N\xcc\x0c0\x8b\x18\x03\xef\xc0\x0c\x90\x16\xb1\'1#\xc4\x00i\x1e8\x85\xfd*p\x1es\x9a\x0e\xaf\xf1$o\n\xbc\x95\xe7\x15\xfe\xcd"\xa0\x0b!\x84\x10B\x08!\x84\x10B\xd8">L\x17\xb8\x8d\x86\xdb\xc8\xdcM\xe2^2\x93\xc0\x0cb\x84X$\x93\x11\x13\x88\x0ef\x00t\xc9z\x15\x98\xa7a7\xf8 \xa6\x01\xd6\x11k\xc0\nf\'\xd2\x0b\xe0\x9b\xb1\x8ec\x1f#\xf1\x06\x99\xd7\xe8\xf0#=\xc9\xea\x16\x9ev\xf8\t\x11\xd0\x85\x10B\x08!\x84\x10B\x08!\\C\xbe\x87\x834\xdcE\xe6\x03d\x1d\xa4a\xb2>\xb5\x9d\xec\x0e\x89\t\xcc$\xc2\x98\xa6T\xcb]\x91\xe1\x88\x04\\\xa4\xd5)`\x82\xe4[0\xa7\x11\x93\x08a\xc6\x80U\xb2^!\xd1AL\xd7O\x9e \xb3\x1d1\xc0z\x0e\xf9k\x88\xef\xe8i\x16\xae\xf1%\x08?!\x02\xba\x10B\x08!\x84\x10B\x08!\x84\xab\xcc\x87\xd9I\x87#\xc0\xddX\xbb\xc8\xf41\x97h\xd8I\xf6\x81+\x02\xb8!b\x1c\xe8a\x84\x18\x00\x19\xd3\xaf\xe1[B\x9c\xa4\xd5I\x12\xe3\xc8\xfb\xcb\x07\xe8U`\x16{\x1a1*\x8f1\x02\x95\xf0-\xb1J\xcb\x14\xc9s\xf5=w\x90iI,\xd3\xeaOH\xfe"\xcb\xfc\x81~\xc0\xe0\xda^\x99\x00\x11\xd0\x85\x10B\x08!\x84\x10B\x08!\\\x15~\x8c\x19.r\x1b\x1d\x1e \xeb\xa3\x88D\xcb2\x89\x11b\x17F\x18\x91\xdc\xaf3\xe62\xd0\x01\xba\x88T\xdbY\xcf\x90\xb5F\xf2A\x8c\x91\xce ^\xa8\x9f\xf0!`\x17f\r\xd3\xd4`o\xad\xbeO\xb7\x06z\x170\x1d\xd0\xab$fhY\xa2a\x1d3\t\xdeUf\xda\xd1%\xb3B\xd2+\xe0o`\xbe\xaag8\xbf%\x17\xed]*\x02\xba\x10B\x08!\x84\x10B\x08!\x84\xb7\x89\x8f\xb0\r\xf30\xe8\xd3\xe0C%\x82\xd3y2\xc6L\x90<\x81\xe9\x03\xbd+~\xad_\xab\xdaR\r\xed\x06e\xe9\x03\xdb0\x0b\xb5\xa5u\x1c\xb3\x86t\x0e\x93\xb1\xb7#&\xea\xef7@\xae\x81\x9c\x80\x16\xa0\xce\xac\x1b!\x86%\xc0\xd3\x19\xec\xef"\xd6\x10\xa70\xdb\xb1\x0e"n!{\x1f\x89\x05\xd0R\t\xf4\xfce2_\xd21\x8e_\xcb\xeb\xf7n\x15\x01]\x08!\x84\x10B\x08!\x84\x10\xc2\xcf\xc0\x9f\xa5\xc7%ne\xc8\xfb0\x1f\xa6\xd1\x87\xc1\xfb\xea,\xb8\x15`\x15\xd3\xd4\xd9r\t\x91kp\xd6\x81:c\xee\xf2\x96\xd5\x06\xb3\n\xac\x93\xe8\x03\t\xeb\x1cx\x1c1\x89\xe9\xd4\x80\x0f\xc4*b\x8d\\\xc3\xbeR\r\'D\xae\xefc\xd8lY\x15\xd23\xc8\xdf\xc0\xf40\xa7)Uv&\xeb\xe7\xc1\x1f')
#     response = postMedia(request)
#     print(response)
    
# if __name__ == "__main__":
#     test1()