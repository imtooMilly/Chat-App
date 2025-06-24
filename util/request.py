class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        if len(request) < 1:
            return


        # changing request from bytes to string, then strips empty spaces and splits request into lines by '\r\n'
        # Went back to process request as bytes, images can NOT be read as strings

        #request_str = request.decode()
        #split_request = request_str.strip().split('\r\n')
        header_body = request.split(b'\r\n\r\n', 1)
        if len(header_body) > 0:
            headers = header_body[0].strip().split(b'\r\n')
        else:
            return

        # if empty string exists in the list, that means there is a value for the body, range is all values in between 0 and last list element
        # set the end of the range and populate the body
        #body = request_str.strip().split(b'\r\n')
        if len(header_body) > 1:
            self.body = header_body[1]
        else:
            self.body = b''

        # if b'' in split_request:

        #     while b'' in split_request:
        #         split_request.remove(b'')
            
        #     rangeEnd = len(split_request)-1
        #     body = split_request[(len(split_request)-1)]
        #     self.body = body
        #     # self.body = body.encode()
        # else:
        #     rangeEnd = len(split_request)
        #     self.body = b''

    
         #populate the variables
        method, path, version = headers[0].split(b' ')

        # self.method = method
        # self.path = path
        # self.http_version = version
        self.method = method.decode()
        self.path = path.decode()
        self.http_version = version.decode()

        rangeEnd = len(headers)
        string_request = []
        for i in range(rangeEnd):
            element = headers[i]
            string_request.append(element.decode())
        #print(string_request)

        #populate all the headers, strip values to remove leading spaces
        self.headers = {}
    
        for index in range(1, len(string_request)):
            # key, value = split_request[index].strip(' ').split(':', 1)
            key, value = string_request[index].strip(' ').split(':', 1)
            self.headers[key.strip()] = value.strip()
        
        # If cookie header exists in headers, fill the cookie jar
        self.cookies = {}
        if 'Cookie' in self.headers:
            cookie_split = self.headers["Cookie"].split(';')
            for element in cookie_split:
                cookie, value = element.strip(' ').split('=')
                self.cookies[cookie] = value

# # a simple test, testing a GET request, with no body or cookies
# def test1():
#     request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
#     assert request.method == "GET"
#     print(request.path)
#     assert "Host" in request.headers
#     assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
#     assert "Connection" in request.headers
#     assert request.body == b""  # There is no body for this request.
#     # When parsing POST requests, the body must be in bytes, not str

#     # This is the start of a simple way (ie. no external libraries) to test your code.
#     # It's recommended that you complete this test and add others, including at least one
#     # test using a POST request. Also, ensure that the types of all values are correct

# #a test, testing a GET request with an additional header, a different path, and a body
# def test2():
#     request = Request(b'GET /static_files/slides/1_2_HTTP.pdf HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nAccept-Language: en-US, en\r\n\r\nhello')
#     assert "Accept-Language" in request.headers
#     assert request.path == '/static_files/slides/1_2_HTTP.pdf'
#     assert request.body == b'hello'

# # a simple test, testing a POST request with a body
# def test3():
#     request = Request(b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\nhello world')
#     assert request.method == "POST"
#     assert request.body == b'hello world'

# # testing a POST request with a body and cookies
# def test4():
#     request = Request(b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: id=X6kAwpgW29M; visits=5; Max-Age=3600\r\n\r\nYou Finished LO1')
#     assert request.body == b'You Finished LO1'
#     assert 'id' in request.cookies
#     assert request.cookies['id'] == 'X6kAwpgW29M'
#     assert request.cookies['Max-Age'] == '3600'

# def test5():
#     request = Request(b'GET /chat-messages/1 HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nAccept-Language: en-US, en\r\n\r\nhello')
#     assert request.path == "/chat-messages/1"
#     sections = request.path.split('/')
#     numbers = 0
#     try:
#         numbers = int(sections[-1])
#     except:
#             print("path is not ended by numbers")
#     assert numbers == 1
    


# if __name__ == '__main__':
#     test1()
#     test2()
#     test3()
#     test4()
#     test5()
