from flask import Flask, render_template, session, redirect, request
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.secret_key = "ghjk;']'[569GHJ%^[;lasdhujkseglf7^%^bhtrjkg';&((*%^*&#$ghkdfguygsed" \
                 "F&*TG#$fjhSDJKF3487034[DW}_*$+HBDIUy894y389yUASDGfiwo9A(P{34(*SADtf#Wjg)"

DB_NAME = "dictionary.db"


def create_connection(db_file):
    """create a connection to the sqlite db - maori.db"""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None


def fetch_categories():
    con = create_connection(DB_NAME)
    query = "SELECT id, category_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    categories = cur.fetchall()
    con.close()
    return categories


@app.route('/')
def render_homepage():
    print("loading home page")
    return render_template('home.html', logged_in=is_logged_in(), categories=fetch_categories())


@app.route('/categories/<cat_id>')
def render_categorypage(cat_id):
    con = create_connection(DB_NAME)
    query = "SELECT id, maori, english, definition, levels, images FROM words WHERE category=?" \
            "ORDER BY maori ASC"
    cur = con.cursor()
    cur.execute(query, (int(cat_id),))
    definition = cur.fetchall()
    print(definition)
    con.close()
    return render_template('words.html', definitions=definition, logged_in=is_logged_in(),
                           categories=fetch_categories())


@app.route('/word/<word_id>')
def render_detailpage(word_id):
    con = create_connection(DB_NAME)
    query = "SELECT maori, english, definition, levels, image FROM words WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (word_id,))
    definition = cur.fetchall()[0]
    con.close()
    return render_template('detail.html', definitions=definition, logged_in=is_logged_in(),
                           categories=fetch_categories())


@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if is_logged_in():
        return redirect('/')
    print(request.form)
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM customers WHERE email = ?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        # if given the email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty resultset
        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        session['cart'] = []
        print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)

        query = "INSERT INTO customers (id, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # You need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))  # this line actually executes the query
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+is+already+used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True

@app.route('/menu')
def render_menu():
    return render_template('menu.html')
if __name__ == "__main__":
    app.run(debug=True)



