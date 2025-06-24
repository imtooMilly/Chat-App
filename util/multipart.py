from util.request import Request

class Multipart:
    def __init__(self, request):
        self.parts = []
        self.boundary = ''
        
        body = request.body


        # gets the boundary of the request
        type = request.headers.get("Content-Type")
        parts = type.split(';')
        if len(parts) > 1:
            label, boundary = parts[1].split('=')
            self.boundary = self.boundary + boundary
        
        skip = b'--' + boundary.encode()
        skip = len(skip)
        body = body[skip:]

        # breaks the multipart request into different parts
        parts = []
        parts = body.split(b'\r\n' + b'--' + self.boundary.encode())
        # remove blank spaces in parts if necessary
        if b'' in parts:
            while b'' in parts:
                parts.remove(b'')
        if b'--' in parts:
            while b'--' in parts:
                parts.remove(b'--')
        if b'--\r\n' in parts:
            while b'--\r\n' in parts:
                parts.remove(b'--\r\n')

        # use part class here to break parts up even more
        for part in parts:
            powerUP = Part(part)
            self.parts.append(powerUP)



        # index = request.find[:index]
        # headers = request[:index]
    
class Part:
    def __init__(self, part):
        self.headers = {}
        self.name = ''
        self.content = b''

        split = part.split(b'\r\n\r\n', 1)
        if len(split) > 0:
            headers = split[0].split(b'\r\n')
        else:
            return
        # remove blank entries in headers
        if b'' in headers:
            while b'' in headers:
                headers.remove(b'')

        for header in headers:
            if b':' in header:
                key, value = header.split(b':')
                self.headers[key.decode().strip()] = value.decode().strip()

        dispo = self.headers.get("Content-Disposition")
        if dispo is not None:
            for element in dispo.split(';'):
                if 'name' in element and '=' in element:
                    key, value = element.split('=')
                    self.name = value.strip('""').strip()
                    break
        if len(split) > 1:
            self.content+= split[1]

def parse_multipart(request: Request):
    #TODO This method returns an object containing the following fields
    # boundary 
    # parts, each part must have headers, name from content disposition header, and content
    multipart = Multipart(request)
    
    
    return multipart

def test1():
    test =  b'POST /media-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 685\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost:8080\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryhlJ59Rg5Jja7C70n\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: visits=8\r\ndnt: 1\r\nsec-gpc: 1\r\n\r\n------WebKitFormBoundaryhlJ59Rg5Jja7C70n\r\nContent-Disposition: form-data; name="upload"; filename="elephant-small.jpg"\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff\xe1\x00\x16Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xdb\x00\x84\x00\x10\x10\x10\x10\x11\x10\x12\x14\x14\x12\x19\x1b\x18\x1b\x19%"\x1f\x1f"%8(+(+(8U5>55>5UK[JEJ[K\x87j^^j\x87\x9c\x83|\x83\x9c\xbd\xa9\xa9\xbd\xee\xe2\xee\xff\xff\xff\x01\x10\x10\x10\x10\x11\x10\x12\x14\x14\x12\x19\x1b\x18\x1b\x19%"\x1f\x1f"%8(+(+(8U5>55>5UK[JEJ[K\x87j^^j\x87\x9c\x83|\x83\x9c\xbd\xa9\xa9\xbd\xee\xe2\xee\xff\xff\xff\xff\xc2\x00\x11\x08\x00\x18\x00\x18\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x16\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x04\x05\xff\xda\x00\x08\x01\x01\x00\x00\x00\x00\xd4\x8e\x9ds\x85\x0b\x8f\x90\x7f\xff\xc4\x00\x15\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\xff\xda\x00\x08\x01\x02\x10\x00\x00\x00\x95?\xff\xc4\x00\x15\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\xff\xda\x00\x08\x01\x03\x10\x00\x00\x00\xa9?\xff\xc4\x00&\x10\x00\x02\x01\x02\x05\x02\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x03\x04\x00\x12\x01\x05\x10\x13B"2\x14!$3\x82\x92\xa2\xff\xda\x00\x08\x01\x01\x00\x01?\x00\xccf\xcc\xdf \xbc\xd0\x03\xdbo*<\xd5\xe3\x16\xfc^^]7V\\\xf7o\xab\x055\xac\x12\xee\xbb\xf5Y\xc4_\x13\t\xb6{\x807\r \x9e\xf1\x08\xf8r=\xbf\xb5C\x84\x98J\xb1\x7f"\xc7HHh\xce\x83\xb9\x10\xd5\xea\xc8\x88\xad\xe3\xd3n\x9f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \xff\xda\x00\x08\x01\x02\x01\x01?\x00\x1f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \xff\xda\x00\x08\x01\x03\x01\x01?\x00\x1f\xff\xd9\r\n------WebKitFormBoundaryhlJ59Rg5Jja7C70n--\r\n'
    request = Request(test)
    parsedRequest = parse_multipart(request)
    assert parsedRequest.boundary == "----WebKitFormBoundaryhlJ59Rg5Jja7C70n"
    assert len(parsedRequest.parts) == 1

def test2():
    request = Request(b'POST /media-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 1350009\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost:8080\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryQnEHVxamsIQVCTBB\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: visits=30\r\ndnt: 1\r\nsec-gpc: 1\r\n\r\n------WebKitFormBoundaryQnEHVxamsIQVCTBB\r\nContent-Disposition: form-data; name="upload"; filename="blink.gif"\r\nContent-Type: image/gif\r\n\r\nGIF89a\xc3\x00\xe5\x00\xf7\x00\x00\x0e\x16\x12\x13\x12\x0c\x19\x19\x17\x16\x19)\x18&\x1a\x16+1!\x1d\x1d \x0e*#\x1e"*\x1b60\x1e6#!\x1e(%\'**2!7)%482*,2-330/738\x13/L\r1o"*D%9D&<Q8)A;9D5?R&:q\x1e@;#B9\x19EP\x15Pn\x1cbx-NQ0Wj;dZ3fmW\x1b\x1bG,4K4+F8:[  Z6+T<9k85D<FB<QT<E`?Dw=BN@=XB<iE:sJ=wQ>ICIJHTKPNFWYXFGUKUYRYHLbDCzIVgGYsWLcTKzYVfWZuJiUPmreJFgLTkQKgUWuKEwMQyUHwXTbMafYee]tvZcs^snrRhdiggydyeftxvciwivtufvtz\x15:\x83\'<\x86\x16O\x86\x1dc\x86,O\x8f,o\x8cOW\x83Rr\x8aeY\x80pr\x8eo~\xa0w\x83<Y\x81xs\x85Ql\x84nM\x83\x89o\x86\x8ev\x84\xa4\x80>=\x8f>H\x82H=\x86GF\x8dFQ\x84YK\x86[T\x96GL\x98IT\x96WL\x96ZU\x85\\c\x99[`\x89cL\x89dW\x8dp]\x90iO\x94gY\x97rZ\x8age\x85ju\x87ue\x86tz\x97je\x97lt\x99th\x9aut\xa2SX\xacZg\xa4h\\\xa6p_\xb0i^\xa5kf\xa7lr\xa8ti\xa9xu\xb5ji\xb9iu\xb6wl\xb9{u\xc2jy\xc1zn\xc3{w\xd3|z\x85k\x88\x86x\x88\x85y\x96\x95o\x81\x99y\x85\x94}\x93\x83}\xa0\xa9|\x83\xa3|\x92\xb8{\x82\xc9x\x86\x85\x8fN\x8e\x8eo\xa1\x81k\xaa\x81{\xbb\x80n\xbb\x81y\xc3\x80o\xc6\x84z\xce\x90~\xd4\x87}\xd1\x90~\x87\x84\x8a\x8a\x85\x95\x80\x91\x82\x8c\x91\x94\x95\x84\x8b\x95\x86\x99\x92\x94\x9b\x85\x84\xa5\x8b\x8c\xb0\x8a\x90\xaf\x89\x91\xb1\x99\x8a\xa4\x97\x8d\xb2\x9b\x94\xa5\x97\x94\xb7\xa9\x82\x87\xa8\x87\x95\xa8\x91\x9b\xb8\x85\x85\xb9\x89\x93\xbe\x90\x8c\xba\x91\x96\xa4\x88\xa7\xa9\x8e\xb1\xa5\x97\xa9\xa9\x99\xb6\xb1\x8c\xa5\xb9\x98\xa5\xb1\x9b\xb9\xa5\xa1\xad\xab\xa2\xb5\xba\xa1\xab\xb4\xa5\xb9\xaf\x9a\xc2\xb7\x9a\xc5\xb9\xa6\xc4\xbc\xb1\xc6\xc9\x88\x84\xc8\x8b\x93\xc8\x91\x8a\xc8\x94\x93\xd6\x8b\x85\xd6\x88\x95\xd8\x92\x88\xd8\x97\x94\xc9\x8e\xa1\xc8\x95\xa5\xd6\x9a\xa7\xd9\xa1\x9d\xc6\xa2\xac\xc2\xa6\xb3\xdb\xa3\xa3\xe2\x89\x86\xe2\x8b\x96\xe4\x96\x8b\xe7\x9a\x94\xf0\x9e\x96\xe3\x91\xa1\xea\xa0\x8e\xe9\xa1\x99\xf2\xa3\x9a\xe6\xa5\xa2\xe1\xa3\xb1\xf7\xaa\xa6\xfb\xad\xb1\xfd\xb0\xad\xfe\xb2\xb4\xc0\x9f\xc8\xc0\xa7\xc9\xc3\xb4\xca\xc3\xb5\xd0\xff\xbb\xc4\xd7\xc3\xde\xf6\xc6\xca\xec\xd9\xf6\xf6\xda\xe3\x00\x00\x00!\xf9\x04\x00\x03\x00\x00\x00!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00,\x00\x00\x00\x00\xc3\x00\xe5\x00\x00\x08\xfe\x00\x03\x08\x1cHP\x80A\x83\x06\x12.`\xc0\x90\x01\x84\x87\x10#Lx\xd8\xd0!\xc4\x8b\x13R\xf0X\x92\x84\x07\x8b\x14\x1ai\x80D\xc1\xa2\x86I\x93OR6Ir\xd2d\x93\x96-\x9b<\x81\xf2\xe7\xcf\x93\x16,\x9a\x10Z\x84\x08\n\x94;\x84\x08\xfdAD\xb4fMAH\x91\x1a\xfds\xe7\x8e\x1d\xa7v\xa2>=\x8at\x90\xd5\xa4\x82\xfcH\xb5\xa35\xaa\x9f\xaf`\xc3\x8a\xfd*h\x90\xa2I\x8a\xd2\xa6\x1d\x04\xa8\xad!\xb5\x84\xac\xf8\xfc\x03%\xa5\xdd\'\x04\xf3\x068\x880aE\x86\x17/\xfe\r\x0cQ#G\x1a<x\x80LA\x83\xc5\xc7\x92&\x93\xa8d\x99$I')
    parsedRequest = parse_multipart(request)
    assert parsedRequest.boundary == "----WebKitFormBoundarycriD3u6M0UuPR1ia"
    assert len(parsedRequest.parts) == 2
    
if __name__ == "__main__":
    test1()