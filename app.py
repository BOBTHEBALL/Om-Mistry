from flask import Flask, render_template, session, redirect, request, flash
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

# this is the stuff I am importing to use for the future of my project
app = Flask(__name__)

bcrypt = Bcrypt(app)
app.secret_key = "ghjk;']'[569GHJ%^[;lasdhujkseglf7^%^bhtrjkg';&((*%^*&#$ghkdfguygsed" \
                 "F&*TG#$fjhSDJKF3487034[DW}_*$+HBDIUy894y389yUASDGfiwo9A(P{34(*SADtf#Wjg)"

DB_NAME = "dictionary.db"


# This is the name of my dictionary

def intention(button):
    if button in request.form:
        return True
    else:
        return False


#

def create_connection(db_file):
    """create a connection to the sqlite db - maori.db"""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None


# This will create a connection with SQLite allowing me to use it in the future.

def fetch_categories():
    con = create_connection(DB_NAME)
    query = "SELECT id, category_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    categories = cur.fetchall()
    con.close()
    return categories


# This is fetching the categories so I can use them in my code later on


@app.route('/', methods=["GET", "POST"])
def render_homepage():
    if request.method == "POST" and is_logged_in():
        category_name = request.form.get('category')
        if len(category_name) < 3:
            return redirect("/?error=Name+must+be+at+least+3+letters+long.")
        else:
            # This code is the beginning of my home page and it will allow me to utilize different features
            con = create_connection(DB_NAME)

            query = "INSERT INTO category (id, category_name) VALUES(NULL, ?)"

            cur = con.cursor()
            try:
                cur.execute(query, (category_name,))  # This line is important as it executes the query

            except:
                flash('Category name already used, please choose a new name')  # duplicate categories cannot be used
                return redirect(request.referrer)
                return redirect('/?error=Unknown+error')

            con.commit()
            con.close()

    return render_template('home.html', logged_in=is_logged_in(), categories=fetch_categories())
    # This renders the home template which I will use to place many different important things


@app.route('/categories/<cat_id>', methods=["POST", "GET"])
# This creates a webpage and then it
def render_categorypage(cat_id):
    if request.method == "POST" and is_logged_in():
        category = request.form.get('Category')
        print(request.form)
        if request.form.get("deleting") == "True":
            con = create_connection(DB_NAME)
            cur = con.cursor()
            query = "DELETE FROM category WHERE id=?"
            cur.execute(query, (category,))
            con.commit()
            con.close()
            return redirect('/')

        print(request.form)
        # This renders the page for the different word categories and it creates a connection with database
        category = request.form.get('Category')
        maori = request.form.get('maoriword').strip().title()
        english = request.form.get('englishword').strip().title()
        definition = request.form.get('description').strip().title()
        levels = request.form.get('difficultylevel')
        # This code above is used to pull information from the website regarding the items in the brackets. It then strips them
        # of their unnecessary spaces and then gives them title case.
        deleting = request.form.get('deleting')
        if len(english) < 1:
            return redirect("/menu?error=Wrong")
        elif len(maori) < 1:
            return redirect("/menu?error=Wrong")
        else:

            con = create_connection(DB_NAME)
            # This connects it to the database
            query = "INSERT INTO words (maori, english, category, definition, levels, images, id) " \
                    "VALUES(?, ?, ?, ?, ?, ?, NULL)"

            cur = con.cursor()
            editor_id = session['userid']
            try:
                # This line is used to execute the query
                cur.execute(query, (
                    maori, english, category, definition, levels, editor_id))
            except:
                return redirect('/categories/' + cat_id + '?error=Unknown+error')

            con.commit()
            con.close()

        if request.form.get("form") == "edit":
            con = create_connection(DB_NAME)
            # This connects it to the database
            query = "UPDATE INTO words SET (maori, english, category, definition, levels, images, id) " \
                    "VALUES(?, ?, ?, ?, ?, ?, NULL)"

            editor_id = session['userid']
            try:
                # This line is used to execute the query
                cur.execute(query, (
                    maori, english, category, definition, levels, editor_id))
            except:
                return redirect('/categories/' + cat_id + '?error=Unknown+error')

            con.commit()
            con.close()

        if deleting == "False":
            english = request.form.get('english').strip().title()
            maori = request.form.get('maori').strip().title()
            definitions = request.form.get('definitions').strip().lower()
            levels = request.form.get('levels')

            con = create_connection(DB_NAME)

            query = "SELECT id, maori, english FROM words WHERE maori = ? or english = ?"
            cur = con.cursor()
            cur.execute(query, (maori, english))
            # This executes the query
            word_repeated = cur.fetchall()
            # This puts the result into the table
            con.close()

            date_added = datetime.today().strftime("%A, %d, %B, %Y")
            user_id = session['userid']
            print("test 1")
            if len(word_repeated) != 0:
                flash('Word already exists in the Dictionary, try again')
                print("test 2")
                return redirect(request.referrer)
            # This makes it so that if there is already a word that is in the database it doesn't allow it by showing
            # An error message
            elif len(maori) > 20:
                flash('Maori word is over 20 characters, try again')
                return redirect(request.referrer)
            # This Makes it so that if a Maori word is over 20 characters long you have to shorten it.
            elif len(english) > 20:
                flash('English word is over 20 characters, try again')
                return redirect(request.referrer)
            # This does the same as the above but for English words
            elif not 2 < len(definitions) < 100:
                return redirect('Description must be below 100 and above 2')
                return redirect(request.referrer)
            else:
                # This gives a limit on the description
                print("test 3")
                con = create_connection(DB_NAME)
                query = "INSERT INTO words(id, maori, english, definitions, levels, category, images, editor_id, date_added) " \
                        "VALUES(NULL,?,?,?,?,?, 'noimage', ?, ? )"
                cur = con.cursor()
                cur.execute(query, (maori, english, definitions, levels, cat_id, user_id, date_added))
                con.commit()
                con.close()
                print("test 4")
                # This code above is used to secure the location of where the words are, this allows it to find out
    #             Where duplicate words are.

    con = create_connection(DB_NAME)
    query = "SELECT id, maori, english, definition, levels, images FROM words WHERE category=?" \
            "ORDER BY maori ASC"
    cur = con.cursor()
    cur.execute(query, (int(cat_id),))
    definition = cur.fetchall()
    print(definition)
    con.close()
    return render_template('words.html', definitions=definition, logged_in=is_logged_in(), deleting=intention("delete"),
                           categories=fetch_categories(), category=cat_id)


# This again creates a connection to the dictionary but then it allows the words and categories to be deleted
# from the template


@app.route('/detail/<word_id>', methods=["POST", "GET"])
def render_detailpage(word_id):
    # This also creates a webpage but this one is for the word details, e.g when you click on a word
    print(request.method)
    if request.method == "POST" and is_logged_in():
        # This line here makes sure that you have to be logged in to actually add/delete/edit
        print("checking word")
        if "delete_confirm" in request.form:
            print(request.form)
            con = create_connection(DB_NAME)
            cur = con.cursor()
            query = "DELETE FROM words WHERE id=?"
            cur.execute(query, (word_id,))
            con.commit()
            con.close()
            return redirect('/')
        else:

            print(request.form)
            english = request.form.get('EnglishWord').strip().title()
            maori = request.form.get('MaoriWord').strip().title()
            definitions = request.form.get('Definitions').strip().lower()
            levels = request.form.get('levels')
            cat_id = request.form.get('Category')
            con = create_connection(DB_NAME)

            date_added = datetime.today().strftime("%A, %d, %B, %Y")
            user_id = session['userid']
            print("test 1")


            if len(maori) > 20:
                flash('Maori word is over 20 characters, try again')
                return redirect(request.referrer)
            # This Makes it so that if a Maori word is over 20 characters long you have to shorten it.
            elif len(english) > 20:
                flash('English word is over 20 characters, try again')
                return redirect(request.referrer)
            # This does the same as the above but for English words
            elif not 2 < len(definitions) < 100:
                return redirect('Description must be below 100 and above 2')
                return redirect(request.referrer)
            else:
                # This gives a limit on the description
                print("test 3")
                con = create_connection(DB_NAME)
                query = "UPDATE words " \
                        "SET maori = ?, english = ?, definitions = ?, levels = ?, category = ?, editor_id = ?, date_added = ?) " \
                        "WHERE id = ?"
                cur = con.cursor()
                # cur.execute(query, (maori, english, definitions, levels, cat_id, user_id, date_added))
                cur.execute(query, (maori, english, definitions, levels, cat_id, user_id, date_added, word_id))
                con.commit()
                con.close()

    con = create_connection(DB_NAME)
    query = "SELECT id, maori, english, definition, levels, images FROM words WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (word_id,))
    definition = cur.fetchall()[0]
    print(word_id)

    # query = "DELETE FROM words WHERE id = ?"
    # cur = con.cursor()
    # print(word_id)
    # cur.execute(query, (word_id,))
    # con.close()
    return render_template('detail.html', definition=definition, logged_in=is_logged_in(),
                           categories=fetch_categories(),
                           deleting=intention("delete"))


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
# This makes it sure that you are logged in

@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():
        return redirect('/')
    # This is the webpage for the signup
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        # These are the requirements for the sign in
        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)
        # This creates a connection
        query = "INSERT INTO customers (id, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # You need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))  # this line executes the query
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+is+already+used')
        # This gives the sign that the email is already in use when you try to signup with a used email
        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', logged_in=is_logged_in())

# This makes it so you need to be logged in
#
# "delete_confirm" in request.form:()
#             con = create_connection(DB_NAME)
#             cur = con.cursor()
#             query = "DELETE FROM dictionary WHERE id=?"
#             cur.execute(query, (maori))
#             con.commit()
#             con.close()
#             return redirect('/')
#
#             deleting = request.form.get('deleting')
#             # print(request.form))()

@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+later!')
# This gives you a message when you log out

def is_logged_in():
    if session.get("email") is None:
        print("you are not logged in")
        return False
    else:
        print("you are logged in")
        return True
# This is used to tell you if you are logged in or not

# @app.route('/menu')
# def render_menu():
#     return render_template('menu.html')
#
# @app.route('/detail')
# def render_delete():
#
#     return render_template('detail.html', categories=fetch_categories())

if __name__ == "__main__":
    app.run(debug=True)