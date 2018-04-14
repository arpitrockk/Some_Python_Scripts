from flask import Flask, render_template, request
from pusher import Pusher
import uuid

# create flask app
app = Flask(__name__)

# configure pusher object
pusher = Pusher(
  app_id='486993',
  key='830c47e4587252ceb505',
  secret='f59f7db4df3f2bd5164d',
  cluster='ap2',
  ssl=True
)

# index route, shows index.html view
@app.route('/')
def index():
  return render_template('index.html')

# store post
@app.route('/post', methods=['POST'])
def addPost(): 
  data = {
    'id': "post-{}".format(uuid.uuid4().hex),
    'title': request.form.get('title'),
    'status': 'active',
    'event_name': 'created'
  }
  pusher.trigger("blog", "post-added", data)
  with open("test.txt",'w') as f:
      f.write(data.get('title'))

# run Flask app in debug mode
app.run(port=5002,host='0.0.0.0')