"""
Django command to wait for the database to be available.
"""
import time

from psycopg import OperationalError as PsyCopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        '''Logic of the command'''
        self.stdout.write("Waiting for the database..")
        db_ready = False
        while db_ready is False:
            try:
                self.check(databases=['default'])
                db_ready = True
            except (PsyCopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 sec.")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is available!'))
