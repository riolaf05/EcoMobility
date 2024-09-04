# Symptom app

1. Create exports

```console
export PROJECT_ID=progetti-poc
export APP=symptom-app 
export PORT=8501
export REGION=europe-west8
export BRANCH=master
export TAG=${REGION}-docker.pkg.dev/${PROJECT_ID}/${APP}/${APP}:${BRANCH}
```

2. Create Artifact Repo

```console
gcloud artifacts repositories create ${APP} --repository-format Docker --location europe-west8 --project progetti-poc
```

3. Create Build

```console
gcloud builds submit --tag  ${TAG} --project progetti-poc
```

Or

```console
docker build -t ${TAG} .
docker push ${TAG}
```

4. Deploy 

```console
gcloud run deploy $APP --image $TAG --platform managed --region $REGION --port $PORT --allow-unauthenticated --cpu 2 --memory 1Gi --env-vars-file=.env.gcloud
```

5. Clean 

```console
gcloud run services delete $APP --region $REGION 
gcloud run services list
```

