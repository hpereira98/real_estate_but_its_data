set -e

# Define your local SSH key
export SSH_PRIVATE_KEY=${SSH_PRIVATE_KEY:-$(cat ~/.ssh/id_rsa)}

# Define your local IP
export LOCAL_IP=${LOCAL_IP:-$(ifconfig en0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')}
echo "Using Local IP: $LOCAL_IP"

# Setup virtual environment
DIR=$(pwd)/venv
if [ -d "$DIR" ]; then
    echo "Python Virtual Environment already created. Activating it..."
    source venv/bin/activate
else
    echo "Python Virtual Environment does not exist. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing project dependencies..."
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
fi

# Clean previous containers
docker compose down

# Start services: LocalStack
echo "Running docker compose to Set up local AWS services"
docker compose up -d

# Create LocalStack objects
echo "Creating real-estate bucket.."
awslocal s3 mb s3://real-estate --region us-east-1 --endpoint-url "http://$LOCAL_IP:4566"
