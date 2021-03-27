# DESCRIPTION
Calamity-cycling is a flask application that analyze my cycling activities.
Using the ```refresh``` endpoint, It downloads all my activities from my strava account and store them in MongoDB.
The app use d3.js to draw graphs. Multiple information are available :
 * Fastest activity
 * Longest activity
 * Total distance 
 ![Alt text](demo-pictures/global-info.png?raw=true "img0")

 * Average speed for a given month/year
  ![Alt text](demo-pictures/average-speed-for-a-given-year-month.png?raw=true "img0")
 * Graph of a monthly distance for a given year 
 ![Alt text](demo-pictures/monthly-distance.png?raw=true "img0")
 * Graph of the average speed by activity day for a given segment.
   ![Alt text](demo-pictures/stat-for-a-given-segment.png?raw=true "img0")


# RUNNING THE APP LOCALLY
* You must create a file named .env into the repository project which contain these variable
```
CLIENT_ID=client_id_of_your_app_created_in_strava
CLIENT_SECRET=client_secret_app_retrieve_from_strava
READ_AUTHORIZATION_CODE=below_how_to_retrieve_the_read_authorization_code
WRITE_AUTHORIZATION_CODE=below_how_to_retrieve_the_write_authorization_code

``` 
**Warning** .env file must finish with an empty line (\n)

* Retrieve read authorization code

Paste the below link into your browser. Don't forget to replace client_id with the id of your app created in strava.
Authenticate and authorize the app with the checked permission.

http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all
You will be redirect to a non working page. Extract the authorization_code from this page url.

 http://localhost/exchange_token?state=&code={authorization_code}&scope=read,activity:read_all,profile:read_all

* Retrieve write authorization code 

Same procedure as read procedure, but use the below link

http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:write,activity:write

* Run the below command to start the app
```
# Suppose that you have install mongodb  
sudo service mongod restart
source venv/bin/activate
FLASK_APP=app.py flask run 
```

# TODO
* show segment info when clicking on a graph point 
* create a graph for monthly elevation and burned calories
* add a section to show top 10 segments (name, dist, avg grade, number of time you've passed through)
* add the refresh button
* package the app into a docker image 