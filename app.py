from flask import Flask, jsonify, render_template, request
from parser import Parser
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template('main.html')


@app.route("/parser", methods=['POST'])
def parser():
    try:
        text = request.form.get('text')
    except KeyError:
        return jsonify({'error': 'не передан параметр text'})
    response = {
        'source': text,
        'result': Parser().parse(text)
    }
    return jsonify(response)
