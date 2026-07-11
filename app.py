from backend import create_app
from celery_config import celery
from flask import render_template
from backend.extensions import cache  

import csv
import io

app = create_app()

# Cache initialization 
cache.init_app(app, config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

from backend.routes import api

if 'trekking_api_unique' not in app.blueprints:
    app.register_blueprint(api, url_prefix='/api/',name='trekking_api_unique')

@app.route('/')
def index():
    return render_template('index.html')

# Celery Configuration
# Important: Celery ko Flask context mein load karein
celery.conf.update(app.config)

if __name__ == '__main__':
    app.run(debug=True)