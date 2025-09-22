"""
ProServe Framework Patterns Configuration
Framework detection patterns and configurations for various web frameworks
"""

from .service_models import Framework


def get_framework_patterns():
    """Get framework detection patterns and configurations"""
    return {
        Framework.FLASK: {
            'import_patterns': [
                r'from\s+flask\s+import',
                r'import\s+flask',
                r'Flask\(__name__\)'
            ],
            'decorator_patterns': [
                r'@app\.route\(',
                r'@bp\.route\(',
                r'@blueprint\.route\('
            ],
            'config_files': ['config.py', 'settings.py', 'instance/config.py'],
            'common_files': ['app.py', 'main.py', 'run.py', 'wsgi.py'],
            'dependencies': ['flask', 'werkzeug', 'jinja2']
        },
        Framework.FASTAPI: {
            'import_patterns': [
                r'from\s+fastapi\s+import',
                r'import\s+fastapi',
                r'FastAPI\('
            ],
            'decorator_patterns': [
                r'@app\.get\(',
                r'@app\.post\(',
                r'@app\.put\(',
                r'@app\.delete\(',
                r'@router\.get\(',
                r'@router\.post\('
            ],
            'config_files': ['config.py', 'settings.py', '.env'],
            'common_files': ['main.py', 'app.py', 'api.py'],
            'dependencies': ['fastapi', 'uvicorn', 'starlette', 'pydantic']
        },
        Framework.DJANGO: {
            'import_patterns': [
                r'from\s+django\.',
                r'import\s+django',
                r'django\.conf\.settings'
            ],
            'decorator_patterns': [
                r'@require_http_methods',
                r'@csrf_exempt',
                r'@login_required'
            ],
            'config_files': ['settings.py', 'local_settings.py', 'production.py'],
            'common_files': ['manage.py', 'wsgi.py', 'asgi.py', 'urls.py', 'views.py'],
            'dependencies': ['django', 'djangorestframework']
        },
        Framework.STARLETTE: {
            'import_patterns': [
                r'from\s+starlette\s+import',
                r'import\s+starlette',
                r'Starlette\('
            ],
            'decorator_patterns': [
                r'@app\.route\(',
                r'Route\('
            ],
            'config_files': ['config.py', '.env'],
            'common_files': ['main.py', 'app.py'],
            'dependencies': ['starlette', 'uvicorn']
        },
        Framework.TORNADO: {
            'import_patterns': [
                r'import\s+tornado',
                r'from\s+tornado\s+import',
                r'tornado\.web\.Application'
            ],
            'decorator_patterns': [],
            'config_files': ['settings.py', 'config.py'],
            'common_files': ['main.py', 'app.py', 'server.py'],
            'dependencies': ['tornado']
        },
        Framework.AIOHTTP: {
            'import_patterns': [
                r'from\s+aiohttp\s+import',
                r'import\s+aiohttp',
                r'aiohttp\.web\.Application'
            ],
            'decorator_patterns': [
                r'@routes\.get\(',
                r'@routes\.post\('
            ],
            'common_files': ['main.py', 'app.py', 'server.py'],
            'dependencies': ['aiohttp', 'aiohttp-cors']
        }
    }


def get_database_patterns():
    """Get database detection patterns"""
    return {
        'postgresql': [
            r'import\s+psycopg2',
            r'postgresql://',
            r'from\s+sqlalchemy.*postgresql'
        ],
        'mysql': [
            r'import\s+mysql',
            r'mysql://',
            r'pymysql',
            r'MySQLdb'
        ],
        'sqlite': [
            r'import\s+sqlite3',
            r'sqlite://',
            r'\.db$',
            r'\.sqlite$'
        ],
        'mongodb': [
            r'import\s+pymongo',
            r'from\s+pymongo',
            r'mongodb://',
            r'MongoClient'
        ],
        'redis': [
            r'import\s+redis',
            r'redis://',
            r'Redis\('
        ]
    }


def get_orm_patterns():
    """Get ORM detection patterns"""
    return {
        'sqlalchemy': [r'from\s+sqlalchemy', r'import\s+sqlalchemy'],
        'django-orm': [r'from\s+django\.db', r'models\.Model'],
        'peewee': [r'import\s+peewee', r'from\s+peewee'],
        'tortoise': [r'from\s+tortoise', r'import\s+tortoise']
    }


def get_deployment_files():
    """Get deployment file patterns"""
    return {
        'Dockerfile': 'docker',
        'docker-compose.yml': 'docker',
        'docker-compose.yaml': 'docker',
        'Procfile': 'heroku',
        'app.yaml': 'gcp',
        'requirements.txt': 'python',
        'pyproject.toml': 'python',
        'setup.py': 'python',
        'kubernetes.yaml': 'kubernetes',
        'k8s.yaml': 'kubernetes'
    }
