import os
import itertools as it
import re
from typing import List, Union, Optional, Generator, Dict, Tuple

import flask
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IS_WINDOWS = os.name != 'posix'


def lines(path: str) -> Generator[str, None, None]:
    with open(path, 'r') as file:
        for line in file:
            yield line


def fetch_list(command: str, value: str, arr: Union[Generator[str, None, None], List[str]]) -> Union[
    Generator[str, None, None], List[str]]:
    if command == 'filter':
        return list(filter(lambda x: value in x, arr))
    elif command == 'map':
        return list(map(lambda x: x.split(' ')[int(value)], arr))
    elif command == 'unique':
        return list(set(x for x in arr))
    elif command == 'sort':
        return list(sorted(arr, key=lambda x: x, reverse=False if value == 'asc' else True))
    elif command == 'limit':
        return list(it.islice(arr, 0, int(value)))
    elif command == 'regex':
        r = re.compile(value)
        return r.findall(''.join(list(arr)))
    else:
        return list('1')


@app.route('/')
def hello_page():
    return render_template('hello.html')

@app.route("/perform_query", methods=['GET', 'POST'])
def perform_query() -> Union[flask.Response, Tuple[flask.Response, int]]:
    if request.method == 'POST':
        details: Optional[Dict[str, str]] = request.json
        if details:
            path = f"{DATA_DIR}\\{details.get('file_name', '')}" if IS_WINDOWS else f"{DATA_DIR}/{details.get('file_name', '')}"
            print(path)
            try:
                temp = fetch_list(details.get('cmd1', ""), details.get('value1', ""), lines(path))
                temp = fetch_list(details.get('cmd2', ""), details.get('value2', ""), temp)
                return jsonify(list(temp))
            except FileNotFoundError as e:
                return jsonify({"error": "invalid payload"}), 400
    # return app.response_class('', content_type="text/plain")
    return jsonify({"error": "invalid payload"}), 400
