# Walabot-Wheelchair
An application leveraging the Walabot sensor array for collision prevention for wheelchair users

## Installation
- clone the repo
- Install the [Walabot API](https://walabot.com/getting-started) for your platform
- Install the Python depencencies

```pip install -r walabot/requirements.txt```
- Install the Node dependencies
```
cd webapp/node
npm install
```
## Running
- Attach your Walabot via USB
- Start the web interface
```
node webapp/node/app.js
```
- Connect to the web UI via ```http://[host ip]:3000```

Alarm MP3 credit: https://www.freesound.org/people/coltonmanz/sounds/381382/
