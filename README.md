rdb-fullstack
=============
Project for Udacity Full Stack Web Developer Nanodegree

## Installation

To run this program you will need to have the following installed:  
* Python
* Vagrant
* VirtualBox

## Running the Project Locally  

Clone this GitHub repository and save to your local machine.  
CD into project and then the vagrant folder in this project.  
In the terminal enter 'vagrant up' and once done enter 'vagrant ssh'.  
CD into /vagrant to enter the virtual machine.   

## Creating a database for the catalog project  

CD into catalog.  
To create a database enter 'python database_setup.py'.  This will create a new database called artistworkwithuser.db inside the catalog folder.  

## Running catalog project  

CD into catalog and enter 'python application.py'.  
You can then view this project at localhost:5000.
If port 5000 is unavailable you can change the port in line 355 in application.py.  

## Get Google Client ID and Client Secret  

In order for the google user authentication to work you will need to create a Google API console project and a client ID and client secret.  Instructions on how to do this can be found at https://developers.google.com/identity/sign-in/web/devconsole-project.  

Once project and client ID is created download the JSON file and save into the catalog project file and call it client_secrets.json.  

## Creating a database for the tournament project 

To create a database enter psql in the terminal and then enter 'create database tournament;'.  
To connect to the database enter \c tournament.  
You can then create the tables by entering \i tournament.sql.  
Exit psql by entering \q.  

## Running tournament project

CD into tournament and enter 'python tournament_test.py' to run the tests for this project. 



