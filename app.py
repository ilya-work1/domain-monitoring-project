from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from login import check_login, check_username_avaliability, registration
from domains_check_MT import check_url_mt as check_url
from session_handler import init_sticky_sessions
import os
import json
from datetime import timedelta
from oauthlib.oauth2 import WebApplicationClient
import requests
from config import Config, logger
from DataManagement import load_domains, remove_domain, update_user_task, delete_user_task, load_user_tasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import time

# Initialize Flask application
app = Flask(__name__)
init_sticky_sessions(app)
app.config["SESSION_PERMANENT"] = Config.SESSION_PERMANENT
app.config["PERMANENT_SESSION_LIFETIME"] = Config.PERMANENT_SESSION_LIFETIME 
app.config["SESSION_TYPE"] = Config.SESSION_TYPE
app.config["SESSION_COOKIE_SAMESITE"] = Config.SESSION_COOKIE_SAMESITE  # Prevents CSRF while allowing normal navigation
app.config["SESSION_COOKIE_SECURE"] = Config.SESSION_COOKIE_SECURE  # Allow cookies over HTTP 
app.config["SESSION_COOKIE_HTTPONLY"] = Config.SESSION_COOKIE_HTTPONLY  # Prevents JavaScript access to session cookie
app.config["SESSION_COOKIE_NAME"] = "STICKY_SESSION_ID"  # Custom session cookie name
app.config["SESSION_REFRESH_EACH_REQUEST"] = Config.SESSION_REFRESH_EACH_REQUEST  # Update session cookie on each request
session_interface = Session(app)
session_interface.permanent = True

os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1'

# Set up Google OAuth client
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

# Initialize scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()

# Dictionary to store user-specific schedules
user_schedules = {}


"""
------------------------------
    routes for schedular
------------------------------

"""
# Schedule a task to run hourly
@app.route("/schedule/hourly", methods=["POST"])
def schedule_hourly():   
    username = session.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data = request.json
    domains = [domain["url"] for domain in load_domains(username)]
    interval = data.get("interval", 1)

    if not domains or interval <= 0:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    job_id = f"{username}_hourly_task"
    scheduler.add_job(
        func=check_url,  #function for the task
        trigger=IntervalTrigger(hours=interval),
        args=[domains, username],
        id=job_id,
        replace_existing=True
    )
    next_run = scheduler.get_job(job_id).next_run_time
    new_task = {
        "type": "hourly",
        "interval": interval,        
        "next_run": next_run.strftime("%Y-%m-%dT%H:%M:%S"),
        "job_id": job_id
    }
    update_user_task(username, new_task)
    return jsonify({"status": "success", "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S")})

# Schedule a task to run daily
@app.route("/schedule/daily", methods=["POST"])
def schedule_daily():
    username = session.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data = request.json
    domains = [domain["url"] for domain in load_domains(username)]
    time = data.get("time", "00:00")
    hour, minute = map(int, time.split(":"))

    if not domains:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    job_id = f"{username}_daily_task"
    scheduler.add_job(
        func=check_url, # function for the task
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[domains, username],
        id=job_id,
        replace_existing=True
    )
    next_run = scheduler.get_job(job_id).next_run_time
    new_task = {
        "type": "daily",
        "time": time,        
        "next_run": next_run.strftime("%Y-%m-%dT%H:%M:%S"),
        "job_id": job_id
    }
    update_user_task(username, new_task)
    return jsonify({"status": "success", "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S")})

# Stop all scheduled tasks for the current user
@app.route("/schedule/stop", methods=["POST"])
def stop_schedule():
    username = session.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    #if username in user_schedules and user_schedules[username].get("job_id"):
       # job_id = user_schedules[username]["job_id"]        
       # scheduler.remove_job(job_id)
       # user_schedules.pop(username, None)
       # logger.debug('deleting task')
    delete_user_task(username)

    return jsonify({"status": "success", "message": "Scheduler stopped for current user"})

# Check the status of scheduled tasks
@app.route("/schedule/status", methods=["GET"])
def schedule_status():
    username = session.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    tasks = load_user_tasks(username).get("tasks", [])
    if tasks:
        return jsonify({"status": "success", "tasks": tasks})
    else:
        return jsonify({"status": "no task", "tasks": tasks})


"""
------------------------------
   routes for google login
------------------------------

"""

# Route to initiate Google Login
@app.route("/google-login")
def google_login():
    """
    Redirects the user to the Google login page to authenticate.
    """
    google_provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    
    callback_url = Config.CallbackUrl
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=callback_url, 
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

# Callback route after Google login
@app.route("/google-login/callback")
def callback():
    """
    Handles the callback from Google login and sets up the user session.
    """
    try:
        logger.debug("Processing Google login callback")
        code = request.args.get("code")
        google_provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        callback_url = Config.CallbackUrl
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=callback_url,  
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens and fetch user information
        client.parse_request_body_response(json.dumps(token_response.json()))
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        # Check if email is verified and create/update user session
        if userinfo_response.json().get("email_verified"):
            user_data = userinfo_response.json()
            unique_id = user_data["sub"]
            users_email = user_data["email"]
            users_name = user_data.get("name", "")
            profile_picture = user_data.get("picture", "")
            
            logger.debug(f"Google authentication successful for: {users_email}")
            
            # Check if user exists first
            is_new_user = check_username_avaliability(users_email)
            
            if is_new_user:
                logger.info(f"Registering new Google user: {users_email}")
                registration(
                    username=users_email,
                    password=unique_id,
                    full_name=users_name,
                    is_google_user=True,
                    profile_picture=profile_picture
                )
            else:
                logger.info(f"Existing Google user logged in: {users_email}")

            # Set session data for the user
            session["username"] = users_email
            session["full_name"] = users_name
            session["profile_picture"] = profile_picture
            session["is_google_user"] = True
            
            logger.info(f"Google user session created for: {users_email}")
            return redirect("/")
            
    except Exception as e:
        logger.error(f"Error in Google callback: {str(e)}", exc_info=True)
        return "Login failed", 400



# Home route
@app.route("/")
def index():
    """
    Redirects to the login page if the user is not logged in, otherwise to the dashboard.
    """
    if not session.get("username"):
        # if not, then redirect to the login page
        return render_template("index.html")
    return render_template('dashboard.html', username=session.get("username"))

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Serve static files
@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

"""
------------------------------
     routes for login
------------------------------

"""

# Login route
@app.route('/login', methods=['POST'])
def login():
    """
    Validates user credentials and creates a session.
    """
    # Get input user from form
    username = request.form.get('username')
    password = request.form.get('password')
    print(f'username:{username}, password:{password}')
    # Validate credentials
    if check_login(username, password):
        session['username'] = username  # Create session
        print("you are logged in", session['username'])
        return redirect("/")# Redirect to the dashboard
    else:
        print("you are not logged in")
        message = "Wrong Username or Password"
        return render_template("index.html", error_message=message)

# Check username availability
@app.route('/checkUserAvaliability', methods=['GET'])
def checkUserAvaliability():
    """
    Checks if a username is available for registration.
    """
    username = request.args.get('username')
    if check_username_avaliability(username):
        return { "available": True }
    else:
        return { "available": False }


# Registration page
@app.route('/register')
def register():
    return render_template('registration.html')

# Create a new user
@app.route('/NewUser', methods=['POST'])
def NewUser():
    """
    Handles new user registration.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    registration(username, password) # Register the user
    message = "You have successfully registered. Please sign in."
    return render_template("index.html", positive_message=message)
    
# Logout route
@app.route("/logout")
def logout():
    """
    Clears the user's session and logs them out.
    """
    username = session.get('username')
    session.clear()  # Clear all session data
    if username:
        logger.info(f"User logged out: {username}")
    return redirect("/") # Redirect to the login page


# Route to check domains
@app.route('/check_domains', methods=['POST'])
def check_domains():
    """
    Checks the status of domains provided by the user.
    """
    try:
        username = session.get('username')
        if not username:
            logger.warning("User not logged in")
            return redirect("/")
        
        # Get domains from request body
        data = request.get_json()
        domains = data.get('domains', [])
        logger.info(f"User {username} started checking {len(domains)} domains.")
    
        #Start timing 
        start_time = time.time()


        # Use existing check_url_mt function
        results = check_url(domains, username)

        #Measure time taken
        elapsed_time = time.time() - start_time
        logger.info(f"Performance Summary for {username}: Checked {len(domains)} domains in {elapsed_time:.2f} seconds.")


        logger.info(f"Results: {results}")

        return jsonify(results)
    except Exception as e:
        logger.error(f"Error occurred while checking domains: {str(e)}", exc_info=True)
        return jsonify({'message': 'An error occurred while checking domains.', 'error': str(e)}), 500

# Route to retrieve user domains    
@app.route('/get_domains', methods=['GET'])
def get_domains():
    """
    Retrieves the list of domains saved for the logged-in user.
    """
    try:
        username = session.get('username')
        if not username:
            return redirect("/")
        
        # Get domains from database
        data = load_domains(username)

        return jsonify(data)
    except Exception as e:
        logger.error(f"Error occurred while retrieving domains: {str(e)}", exc_info=True)
        return jsonify({'message': 'An error occurred while reading domains data.', 'error': str(e)}), 500
    
# Route to remove a domain from the database
@app.route('/remove_domain', methods=['DELETE'])
def remove_domain_from_database():
    try:
        username = session.get('username')
        if not username:
            return redirect("/")
        
        # Get the domain to be removed from query parameters
        domain_to_remove = request.args.get('domain')
        
        if not domain_to_remove:
                return jsonify({'message': 'No domain provided for deletion!'}), 400

        # Remove the domain using the appropriate function
        if remove_domain(domain_to_remove, username):  
            return jsonify({'message': f'Domain {domain_to_remove} deleted successfully.'}), 200
        else:
            return jsonify({'message': f'Domain {domain_to_remove} not found or cannot be deleted.'}), 404

    except Exception as e:
        logger.error(f"Error occurred while removing domain: {str(e)}", exc_info=True)
        return jsonify({'message': 'An error occurred while removing the domain.', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(
        debug=Config.FLASK_DEBUG,
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT
    )