# DESCRIPTION

Calamity-Cycling is a Flask application that analyzes my cycling activities. Using the `refresh` endpoint, it downloads all my activities from my Strava account and stores them in MongoDB.
The app uses D3.js to draw graphs. Multiple pieces of information are available:

* Fastest activity  
* Longest activity  
* Total distance  

![Alt text](demo-pictures/global-info.png?raw=true "img0")

* Average speed for a given month/year  

![Alt text](demo-pictures/average-speed-for-a-given-year-month.png?raw=true "img0")

* Graph of monthly distance for a given year  

![Alt text](demo-pictures/monthly-distance.png?raw=true "img0")

* Graph of average speed by activity day for a given segment  

![Alt text](demo-pictures/stat-for-a-given-segment.png?raw=true "img0")

---

# RUNNING THE APP LOCALLY

* You must create a file named `.env` in the repository project containing the following variables:

```
CLIENT_ID=client_id_of_your_app_created_in_strava
CLIENT_SECRET=client_secret_app_retrieve_from_strava
READ_AUTHORIZATION_CODE=below_how_to_retrieve_the_read_authorization_code
WRITE_AUTHORIZATION_CODE=below_how_to_retrieve_the_write_authorization_code
```

**Warning:** The `.env` file must end with an empty line (`\n`).

---

* Retrieve read authorization code

Paste the link below into your browser. Don't forget to replace `client_id` with the ID of your app created in Strava.  
Authenticate and authorize the app with the required permissions.

http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

You will be redirected to a non-working page. Extract the `authorization_code` from this page URL:

http://localhost/exchange_token?state=&code={authorization_code}&scope=read,activity:read_all,profile:read_all

---

* Retrieve write authorization code

Same procedure as the read authorization code, but use the link below:

http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:write,activity:write

---

* Run the command below to start the app:

```

# Assuming you have Docker installed
# enable venv 
docker compose up --build
```
# Then go to:
[http://localhost:5000](http://localhost:5000)



---

# TODO

* You need to start packaging the Calamity app into Docker. Check how to pass the `CLIENT_ID` environment variable via `docker run`. Automate the process of obtaining user credentials in order to automatically create the `.env` file.  

* Show segment info when clicking on a graph point  
* Create a graph for monthly elevation and burned calories  
* Add a section showing top 10 segments (name, distance, average grade, number of times passed through)  
* Add a refresh button  