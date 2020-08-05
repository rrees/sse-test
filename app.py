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

current_page = 0

subscribers = []


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
		a_subscriber = queue.Queue()
		subscribers.append(a_subscriber)
		a_subscriber.put(current_page)
		while True:
			page = a_subscriber.get()

			print(page)

			yield f"data: {json.dumps(book[page])}\n\n" 

	return flask.Response(event_stream(), mimetype="text/event-stream")

def next_page_in_sequence(current_page, direction):
	if direction == 'next':
		if current_page < len(book) - 1:
			return current_page + 1
		else:
			return 0

	if direction == 'previous':
		if current_page < 1:
			return len(book) - 1
		else:
			return current_page - 1

	return current_page

def notify_listeners(current_page):
	for subscriber in subscribers:
		subscriber.put(current_page)

@app.route('/book/pages/next')
def turn_next_page():
	global current_page
	current_page = next_page_in_sequence(current_page, 'next')
	notify_listeners(current_page)
	return flask.jsonify({"new_page": current_page})


@app.route('/book/pages/previous')
def turn_previous_page():
	global current_page
	current_page = next_page_in_sequence(current_page, 'previous')
	notify_listeners(current_page)

	return flask.jsonify({"new_page": current_page})