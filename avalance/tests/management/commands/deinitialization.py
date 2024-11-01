import os

from django.core.management import BaseCommand, CommandError

from avalance.settings import base


class Command(BaseCommand):
    help = "nullifies the consequences of initialization - deletes media files, database, migrations"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Deinitialization...'))

        db_path = os.path.join(base.BASE_DIR, 'db.sqlite3')
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            raise CommandError("To run the deinitialization command, you must close the shell and disconnect from the database in programs currently interacting with it")

        migrations_dir = os.path.join(base.BASE_DIR, 'stock', 'migrations')
        if os.path.exists(migrations_dir):
            for filename in os.listdir(migrations_dir):
                file_path = os.path.join(migrations_dir, filename)
                if filename != '__init__.py' and os.path.isfile(file_path):
                    os.remove(file_path)

        self.stdout.write(self.style.SUCCESS('Deinitialization completed'))
