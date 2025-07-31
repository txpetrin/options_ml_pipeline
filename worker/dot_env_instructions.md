Keep the .env file in this filepath under the name '.env'. There shall be a single line in the file using a polygion.io key.

## Rationale behind this: 
During development we want this all to be hosted locally without sharing any API keys. Because our runs were not hosted (yet) via K8s or using Git Actions it would not make any sense to use Git Secrets. Local .env files which are ignored via the .gitignore seemed like the best bet here. 

POLYGON_KEY=polygon.io_user_api_key