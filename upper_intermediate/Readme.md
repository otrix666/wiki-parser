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

```python3 -m upper_intermediate.main <url> <max_depth>```
