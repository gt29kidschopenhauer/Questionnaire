from flask import Blueprint, request, render_template, session, url_for, redirect
from sqlite3 import connect, Error

user = Blueprint('user', __name__)

@user.route('/question', methods=["GET", "POST"])
def question():
	if not session.get("answered"):
		session["answered"] = 0

	conn = None

	try:
		conn = connect('results.db')
		cur = conn.cursor()

		if not session.get("total"):
			session["total"] = 0
	
		if request.method == "GET":
			cur.execute("SELECT id, name, op_1, op_2, op_3, op_4 FROM questions WHERE id = ?;", [session["answered"] + 1])
			query = cur.fetchone()
			return render_template('question.html', query=query)
		else:
			answer = request.form.get('options')
			cur.execute("SELECT op_1, op_2, op_3, op_4, point_1, point_2, point_3, point_4 FROM questions WHERE id = ?", [session["answered"] + 1])
			query = cur.fetchone()
			index = query.index(answer)
			session["total"] += query[index+4]

			cur.execute("SELECT * FROM questions;")
			query_count = len(cur.fetchall())
			if session["answered"] == query_count - 1:
				cur.execute("SELECT num FROM result WHERE total_point = ?", [session["total"]])
				query = cur.fetchall()
				if len(query) == 0:
					cur.execute("INSERT INTO result (total_point, num) VALUES(?, ?)", [session["total"], 1])
				else:
					new = query[0][0] + 1
					cur.execute("UPDATE result SET num = ? WHERE total_point = ?", [new, session["total"]])
				conn.commit()
				session["answered"] = 0
				return redirect(url_for('user.result'))
			else:
				session["answered"] += 1
				return redirect(url_for('user.question'))
	except Error as e:
		print(e)
		return "Error"
	finally:
		if conn:
			conn.close()

@user.route('/result')
def result():
	conn = None
	try:
		conn = connect('results.db')
		cur = conn.cursor()
		cur.execute('SELECT total_point, num FROM result;')
		queries = cur.fetchall()
		from .admin import boundary
		result = {}
		bounded_result = []
		for i in boundary:
			result[i] = 0
		for query in queries:
			total_point = query[0]
			for i in range(len(boundary)):
				if i != len(boundary) - 1 and total_point >= boundary[i] and total_point < boundary[i+1]:
					result[boundary[i]] += query[1]
					break
				elif i != len(boundary) - 1:
					continue
				else:
					result[boundary[i]] += query[1]
		result = list(result.items())
		result = sorted(result, key=lambda x: x[0])
		for i, j in result:
			if i == boundary[-1]:
				bounded_result.append([i, j])
			else:
				index = result.index((i, j))
				bounded_result.append([i, result[index + 1][0] - 1, j])
		return render_template('result.html', query=bounded_result)
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

@user.route('/search', methods=['POST'])
def search():
	return "SEARCH"