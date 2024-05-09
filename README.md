# Creating an appendix from a feature layer

Data is stored on a feature layer hosted by ESRI so to prevent double handling we want to be able to automate the process.
This flask app intends to produce the tex file and output the pdf file to the user after allowing for customisation.

# Use with Docker

A Dockerfile is provided in the repo for ease of use setting up with docker.

First build with 
```console
docker build -t appendix .
```

And then initialize the image with
```console
docker run -p 5050:5050 -e FLASK_RUN_HOST=0.0.0.0 appendix
```
