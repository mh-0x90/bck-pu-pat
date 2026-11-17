
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

def check_submission(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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


@app.route('/page23')
def page23():
    msg = request.args.get('name','')
    filter_pattern = r'<(?!style\b[^>]*(?:type="text/css"|type=\'text/css\'))[^>]+>'
    msg = re.sub(filter_pattern, '', msg, flags=re.IGNORECASE | re.DOTALL)
    value =  "" if msg == "" else '{0}'.format(msg)

    data = PAGE_CONTENT_TAG.format("23", "Star", value, "", "")
    result = check_submission(data,flags[0],msg,'page_medium')
    return PAGE_CONTENT_TAG.format("23", "Star", value, result, "")

if __name__ == '__main__':
    app.run(debug=True)
