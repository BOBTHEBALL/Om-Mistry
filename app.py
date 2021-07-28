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


@app.route('/', methods=["GET", "POST"])
def render_homepage():
    if request.method == "POST" and is_logged_in():
        category_name = request.form.get('category')
        if len(category_name) < 3:
            return redirect("/?error=Name+must+be+at+least+3+letters+long.")
        else:
            # connect to the database
            con = create_connection(DB_NAME)

            query = "INSERT INTO category (id, category_name) VALUES(NULL, ?)"

            cur = con.cursor()  # You need this line next
            try:
                cur.execute(query, (category_name,))  # this line actually executes the query
            except:
                return redirect('/menu?error=Unknown+error')

            con.commit()
            con.close()

    return render_template('home.html', logged_in=is_logged_in(), categories=fetch_categories())


@app.route('/categories/<cat_id>', methods=["POST", "GET"])
def render_categorypage(cat_id):
    if request.method == "POST" and is_logged_in():
        maori = request.form['Maori Word'].strip().title()
        english = request.form['English Word'].strip().title()
        category = request.form['Word Category']
        definition = request.form['Description'].strip().title()
        levels = request.form['Difficulty Level']

        if len(english) < 1:
            return redirect("/menu?error=Wrong")
        elif len(maori) < 1:
            return redirect("/menu?error=Wrong")
        else:
            # connect to the database
            con = create_connection(DB_NAME)

            query = "INSERT INTO words (maori, english, category, definition, levels, images, id) " \
                    "VALUES(?, ?, ?, ?, ?, ?, NULL)"

            cur = con.cursor()  # You need this line next
            editor_id = session['userid']
            try:
                cur.execute(query, (
                maori, english, category, definition, levels, editor_id))  # this line actually executes the query
            except:
                return redirect('/categories/' + cat_id + '?error=Unknown+error')

            con.commit()
            con.close()


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
    query = "SELECT id, maori, english, definition, levels, images FROM words WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (word_id,))
    definition = cur.fetchall()[0]
    con.close()
    return render_template('detail.html', definition=definition, logged_in=is_logged_in(),
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
        #
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
            cur.execute(query, (fname, lname, email, hashed_password))  # this line executes the query
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
    return redirect('/?message=See+you+later!')


def is_logged_in():
    if session.get("email") is None:
        print("you are not logged in")
        return False
    else:
        print("you are logged in")
        return True


@app.route('/menu')
def render_menu():
    return render_template('menu.html')

@app.route('/delete')
def render_delete():
    return render_template('   ')

if __name__ == "__main__":
    app.run(debug=True)

