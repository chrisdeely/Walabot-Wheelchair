var express = require('express');
var path = require('path');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use(express.static(path.join(__dirname, 'public')))

app.get('/', function(req, res){
  res.sendFile(__dirname + '/public/index.html');
});

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

http.listen(3000, function(){
  console.log('listening on *:3000');
});
