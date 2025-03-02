# general
LAMB_APP_SERVERNAME=localhost
LAMB_APP_ALLOWED_HOSTS=localhost,host.docker.internal
LAMB_APP_NAME=api-generic
LAMB_APP_GOD_MODE=true
LAMB_APP_PORT=80
LAMB_APP_SCHEME=http
LAMB_APP_DEBUG=false
LAMB_LOG_JSON_ENABLE=true
LAMB_EXECUTION_TIME_TIMESCALE=true
LAMB_ADD_CORS_ENABLED=false
LAMB_VERBOSE_SQL_LOG=false

LAMB_REDIS_HOST=localhost

LAMB_SMTP_USER=
LAMB_SMTP_PASS=
LAMB_SMTP_HOST=
LAMB_SMTP_PORT=
LAMB_SMTP_TLS=

# APP
APP_SECRET_KEY=123

APP_POSTGRES_USER={{project_name}}_user
APP_POSTGRES_PASS=
APP_POSTGRES_NAME={{project_name}}
APP_POSTGRES_HOST=localhost