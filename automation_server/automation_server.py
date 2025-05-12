from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title="Welcome")

if __name__ == "__main__":
    try:
        app.run(debug=True, use_reloader=False)  # use_reloader=False is critical!
    except (KeyboardInterrupt, SystemExit):
        None