import os
# import threading
import time

from invoke import task

import os


def get_clear_db_query(file_name="clear.sql"):
    with open(file_name, "r") as f:
        clear_db_query = f.read()

    clear_db_query = clear_db_query.format(db_user=os.environ.get("POSTGRES_USER"))

    return clear_db_query


def wait_port_is_open(host, port):
    import socket

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return
        except socket.gaierror:
            pass
        time.sleep(1)


@task
def devcron(ctx, crontab_name="crontab"):
    ctx.run(f"python -m devcron {crontab_name}")


@task
def init_db(ctx, recreate_db=False):
    wait_port_is_open(os.getenv("POSTGRES_HOST", "db"), 5432)

    if recreate_db:
        clear_db_query = get_clear_db_query()

        ctx.run(f"echo '{clear_db_query}' | python -m manage dbshell")
        ctx.run("python -m manage dbshell < ./db.dump")

    ctx.run("python -m manage makemigrations")
    ctx.run("python -m manage migrate")


@task
def collect_static_element(ctx):
    ctx.run("python -m manage collectstatic --noinput")


@task
def run(ctx):
    init_db(ctx, recreate_db=True)
    collect_static_element(ctx)

    # thread_cron = threading.Thread(target=devcron, args=(ctx,))
    # thread_cron.start()

    ctx.run("uwsgi --ini uwsgi.ini")


@task
def runprod(ctx):
    init_db(ctx)
    collect_static_element(ctx)

    # thread_cron = threading.Thread(target=devcron, args=(ctx,))
    # thread_cron.start()

    ctx.run("uwsgi --ini uwsgi.ini")


@task
def test(ctx):
    wait_port_is_open(os.getenv("POSTGRES_HOST", "db"), 5432)
    ctx.run("python -m manage test")
