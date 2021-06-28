from flask import Flask, render_template
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt


app = Flask(__name__)


bcrypt = Bcrypt(app)
app.secret_key = "ghjk;']'[569GHJ%^[;lasdhujkseglf7^%^bhtrjkg';&((*%^*&#$ghkdfguygsed" \
                 "F&*TG#$fjhSDJKF3487034[DW}_*$+HBDIUy894y389yUASDGfiwo9A(P{34(*SADtf#Wjg)"

DB_NAME = "dictionary.db"


def create_connection(db_file):
    try:
        connection = sqlite3.connection(db_file)
        return connection
    except Error as e:
        print(e)


@app.route('/')
def render_home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run()