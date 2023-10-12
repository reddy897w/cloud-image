import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.cloud import storage, datastore

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET_KEY', 'image-manager-app')

# Set your Google OAuth2 client ID
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '110981627320-n8tfb1l2lpodpojmgqkfg45q84rs630n.apps.googleusercontent.com')

# Path to your client secret file
CLIENT_SECRETS_FILE = 'client_secret.json'

# Set up OAuth2 flow
flow = Flow.from_client_secrets_file(
    client_secrets_file=CLIENT_SECRETS_FILE,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://your-app-url.com/callback"
)

# Configure Google Cloud Storage and Datastore clients using the service account key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account-key.json'
storage_client = storage.Client()
datastore_client = datastore.Client()

# Helper function to check if a user is logged in
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect(url_for('login'))  # Redirect to the login page
        else:
            return function()
    return wrapper

# Login route
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

# Callback route
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/index")

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Index route, which now requires login
@app.route('/index', methods=['GET', 'POST'])
@login_is_required
def index():
    email = session.get('email', '')

    if request.method == 'POST':
        image = request.files['imageInput']
        filename_parts = os.path.splitext(image.filename)
        unique_filename = f"{filename_parts[0]}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{filename_parts[1]}"

        # Upload image to Google Cloud Storage
        bucket = storage_client.bucket('your-bucket-name')
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(
            image.read(),
            content_type=image.content_type
        )

        # Save image metadata to Google Cloud Datastore
        entity = datastore.Entity(
            key=datastore_client.key('Image', unique_filename))
        entity.update({
            'filename': unique_filename,
            'user': email,
            'uploaded_at': datetime.utcnow()
        })
        datastore_client.put(entity)

        return redirect(url_for('index'))

    # Fetch all image metadata from Datastore
    query = datastore_client.query(kind='Image')
    query = query.add_filter(
        filter=datastore.query.PropertyFilter('user', '=', email))
    all_images = list(query.fetch())
    all_images = [image['filename'] for image in all_images]

    return render_template('index.html', images=all_images)

# View image route
@app.route('/view/<filename>')
def view_image(filename):
    image_url = f"https://storage.googleapis.com/your-bucket-name/{filename}"
    return render_template('view.html', image_url=image_url, filename=filename)

# Uploaded file route
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    image_url = f"https://storage.googleapis.com/your-bucket-name/{filename}"
    return redirect(image_url)

# Delete image route
@app.route('/delete/<filename>')
def delete_image(filename):
    # Delete image from Google Cloud Storage
    bucket = storage_client.bucket('your-bucket-name')
    blob = bucket.blob(filename)
    blob.delete()

    # Delete image metadata from Datastore
    key = datastore_client.key('Image', filename)
    datastore_client.delete(key)

    return redirect(url_for('index'))

if __name__ == '__main':
    app.run(host='0.0.0.0', port=8080)
