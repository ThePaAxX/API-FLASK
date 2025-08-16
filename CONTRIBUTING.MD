# CONTRIBUTING

## How to run the DockerFile locally

'''
docker run -dp 5001:5000 -w /app -v "$(pwd):/app" IMAGE_NAME sh -c 'flask run --host 0.0.0.0 --reload'
'''