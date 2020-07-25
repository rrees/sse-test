import random
import threading

import flask

app = flask.Flask(__name__)

messages = []

@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/stream')
def stream():
	def event_stream():
		previous_message = 0
		while True:
			if len(messages) > previous_message:
				previous_message = len(messages)
				yield f"data: New message {messages[-1]}\n\n" 

	return flask.Response(event_stream(), mimetype="text/event-stream")

WAIT_SECONDS=5

def create_messages():
	print("Checking to see if I should create a message")
	if random.choice((True, False)):
		messages.append(str(random.randint(1,20)))
	threading.Timer(WAIT_SECONDS, create_messages).start()

create_messages()