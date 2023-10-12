# Cloud-Image-Manager

## Webiste Url

Project I: [Cloud Image Manager (VM Infra)](http://34.106.224.155:8000)

Project II: [Cloud Image Manager (Serverless)](https://image-manager-g-e5hfku65bq-wl.a.run.app/)

## Setup

### Run locally

1. Setup python and pip on your machine
2. Install necessary packages using:

```
> pip install -r requirements.txt
```

3. Start the application:

```
> python app.py
```

### Using docker

1. Setup docker on your machine and start docker service
2. Create docker image:

```
> docker build -t image-manager
```

3. Run docker container:

```
docker run -p 4000:5000 image-manager
```

## Technologies Used

1. Python Flask
2. HTML
3. CSS
4. Google OAuth2 (User Authentication)
5. Google Cloud Datastore (Stores image metadata)
6. Google Cloud Storage (Stores images)
7. Google Cloud Artifact Registry (Stores docker image)
8. Google Cloud Run (Serverless)
