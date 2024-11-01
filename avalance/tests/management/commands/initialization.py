from django.core.management import BaseCommand, call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "initialization command, run this command once"

    def has_migrations_applied(self):
        app_label = 'tests'
        try:
            recorder = MigrationExecutor(connection)
        except ValueError:
            return False
        applied_migrations = recorder.loader.applied_migrations

        return any(app_label == migration[0] for migration in applied_migrations)

    def handle(self, *args, **options):
        if self.has_migrations_applied():
            self.stdout.write(self.style.ERROR('Initial data has already been initialized'))
        else:
            self.stdout.write(self.style.NOTICE('Initialization...'))

            call_command('makemigrations')
            call_command('migrate')
            call_command('generate_data')

            self.stdout.write(self.style.SUCCESS('Initialization completed'))
