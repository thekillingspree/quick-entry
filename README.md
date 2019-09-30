# Quick-Entry

Quick-entry for ***Terna Engineering College***.
●Quick-Entry is an Entry Management system
●rooms like the Library, Reading Room, Reference Room etc
which require students to enter their name, ID number, date and
time of entry
●This becomes quite a lengthy process and often leads to a long
queue near the entry register
● Quick-Entry is a solution to handle this type of situations with
ease


Uses Flask, MongoDB with the mongoengine ODM on the backend. 
Uses JWT token based authentication.

## Setup

Get the current codebase

    $ git init
    $ git remote add github git@github.com:thekillingspree/quick-entry.git
    $ git pull github master 
Install `virtualenv` if you haven't already

    $ pip install virtualenv
Create and activate a new virtual environment.

    $ virtualenv venv
    $ source ./venv/bin/activate
**Note(WINDOWS):**  You need to run the activate.bat or activate file on cmd and activate.ps1 on powershell.

Install Required modules

    (venv) $ pip install -r requirements.txt

## Starting the server

On Linux

    (venv) $ gunicorn server.sever:app
    
On Windows

    (venv) > waitress-serve --port=<port-number> server.sever:app
 
