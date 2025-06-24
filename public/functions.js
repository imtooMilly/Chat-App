const ws = true;
let socket = null;

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('wss://' + window.location.host + '/websocket');

    // called whenever a new socket connection is opened, to send userList data to all open connections
    socket.onopen = function() {
        socket.send(JSON.stringify({'messageType': 'userJoined', 'message': 'new user'})); 
        console.log("!!!!!!!!!!!!!!query sent for userList!!!!!!!!!!!!");  
    }

    socket.onclose = function() {
        socket.send(JSON.stringify({'messageType': 'userLeft', 'message': 'user disconnected'})); 
        console.log("!!!!!!!!!!!!!!query sent for userList!!!!!!!!!!!!");  
    }

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType

        if(messageType === 'chatMessage'){
            addMessageToChat(message);
        }else if(messageType === 'forceUpdate'){
            socket.send(JSON.stringify({'messageType': 'userList', 'message': 'send the list bruh'})); 
        }else if(messageType === 'userList'){
            list = message.message
            console.log(list)
            setUserList(list);
        }else if(messageType === "directMessage"){
            addDMToChat(message)
        }else{
            // send message to WebRTC
            processMessageAsWebRTC(message, messageType);
        }
    }
}

// function login() {
//     // Hide login section
//     document.getElementById("login-section").style.display = "none";
//     document.getElementById("login-section").style.display = "none";
    
//     // Display content section
//     document.getElementById("logout-section").style.display = "block";
// }

// function logout() {
//     // Hide content section
//     document.getElementById("logout-section").style.display = "none";
    
//     // Display login section
//     document.getElementById("login-section").style.display = "block";
//     document.getElementById("register-section").style.display = "block";
// }

function deleteMessage(messageId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("DELETE", "/chat-messages/" + messageId);
    request.send();
}

function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    let messageHTML = "<br><button onclick='deleteMessage(\"" + messageId + "\")'>X</button> ";
    messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}


function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const xsrfToken = document.getElementById("xsrf_token").value;

    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws) {
        // Using WebSockets
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, "xsrf": xsrfToken}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, "xsrf": xsrfToken}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, "xsrf": xsrfToken}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, "xsrf": xsrfToken}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, "xsrf": xsrfToken}));
    } else {
        // Using AJAX
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log(this.response);
            }
        }
        const messageJSON = {"message": message, "xsrf": xsrfToken};
        request.open("POST", "/chat-messages");
        request.send(JSON.stringify(messageJSON));
    }
    chatTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-messages");
    request.send();
}

function updateDM() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearDMs();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addDMToChat(message);
            }
        }
    }
    request.open("GET", "/chat-history");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀";
    document.getElementById("chat-text-box").focus();

    updateChat();
    updateDM();

    if (ws) {
        initWS();
    } else {
        const videoElem = document.getElementsByClassName('video-chat')[0];
        videoElem.parentElement.removeChild(videoElem);
        setInterval(updateChat, 5000);
    }

    // use this line to start your video without having to click a button. Helpful for debugging
    startVideo();
}

function sendDirectMessage(username){
    const dmBox = document.getElementById('dm-message');
    const message = dmBox.value;
    dmBox.value = "";
    console.log(message)
    if(ws){
        // Using WebSockets
        socket.send(JSON.stringify({'messageType': 'directMessage','recipient': username, 'message': message}));
        console.log("dm sent!");
    }

}

// function startFT(username){
//     console.log('send webrtc');
//     if(ws){
//         // Using WebSockets
//         socket.send(JSON.stringify({'messageType': 'webRTC-offer','recipient': username, 'message': 'create webrtc connection with user'}));
//         console.log("offer sent!");
//     }
// }

function userListHTML(username) {
    console.log(username)
    let userHTML = "<br><br><button onclick='sendDirectMessage(\"" + username + "\")'>DM</button> ";
    userHTML += "<button onclick='connectWebRTC(\"" + username + "\")'>Video</button>"+ "<span><b>" + username + "</b></span> ";
    return userHTML;
}

function clearList() {
    const userList = document.getElementById("user-display");
    userList.innerHTML = "";
}

function setUserList(list) {
    clearList()
    const userList = document.getElementById("user-display");
    for(index in list) {
        user = list[index]
        userList.innerHTML += userListHTML(user);
        userList.scrollIntoView(false);
        userList.scrollTop = userList.scrollHeight - userList.clientHeight;
    }
}

function dmHTML(messageJSON) {
    console.log(messageJSON)
    const username = messageJSON.sender;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    let messageHTML = "<br><button onclick='deleteMessage(\"" + messageId + "\")'>X</button> ";
    messageHTML += "<label>(DM) <label/><span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    return messageHTML;
}

function addDMToChat(messageJSON){
    const chatMessages = document.getElementById("dm-display");
    chatMessages.innerHTML += dmHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function clearDMs() {
    const dms = document.getElementById("dm-display");
    dms.innerHTML = "";
}