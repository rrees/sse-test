import json
import queue
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

#create_messages()

event_queue = queue.Queue()

book = (
	{
		"page_number": 1,
		"page_text": 'The beginning'
	},
	{
		"page_number": 2,
		"page_text": 'The middle'
	},
	{
		"page_number": 3,
		"page_text": 'The end'
	},
)

@app.route('/book')
def display_book():
	return flask.render_template('book.html')


@app.route('/book/stream')
def book_stream():

	def event_stream():
		global next_page
		current_page = -1
		event_queue.put('next')
		while True:
			event = event_queue.get()
			print(event)
			if event == 'next':
				if current_page < len(book) - 1:
					current_page = current_page + 1
				else:
					current_page = 0

			if event == 'previous':
				if current_page < 1:
					current_page = len(book) - 1
				else:
					current_page = current_page - 1

			yield f"data: {json.dumps(book[current_page])}\n\n" 

	return flask.Response(event_stream(), mimetype="text/event-stream")

@app.route('/book/pages/next')
def turn_next_page():
	event_queue.put('next')

	return flask.jsonify({})


@app.route('/book/pages/previous')
def turn_previous_page():
	event_queue.put('previous')

	return flask.jsonify({})