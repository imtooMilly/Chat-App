import hashlib #SHA1 hash
import base64 #base64 encoding
import struct
import json
from util.request import Request

def unmask_payload(payload: bytes, masking_key: bytes) -> bytes:
    unmasked_payload = bytearray(len(payload))
    # mask_length = len(masking_key)
    for i in range(len(payload)):
        # Apply the mask to each byte of the payload
        unmasked_payload[i] = payload[i] ^ masking_key[i % 4]
    return bytes(unmasked_payload)

class WebsocketFrame:
    def __init__(self, socketBytes):
        self.fin_bit = 0
        self.opcode = 0
        self.payload_length = 0
        self.payload = b''
        
        n = len(socketBytes)
        # greater126 will be true if payload length is greater than 126 and less than 65536 bytes
        greater126 = False
        greater65536 = False

        # get the current 8 bits
        currentBytes = socketBytes[0]

        # handles finbit and opcode
        finMask = 0b10000000
        finBit = currentBytes & finMask
        self.fin_bit = finBit >> 7  # Shift the resulting bit to the rightmost position

        opMask = 0b000001111
        opcode = currentBytes & opMask
        self.opcode = opcode

        currentBytes = socketBytes[1]

        # handles mask and payload length
        maskMask = 0b10000000
        mask = currentBytes & maskMask
        mask = mask >> 7

        lengthMask = 0b01111111
        payloadLength = currentBytes & lengthMask
        if payloadLength == 127:
            greater65536 = True
        elif payloadLength == 126:
            greater126 =  True
        else:
            self.payload_length = payloadLength
        
        if greater65536 == True:
            currentBytes = bytes([socketBytes[2],socketBytes[3],socketBytes[4],socketBytes[5],socketBytes[6],socketBytes[7],socketBytes[8],socketBytes[9]])
            payloadLength = int.from_bytes(currentBytes, 'big')
            # handles 64 bit payload length
            # lengthMask = 0b1111111111111111111111111111111111111111111111111111111111111111
            # payloadLength = currentBytes & lengthMask
            self.payload_length = payloadLength

            if mask == 1:
                maskList = list([socketBytes[10], socketBytes[11], socketBytes[12], socketBytes[13]])

                self.payload = unmask_payload(socketBytes[14:len(socketBytes)], maskList)
    
            else:
                self.payload = socketBytes[10:len(socketBytes)]

        elif greater126 == True:
            currentBytes = bytes([socketBytes[2], socketBytes[3]])
            payloadLength = int.from_bytes(currentBytes, 'big')
            
            # handles 16 bit payload length
            # lengthMask = 0b1111111111111111
            # payloadLength = currentBytes & lengthMask
            self.payload_length = payloadLength

            if mask == 1:
                # mask = socketBytes[4:7]
                maskList = list([socketBytes[4], socketBytes[5], socketBytes[6], socketBytes[7]])

                self.payload = unmask_payload(socketBytes[8:len(socketBytes)], maskList)
            else:
                self.payload = socketBytes[4:len(socketBytes)]
        else:
            if mask == 1:
                maskList = list([socketBytes[2], socketBytes[3], socketBytes[4], socketBytes[5]])
        
                self.payload = unmask_payload(socketBytes[6:len(socketBytes)], maskList)
            else:
                self.payload = socketBytes[2:len(socketBytes)]

        

        
    
def compute_accept(websocketKey: str) -> str:
    guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    accept = websocketKey + guid
    # compute SHA1 hash of accept
    hasher = hashlib.sha1()
    hasher.update(accept.encode())
    hashedAccept = hasher.digest()

    # compute base64 encode of the hashedAccept
    encodedAccept = base64.b64encode(hashedAccept)
    stringAccept = encodedAccept.decode()

    return stringAccept

def parse_ws_frame(websocketBytes: bytes) -> WebsocketFrame:
    # parse through the bytes of the websocket Frame
    frame = WebsocketFrame(websocketBytes)
    return frame

def generate_ws_frame(payload: bytes) -> bytes:
    # Use finbit of 1, an opcode of bx0001 for text, and no mask!
    # Use input bytes for the payload
    # rsv1, rsv2, rsv3 assumed to be 0 
    finbit = 0b10000000
    opcode = 0b0001
    firstByte = finbit | opcode # use or on the finbit and opcode to get 0b10000001
    
    mask = 0b00000000
    length = len(payload)

    if length < 126:
        scndByte = mask | length
        #scndByte = length.to_bytes(1, 'big')
        frameBytes = bytes([firstByte, scndByte]) + payload
    elif length >= 126 and length < 65536:
        totalLen = len(payload)
        semiLen = 0b01111110 # 126
        totalLen = totalLen.to_bytes(2, 'big')
        frameBytes = bytes([firstByte, semiLen]) + totalLen + payload
    else:
        totalLen = len(payload)
        semiLen = 0b01111111 # 127
        totalLen = totalLen.to_bytes(8, 'big')
        frameBytes = bytes([firstByte, semiLen]) + totalLen + payload
    return frameBytes


# # Test 1 tests compute_accept function
# def test1():
#     frameBytes = b''

#     key = 'NiaTu05gdvLD/Dm6RGTy3Q=='
#     accept = compute_accept(key)
#     # get the rest of this testcase from Jesse's lecture video
#     expected = 'Ygra1uVdEjHM3MSn0EJ3g1pYNzg='
#     assert accept == expected

def test2():
    frameBytes = b'\x81\xba/\xea\xd2\xd8T\xc8\xbf\xbd\\\x99\xb3\xbfJ\xbe\xab\xa8J\xc8\xe8\xfaL\x82\xb3\xacb\x8f\xa1\xabN\x8d\xb7\xfa\x03\xc8\xbf\xbd\\\x99\xb3\xbfJ\xc8\xe8\xfaG\x83\xf0\xf4\r\x92\xa1\xaaI\xc8\xe8\xfaA\x85\xbc\xbd\r\x97'
    calculatedFrame = parse_ws_frame(frameBytes)
    expectedPayload = b'{"messageType":"chatMessage","message":"hi","xsrf":"none"}'
    print(calculatedFrame)
    expectedLength = 58
    expectedFin = 1
    #assert calculatedFrame.payload == expectedPayload
    assert expectedLength == calculatedFrame.payload_length
    assert expectedFin == calculatedFrame.fin_bit

# def test3():
#     payload = b'{"messageType": "chatMessage", "message": "hi"}'
#     frameBytes = generate_ws_frame(payload)
#     print(frameBytes)
#     frame = parse_ws_frame(frameBytes)
#     assert frame.fin_bit == 1
#     assert frame.opcode == 1
#     assert frame.payload_length == 47

# def test4():
#     frameBytes = b'\x81/{"messageType": "chatMessage", "message": "hi"}'
#     frame = parse_ws_frame(frameBytes)
#     assert frame.payload_length == 47
#     assert frame.opcode == 1
#     assert frame.fin_bit == 1

# def test5():
#     frameBytes = b'\x81\xfe\x01\t\x1f\xb7\xb3#d\x95\xdeFl\xc4\xd2Dz\xe3\xcaSz\x95\x89\x01|\xdf\xd2WR\xd2\xc0P~\xd0\xd6\x013\x95\xdeFl\xc4\xd2Dz\x95\x89\x01z\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\xdf\xd6Os\xd8\xdbFs\xdb\xdcKz\xdb\xdfLw\xd2\xdfOp\x95\x9f\x01g\xc4\xc1E=\x8d\x91Mp\xd9\xd6\x01b' 
#     calculatedFrame = parse_ws_frame(frameBytes)
#     print(len(calculatedFrame.payload))
#     print(calculatedFrame.payload)

def test6():
    payload = {"messageType": "chatMessage", "message": "hi"}
    payload = json.dumps(payload).encode()
    frame = generate_ws_frame(payload)
    print(frame)


if __name__ == "__main__":
    test6()