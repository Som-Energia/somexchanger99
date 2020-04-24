# somexanger99
exchanging files like hugs. This project is prototype and its deployment in production is not yet stable. 

#### Prerequisites

Before you begin, ensure you have met the following requirements:
* You should have installed `pipenv`. Instructions here -> https://pipenv.readthedocs.io/en/latest/#install-pipenv-today
* You should have a `Linux/Mac` machine. Windows is not supported and we are not thinking in it.
* Optionally, an user with sudo permissions

#### Development
##### Basic GitHub Checkout
We will assume that the folowing folder exists:

  * `PROJECTS_PATH` = `$HOME/projects`

Checkout the project:
```bash
user@host:> git clone git@github.com:Som-Energia/somexchanger99.git $PROJECTS_PATH/somexchanger99
```

Walk throw `$PROJECTS_PATH/somexchanger` and install the requirements with `pipenv`
```bash
user@host:> cd $PROJECTS_PATH/somexchanger
user@host:somexchanger> pipenv install --dev
```

We use a dot env file to configure somexanger99. Copy `.env.example` to `.env` and adapat it to meet your needs.

Run migrations, create an admin user and run the server to check that everything fit.
```bash
user@host:somexchanger> pipenv run ./manage migrate
user@host:somexchanger> pipenv run ./manage createsuperuser
user@host:somexchanger> pipenv run ./manage runserver
```

##### Background tasks
Somexanger99 is thought as a background task runner. Once you have configured the predefined tasks in the admin site, to run them, you have to lunch the worker and the beat processes.

First luch beat process
```bash
user@host:somexchanger> pipenv run celery beat -A config -l info --scheduler  django_celery_beat.schedulers:DatabaseScheduler
```

And in other terminal launch the worker:
```bash
user@host:somexchanger> pipenv run celery -A config worker --pool gevent -l info -E
```

#### Usage


#### Changes


#### Contact
If you want to contact with us, feel free to send an email to <info@somenergia.coop>.

#### License
This project uses the following license: [GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE).
