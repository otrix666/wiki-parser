# Set up the virtual environment

```
python3 -m venv venv
source venv/bin/activate
````

# Install dependencies

```pip install -r requirements.txt```

# Load environment variables

```
cp from .env.dist to .env 
export $(grep -v '^#' .env | xargs)
```

# Start Docker services

```docker-compose up -d```

# Command to run the wiki-parser

```python3 -m advanced.main <url> <max_depth>```

# Create database for tests

```docker exec -it <container name | id> sh -c "export PGPASSWORD=$POSTGRES_PASSWORD && psql -h $POSTGRES_HOST -U $POSTGRES_USER -c \"CREATE DATABASE test_db\""```

# Command to run tests

```pytest advanced/tests/```