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

## Creating a database for the tournament project 

To create a database enter psql in the terminal and then enter 'create database tournament;'.  
To connect to the database enter \c tournament
Exit psql by entering \q.  

## Running tournament project

CD into tournament and enter 'python tournament_test.py' to run the tests for this project


