import os

"""Environment configuration for Windsage.

This module exposes a small set of constants read from environment
variables with reasonable defaults. The rest of the application imports
these names for database and webhook configuration.

Available constants:
- `SQLHOST`: Address and port of the Postgres server (default: "localhost:5432").
- `DBUSER`: Database username (default: 'postgres').
- `DBPASS`: Database password (default: 'mysecretpassword').
- `DBTABLE`: Database name (default: 'sysml2').
- `WINDSTORMHOST`: URL of the Windstorm webhook endpoint used for notifications.
"""

# Host and port for the SQL server, e.g. "localhost:5432" or "db:5432".
SQLHOST = os.environ.get("SQLHOST", "localhost:5432")

DBUSER = os.environ.get("DBUSER",'postgres')
DBPASS = os.environ.get("DBPASS",'mysecretpassword')
DBTABLE = os.environ.get("DBTABLE",'sysml2')

# Webhook endpoint to POST notifications to Windstorm. This is typically
# an internal cluster service in deployments using Argo Events.
WINDSTORMHOST = os.environ.get(
    "WINDSTORMHOST",
    "http://windstorm-webhook-eventsource-svc.argo-events:12000/windstorm"
)
