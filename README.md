# Quick-Entry

Quick-entry for TEC

## Setup

Get the current codebase

    $ git init
    $ git remote add github git@github.com:thekillingspree/quick-entry.git
    $ git pull github master 
Install `virtualenv` if you haven't already

    $ pip install virtualenv
Create and activate a new virtual environment.

    $ virtualenv venv
    $ ./venv/Scripts/activate
**Note:**  You need to run the activate.bat or activate file on cmd and activate.ps1 on powershell.

Install Required modules

    (venv) $ pip install -r requirements.txt
Starting the server

    (venv) $ python server/server.py
 
