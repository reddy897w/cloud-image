import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, g, session

from google.oauth2 import id_token
from google.auth.transport import requests

from google.cloud import storage, datastore

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './service-account-key.json'

app = Flask(__name__)
app.secret_key = 'super secret key'  # Set a secret key for session management

storage_client = storage.Client()
datastore_client = datastore.Client()

BUCKET_NAME = "cloud-image-app"

# Define the allowed email and password
ALLOWED_EMAIL = "sreedharreddy775@gmail.com"
ALLOWED_PASSWORD = "Cloudmail@321"


@app.before_request
def request_logger():
    print("--------------------------------------")
    print(request.method, "-", request.path)



@app.before_request
def protect():
    if not session.get('logged_in') and request.endpoint != "login":
        flash('You need to log in first', 'error')
        return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the entered credentials are correct
        if email == ALLOWED_EMAIL and password == ALLOWED_PASSWORD:
            # Set a session variable to indicate the user is logged in
            session['logged_in'] = True
            return redirect(url_for("index"))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')



# Add a logout route to clear the session
@app.route("/logout", methods=["POST"])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for("login"))


@app.route('/', methods=['GET', 'POST'])
def index():
    email = g.get('email', '')

    if request.method == 'POST':
        image = request.files['imageInput']
        filename_parts = os.path.splitext(image.filename)
        unique_filename = f"{filename_parts[0]}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{filename_parts[1]}"

        # Upload image to GCP Storage
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(
            image.read(),
            content_type=image.content_type
        )

        # Save image metadata to Datastore
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
    print(all_images)

    return render_template('index.html', images=all_images)


@app.route('/view/<filename>')
def view_image(filename):
    image_url = f"https://storage.googleapis.com/cloud-image-app/{filename}"
    return render_template('view.html', image_url=image_url, filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    image_url = f"https://storage.googleapis.com/cloud-image-app/{filename}"
    return redirect(image_url)


@app.route('/delete/<filename>')
def delete_image(filename):
    # Delete image from GCP Storage
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.delete()

    # Delete image metadata from Datastore
    key = datastore_client.key('Image', filename)
    datastore_client.delete(key)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host='0.0.0.0', debug=False)
