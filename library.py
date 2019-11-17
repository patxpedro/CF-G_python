from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
import json
import xmltodict

load_dotenv() #load environment variables from a file named .env
api_key = os.getenv("goodreads_key")

#Create the application_main page
app = Flask("BookParlour")

#Display index page at "/"
@app.route("/")
def mainSearchx ():
    return render_template('index.html')

#Display search page with results
@app.route("/search")
def search():
    searchText = request.args.get("searchText")
    if not searchText:
        return render_template('search.html', data = []) #if search is empty, return empty list
    searchResults = getResults(searchText) #calls function that returns results from API, passes searchText as parameter
    return render_template('search.html', data = searchResults) #reads html template, looks for placeholder and replaces them with values

@app.route("/searchresults")
def searchResults():
    searchText = request.args.get("searchText")
    return {'results': getResults(searchText)}

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

app.run(debug=True)