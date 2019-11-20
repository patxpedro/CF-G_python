from flask import Flask, session, render_template, request, redirect
from dotenv import load_dotenv
import os
import requests
import json
import xmltodict
import pandas as pd
import numpy as np

load_dotenv() #load environment variables from a file named .env
api_key = os.getenv("goodreads_key")

#Create the application_main page
app = Flask("BookParlour")
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RM'

availableBooks = json.load(open('static/data/available_books.json', 'r'))

#Display index page at "/"
@app.route("/")
def mainSearch ():
    return render_template('index.html', list = availableBooks.values())

@app.route("/about")
def about ():
    return render_template('about.html')

@app.route("/listed")
def listed ():
    return render_template('listed.html', list = availableBooks.values())

#Display results of search for user's book
@app.route("/search", methods=['POST', 'GET'])
def search():
    searchText = request.args.get("searchText")
    if not searchText:
        return render_template('search.html', data = []) #if search is empty, return empty list
    searchResults = getResults(searchText) #calls function that returns results from API, passes searchText as parameter
    return render_template('search.html', data = searchResults) #reads html template, looks for placeholder and replaces them with values


#Display form to add user's book
@app.route("/list_book")
def list_book():
    title = request.args.get("bookTitle")
    return render_template('list_book.html', title=title)

@app.route("/addBook", methods=["POST"])
def addBook():
    form_data = request.form

    if 'username' not in session.keys():
        error = 'You must be logged in before you can add a book'
        return render_template('list_book.html', error=error)
    
    if session['username']:
        bookTitle = form_data["book"]

        print(session)

        name = session["username"]
        user = json.load(open('static/data/users.json', 'r'))[name]
        
        email = user["email"]
        postcode = user["postcode"]

        newBook = {"name": name, "bookTitle": bookTitle,"postcode": postcode, "email": email}

        availableBooks.update({bookTitle:newBook})
        json.dump(availableBooks, open('static/data/available_books.json', 'w'))

        # return render_template('index.html')
        return redirect('/')
    
    error = 'You must be logged in before you can add a book'
    return render_template('list_book.html', error=error)

#gets results from API
def getResults(searchText):
    # Documentation for this specific endpoint is here: https://www.goodreads.com/api/index#search.books
    # The documentation tells you the URL to enter here in 'endpoint'
    endpoint = 'https://www.goodreads.com/search/index.xml'
    # Look in the 'parameters' section of the documentation to fill this bit in
    payload = {"key": api_key, "q": searchText}
    response = requests.get(endpoint, params=payload)

    # This takes the xml type data and turns it into JSON data
    xpars = xmltodict.parse(response.text)
    raw_json = json.dumps(xpars)
    book_data = json.loads(raw_json)
    totalResults = book_data["GoodreadsResponse"]["search"]["results"]
    if not totalResults:
        return []

    bookList = book_data["GoodreadsResponse"]["search"]["results"]["work"]
    results = [] #list to store results
    for book in bookList:
        title = book["best_book"]["title"]
        author = book["best_book"]["author"]["name"]
        image = book["best_book"]["image_url"]
        myBook = {
           "title": title,
           "author": author,
           "image": image
        }
        results.append(myBook)

    return results

@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()
    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        users = json.load(open('static/data/users.json', 'r'))
        user_in_keys = username in users.keys()

        if user_in_keys == False:
            error = 'Invalid Username/Password'

        else:
            session['username'] = username
            session['password'] = password

            return redirect("/")

    return render_template('login.html', error=error)


@app.route("/signup", methods=["POST", "GET"])
def signuppage():
    return render_template('signup.html')

def update_user_data(form_data):

    username = form_data["username"]
    password = form_data["password"]
    email = form_data["email"]
    postcode = form_data["postcode"]

    users = json.load(open('static/data/users.json', 'r'))

    user_in_keys = username in users.keys()
    
    if user_in_keys == True:
        print(f'You are already registered {username}')
    else:
        users.update({username : {
            'password' : password,
            'email' : email,
            'postcode' : postcode,
        }})

    json.dump(users, open('static/data/users.json', 'w'))
    
    return

@app.route("/update_users", methods=["POST", "GET"])
def update_users():
    #username, password, users
    form_data = request.form
    
    update_user_data(form_data)

    return redirect('/')


def add_to_reading_list(username, reading_lists, book, blurb=''):
    book = book.title()
    
    if username not in reading_lists.keys():
        reading_lists[username] = dict()
    if book in reading_lists[username].keys():
        print(f'{book} has already been added to {username}\'s reading list')
        return reading_lists
    
    reading_lists[username][book] = blurb
    
    return reading_lists

    username = ["username"]
    bookTitle = form_data["book"]

    reading_lists = add_to_reading_list(username, reading_lists, book)
    reading_lists

app.run(debug=True)