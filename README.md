## Insurance Exchange
![GitHub last commit](https://img.shields.io/github/last-commit/duseth/Insurance-Exchange?label=updated&logo=ableton-live&logoColor=black)
![GitHub pull requests](https://img.shields.io/github/issues-pr/duseth/Insurance-Exchange?logo=git&logoColor=white)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/duseth/Insurance-Exchange?logo=git&logoColor=white)
***
## About
Exchange of insurance companies to attract new customers
***
## Technology Stack
* **Django** (backend) / Django Templates (frontend)
* **PostgreSQL** (database)
* **RabbitMQ** (message broker)
* **Celery** (task queue)
* **Elasticsearch** (search engine)
***
## Quickstart
#### 1. Create `.env` environment file in root directory
#### 2. Provide values for the following variables:
   * **Django**
       * `DEBUG`
       * `DJANGO_SECRET_KEY`
   * **Django ORM**
     * `DATABASE`
     * `DATABASE_NAME`
     * `DATABASE_USER`
     * `DATABASE_PASSWORD`
     * `DATABASE_HOST`
     * `DATABASE_PORT`
   * **PostgreSQL**
     * `POSTGRES_USER`
     * `POSTGRES_PASSWORD`
     * `POSTGRES_DB`
   * **RabbitMQ**
     * `RABBITMQ_USER`
     * `RABBITMQ_PASSWORD`
   * **Celery**
     * `CELERY_BROKER_URL`
   * **Mailing**
     * `UNISENDER_KEY`
     * `COMPANY_NAME`
     * `COMPANY_EMAIL`
   * **Elasticsearch**
     * `ELASTICSEARCH_HOST`
#### 3. Run `docker-compose up --build`