var express = require('express');
var path = require('path');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var spawn = require('child_process').spawn;

//Serve up static assets for the user interface
app.use(express.static(path.join(__dirname, 'public')))
app.get('/', function(req, res){
  res.sendFile(__dirname + '/public/index.html');
});

//prepare the socket server & relay messages from the Walabot to the UI
io.on('connection', function(socket){
  console.log('a user connected');
  socket.on('targetData', function(data){
    socket.broadcast.emit('targetData', data);
  });
  socket.on('noTarget', function(){
    socket.broadcast.emit('noTarget');
  });
  socket.on('status', function(status){
    socket.broadcast.emit('status', status);
  });
  socket.on('disconnect', function(){
    socket.broadcast.emit('status', 'sensor disconnected');
  });
});

//run the Python code to detect Walabot signals
var walabot = spawn('python', ['../../walabot/WalabotWheelchair.py']);
walabot.on('exit', function (exitCode) {
  if(exitCode !==0){
    console.log('Walabot exited with error:', exitCode)
  }
})

//initialize the HTTP server
http.listen(3000, function(){
  console.log('listening on *:3000');
});
