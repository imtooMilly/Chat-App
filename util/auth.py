import re
from util.request import Request

def extract_credentials(request: Request) -> list:
    retList = []
    
    urlEncoded = request.body.decode()
    fields = urlEncoded.split("&")

    # find keys related to username and password
    for element in fields:
        key, value = element.split("=")
        value = value.replace('%40', '@').replace('%26', '&').replace("%21", "!").replace("%23", "#").replace("%29", ")").replace\
        ("%5E", "^").replace("%28", "(").replace("%2D", "-").replace("%24","$").replace("%5F", "_").replace("%20", "=").replace('%25', '%')
    
        if key == "username_reg" or key == "username_login":
            username = value
        if key == "password_reg" or key == "password_login":
            password = value
        
    # add username and password to list and return
    retList.append(username)
    retList.append(password)
    return retList

def validate_password(password: str) -> bool:
    # Passwords must follow this six critera:
    # 1. length must be at least 8
    # 2. Password must contain at least 1 lowercase char
    # 3. password must contain at least 1 uppercase char
    # 4. password must contain at least 1 number
    # 5. Password must contain at least 1 of the 12 special chars 
    #specialChars = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}
    # 6. password does not contain any invalid char (any char not alphanumeric or in specialchars)

    # this regex expression checks pattern for alphanumeric (upper and lower case) and special chars
    pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])+(?=.*[!@#$%^&()\-_=])+[a-zA-Z0-9!@#$%^&()\-_=]+$")

    if len(password) < 8:
        return False
    else:
        if pattern.search(password):
            return True
        else:
            return False
        
# if __name__ == "__main__":
#     valid = validate_password("Bromommnt&^3")
#     print(valid)


