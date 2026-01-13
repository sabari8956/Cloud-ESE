from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student_docs')
def student_docs():
    return render_template('student_docs.html')

@app.route('/staff_docs')
def staff_docs():
    return render_template('staff_docs.html')

if __name__ == '__main__':
    app.run(debug=True)
