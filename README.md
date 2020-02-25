# README #

AMZOrbit -> Boost your Amazon sales with Automatic Listing Repair

The goal of Amzorbit is to help amazon sellers to keep track of their products and quickly revert the unitended changes in the product listing on Amazon that hurts the sales. Amazon orbit continously scraps the Amazon product and validates with the content saved by the sellers. 

Major Features:
    Add product
    Get automated report notifications every few hours
    Get immediate notifications when product content changes. 

Featurs in this code base:
    User Management- User registration and Authentication
    Product Management- Add/Delete products
    Alert Mangament- Customize how you want to receive the notifications
    Payment Management- Payment solution to use amzorbit
    Scrape the content using different servers (As Amazon blocks them in case of continous scraping)
    Decouple the scrapping and validation with the user and product management. 

Modules
* Detect & Alert
* Auto Repair
* Assisted Ticket Creation

### What is this repository for? ###
* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### Starting Frontend Server
* cd frontend
* npm install -> Will install all the dependencies
* npm start -> Start the front end server

### Starting Backend Server
Start Kafka
./bin/zookeeper-server-start.sh config/zookeeper.properties
./bin/kafka-server-start.sh config/server.properties

### Starting Consumer
python3 consumer_start.py

### Starting Flask Server
export EnvMode='local' or 'dev'
python3 app.py

### Dropping Schema
* drop schema amzorbit
* mysql -u root -p < dm_amazorbit.sql  -> Run this from the root folder

