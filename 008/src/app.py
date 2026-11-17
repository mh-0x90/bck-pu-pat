
from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def process_input(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "verify.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url.encode())
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Ready when you are.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'MSG':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! Unexpected result: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

@app.route('/page21')
def page21():
    msg = request.args.get('name','')
    blacklist = ['script', "onload", "onmouseover", "onclick", "onbegin", "onerror", "svg", "'", '"', "<", ">"]
    value =  "" if msg == "" else '> {0}'.format(msg)

    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Invalid input contains: '%s'</div>""" % word
            value = ">"
            return PAGE_CONTENT.format("21","Star",value,"",error_msg)

    data = PAGE_CONTENT.format("21","Star",value, "","")
    result = process_input(data,flags[0],msg,'challenge_medium')

    response = make_response(PAGE_CONTENT.format("21","Star",value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)
