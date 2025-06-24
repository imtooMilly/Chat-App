from util.request import Request
from util.router import Router
from util.websockets import *
from util.database import *
import math
import random
import json


# router = Router()
# router.add_route("GET", '/chat-history', getChatHistory)

def doHandshake(request: Request):
    auth = request.cookies.get("token")
    
    if auth:
        username = checkToken(auth)
    else:
        username = 'guest'

    key = request.headers.get("Sec-WebSocket-Key")
    key = compute_accept(key)
    
    response = 'HTTP/1.1 101 Switching Protocols\r\nX-Content-Type-Options: nosniff\r\n'
    connection = "Connection: Upgrade"
    upgrade = "Upgrade: websocket"
    accept = "Sec-WebSocket-Accept: " + key
    
    response = (response + connection + '\r\n' + upgrade + '\r\n' + accept + '\r\n\r\n').encode()
    return (response, username)

webrtc = {}

def runSocket(response101, username, self, connections):

    print("connections: " , connections)
    self.request.sendall(response101)
    
    buffer = b''
    totalLength = 0
    calcLength = 0
    collector = []
    complete = b''

    while True:
        print('bytes in buffer: ', len(buffer))

        
        # buffer is empty, receive normally
        received_data = self.request.recv(16)

        print(self.client_address)
        print("--- received data ---")

        # parse the inital bytes received to check if buffering is needed
        initalFrame = parse_ws_frame(received_data)
        totalLength = initalFrame.payload_length
        finbit = initalFrame.fin_bit
        payload = initalFrame.payload
        calcLength = len(payload)
        print('totalLength: ', totalLength)   
        print('calcLength: ', calcLength)
        print("payload: " , payload)
        print("payload Length: ", len(payload))
        print("--- end of data ---\n\n")
        
        # disconnect user from list of connections
        if initalFrame.opcode == 8:
            return self
            
        # received bytes is less than expected amount, buffering is needed
        if totalLength > len(payload):
            print('we need to buffer Jesse')
            buffer = received_data
                    
            while totalLength != calcLength:
                # while payload doesnt match payload length, keep receiving (buffer)
                bytes = self.request.recv(min(2048, totalLength - calcLength))
                calcLength += len(bytes)
                buffer += bytes

            # parse complete frame, get new payload, reset variables
            frame = parse_ws_frame(buffer)
            finbit = frame.fin_bit
            payload = frame.payload
            buffer = b''
            calcLength = 0
            totalLength == 0              

        if finbit == 0:
            # continuation frames, collect all the frames
            print('frames split up, LISAN AL GAIB')
            print("collection: ", collector)
            collector.append(frame)
            continue
        if finbit == 1 and len(collector) > 0:
            collector.append(frame)
            for entry in collector:
                
                print('temp: ', entry.payload_length)
                complete += entry.payload
            
            payload = complete
            # reset variables
            complete = b''
            collector = []
            print('complete: ', len(payload))
            #print('complete payload: ', payload)
        
        payload = json.loads(payload)
        type = payload.get('messageType')

        if type == 'chatMessage':
            # store chat history in database, send a response frame back to every connected user
            message = html.escape(payload['message'])
            # escape html in comments before entering them in database
            messageID = random.randint(1, 1000000000)

            responsePayload = {'messageType': 'chatMessage', 'username' : username, 'message' : message, 'id': str(messageID)}
            bytesPayload = json.dumps(responsePayload).encode('utf-8')
            postFrame(responsePayload)
            # print(bytesPayload)
            responseFrame = generate_ws_frame(bytesPayload)

            for key in connections:
                #print(key)
                 key.request.sendall(responseFrame)
        elif type == 'userList':
            # respond to this message type with a list of users and unpack in the js
            userList = []
            for socket in connections:
                if socket == self:
                    continue
                user = connections[socket]
                if user != 'guest':
                    userList.append(user)
            print('userList: ', userList)
            responsePayload = {'messageType': 'userList', 'message' : userList}
            bytesPayload = json.dumps(responsePayload).encode('utf-8')
            responseFrame = generate_ws_frame(bytesPayload)

            for key in connections:
                #print(key)
                if key == self:
                    key.request.sendall(responseFrame)
        elif type == 'directMessage':
            # only send dms to sender and receiver
            message = html.escape(payload['message'])
            messageID = random.randint(1, 1000000000)
            recipient = payload['recipient']
            sender = ''

            for key in connections:
                if key == self:
                    sender = connections[key]
                    # guest trying to send dms
                    if sender == 'guest':
                        break
                    responsePayload = {'messageType': 'directMessage', 'recipient': recipient, 'sender': sender, 'message': message, 'id': str(messageID)}
                    bytesPayload = json.dumps(responsePayload).encode('utf-8')
                    postDM(responsePayload)
                    responseFrame = generate_ws_frame(bytesPayload)
                    break
            
            # guest cant send dms, dont send to users
            if sender == 'guest':
                continue

            for key in connections:
                if connections[key] == recipient:
                    key.request.sendall(responseFrame)
                if connections[key] == sender:
                    key.request.sendall(responseFrame)
        elif type == "webRTC-offer":
            print(payload)
            recipient = payload['recipient']
            offer = payload['offer']
            responsePayload = {'messageType': 'webRTC-offer', 'offer': offer}
            bytesPayload = json.dumps(responsePayload).encode('utf-8')
            responseFrame = generate_ws_frame(bytesPayload)

            # to direct answers back to this user, store key-value {recipient: sender}
            for key in connections:
                if key == self:
                    webrtc[recipient] = connections[key]
            
             # pass the webrtc offer to the intended user
            for key in connections:
                if connections[key] == recipient:
                    key.request.sendall(responseFrame)
                    break
            print('webrtc: ', webrtc)

        elif type == "webRTC-answer":
            answer = payload['answer']
            responsePayload = {'messageType': 'webRTC-answer', 'answer': answer}
            bytesPayload = json.dumps(responsePayload).encode('utf-8')
            responseFrame = generate_ws_frame(bytesPayload)

            # to send answer back to correct user, access webrtc dictionary with username, value should be the person who receives the answer
            print('CURRENT WEBRTC', webrtc)
            for key in connections:
                if key == self:
                    recipient = webrtc[connections[key]]
                    webrtc[connections[key]] = recipient
                    break



            # pass the webrtc answer to the intended user
            for key in connections:
                if connections[key] == recipient:
                    key.request.sendall(responseFrame)
                    break
            print('webrtc: ', webrtc)

        elif type == 'webRTC-candidate':
            candidate = payload['candidate']
            responsePayload = {'messageType': 'webRTC-candidate', 'candidate': candidate}
            bytesPayload = json.dumps(responsePayload).encode('utf-8')
            responseFrame = generate_ws_frame(bytesPayload)
            print('webrtc: ', webrtc)
            print(payload)

            # grab the recipient from the dictionary
            for key in connections:
                if key == self:
                    recipient = connections[key]
                    break
            # pass the webrtc candidate to the intended user
            for key in connections:
                if connections[key] == recipient:
                    key.request.sendall(responseFrame)
                    break
        else:
            responsePayload = {'messageType': 'forceUpdate', 'message': 'inquire update'}
            bytesPayload = json.dumps(responsePayload).encode('utf-8')
            responseFrame = generate_ws_frame(bytesPayload)
            for key in connections:
                #print(key)
                key.request.sendall(responseFrame)
