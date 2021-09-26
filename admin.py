from flask import Blueprint, render_template, url_for, redirect, request, abort, flash, session
from werkzeug.security import check_password_hash
from sqlite3 import connect, Error

admin = Blueprint('admin', __name__)

boundary = [1, 5, 13, 21]

@admin.route('/login', methods=["GET", "POST"])
def login():
	if session.get("name"):
		return redirect(url_for("admin.admin_loggedin.main_admin"))
	if request.method == "GET":
		return render_template('login.html')
	else:
		username = request.form.get("username")
		password = request.form.get("password")

		conn = None

		try:
			conn = connect("admin.db")
			cur = conn.cursor()

			cur.execute("SELECT name, username, password FROM admin WHERE username = ?;", [username])
			query = cur.fetchall()

			if len(query) != 1:
				flash("Wrong admin username.")
				return render_template('login.html')
			
			password_hashed = query[0][2]
			if not check_password_hash(password_hashed, password):
				flash("Wrong password.")
				return render_template('login.html')

			session["name"] = query[0][0]
			return redirect(url_for("admin.admin_loggedin.main_admin"))
		except Error as e:
			print(e)
		finally:
			if conn:
				conn.close()

admin_loggedin = Blueprint("admin_loggedin", __name__, url_prefix="/admin_loggedin")
admin.register_blueprint(admin_loggedin)

@admin_loggedin.route("/")
def main_admin():
	if not session.get("name"):
		abort(403)
	try:
		conn = connect("results.db")
		cur = conn.cursor()

		cur.execute("SELECT num FROM result;")
		query = cur.fetchall()
		num_user = 0
		for i in query:
			num_user += i[0]

		return render_template("admin.html", code=[session["name"], num_user])
	except Error as e:
		print(e)
		return "Error"
	finally:
		if conn:
			conn.close()

@admin_loggedin.route("/add", methods=["GET", "POST"])
def add():
	if request.method == "GET":
		return render_template("add.html")
	else:
		name = request.form.get("name")
		op_1 = (request.form.get("op_1"), request.form.get("point_1"))
		op_2 = (request.form.get("op_2"), request.form.get("point_2"))
		op_3 = (request.form.get("op_3"), request.form.get("point_3"))
		op_4 = (request.form.get("op_4"), request.form.get("point_4"))

		try:
			conn = connect("results.db")
			cur = conn.cursor()
			cur.execute("INSERT INTO questions (name, op_1, op_2, op_3, op_4, point_1, point_2, point_3, point_4) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", [name, op_1[0], op_2[0], op_3[0], op_4[0], op_1[1], op_2[1], op_3[1], op_4[1]])
			conn.commit()
			return redirect(url_for("admin.admin_loggedin.add"))
		except Error as e:
			print(e)
			return "Error"
		finally:
			if conn:
				conn.close()
