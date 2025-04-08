from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/todo")
def todo():
    return render_template("todo.html")

@app.route("/timer")
def timer():
    return render_template("timer.html")

if __name__ == "__main__":
    app.run(debug=True)
