var moment = moment();
var socket = io();
const chatMessages = document.querySelector('.messages');
const messageField = document.getElementById('message');
const send = document.getElementById('send');
const sender = document.querySelector('.id').innerHTML
const receiver = document.querySelector('.receiver').innerHTML


let room = [sender, receiver];
room.sort();
let roomCode = room.toString()
chatMessages.scrollTop = chatMessages.scrollHeight;


function outputMessage(message) {
    const div = document.createElement('div');
    if (message.sender === sender) {
        div.classList.add('message-sent');
    }
    else {
        div.classList.add('message-received')
    }
    const addTime = document.createElement('div');
    addTime.innerText = message.time;
    const p = document.createElement('p')
    p.classList.add('message-body')
    p.innerText = `${message.sender_username}: ${message.message}`;
    div.append(addTime);
    div.appendChild(p);
    document.querySelector('.messages').appendChild(div)
}

socket.on('connect', () => {
    socket.emit('connectUser', {
        id: sender,
        room: roomCode,
    })
    console.log(`${sender} has connected.`)
})

messageField.addEventListener('keypress', (e) => {
    messageField.value.trim()
    if (e.which === 13) {
        if (messageField.value.length !== 0) {
            socket.emit('chat', {
                time: moment.format("h:mm a"),
                message: messageField.value,
                sender: sender,
                receiver: receiver,
                room: roomCode
            });
            messageField.value = "";
            messageField.focus();
        }
        else {
            console.log('Type something!')
        }
    }
})

send.addEventListener('click', () => {
    messageField.value.trim()
    if (messageField.value.length !== 0) {
        socket.emit('chat', {
            time: moment.format("h:mm a"),
            message: messageField.value,
            sender: sender,
            receiver: receiver,
            room: roomCode
        });
        messageField.value = "";
        messageField.focus();
    }
    else {
        console.log('Type something!')
    }
})

socket.on('message', (message) => {
    outputMessage(message)
    chatMessages.scrollTop = chatMessages.scrollHeight;
})
