# Udemy Alerts Course Prices
## This projects aims at sending me notifications every time a tracked course has a discount on his price

## I - Project requirements:
### 1 - python packages listed in the requirements.txt
### 2 - a python interpreter >= 3.10
### 3 - a json file containing all the urls of the courses I want to be notified if they're on discount, an example of what it should looks like is in the file named "urls_exmaple.json"
### 4 - your email, so you can receive alerts.

## II - How it works ?

### When the program starts, it starts scrapping informations on every courses in urls.json. Especially the program is searching for the name, description, price, currency of the price, the image link and the course link. 
### Then all these datas are stored in a csv file at csv/courses_tracked_prices.csv.
### We filter all the courses which are discounted and we send an alert email to your email.
### We may encounter some errors while scrapping or at any moment, if so, I made sure that the owner of the project receive the log file by email.