from flask import Flask, render_template
from sqlite3 import connect, Error

conn = None 
try:
	conn = connect("results.db")
	cur = conn.cursor()

	cur.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, op_1 TEXT NOT NULL, op_2 TEXT NOT NULL, op_3 TEXT NOT NULL, op_4 TEXT NOT NULL, point_1 INTEGER, point_2 INTEGER, point_3 INTEGER, point_4 INTEGER);")
	cur.execute("CREATE TABLE IF NOT EXISTS result (id INTEGER PRIMARY KEY, total_point INTEGER UNIQUE, num INTEGER);")
except Error as e:
	print(e)
finally:
	if conn:
		conn.close()

app = Flask(__name__)
app.config["SECRET_KEY"] = b'\x13(\x03\xf2\xad\xc6\xf1\xf2l\xdc8\xd4\x93\x83\xde0'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'


from .user import user
app.register_blueprint(user)

from .admin import admin
app.register_blueprint(admin)

@app.route('/')
def index():
	try:
		conn = connect("results.db")
		cur = conn.cursor()

		cur.execute("SELECT num FROM result;")
		query = cur.fetchall()
		num_user = 0
		for num in query:
			num_user += num[0]
		return render_template("index.html", num_user=num_user)
	except Error as e:
		print(e)
		return "Error"
	finally:
		if conn:
			conn.close()



