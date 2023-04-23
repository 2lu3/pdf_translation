from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError


class Command(createsuperuser.Command):
    help = "Crate a superuser, and allow password to be provided"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help="Specifies the password for the superuser.",
        )

    def handle(self, *args, **options):
        options.setdefault("interactive", False)

        password = options.get("password")
        username = options.get("username")
        database = options.get("database")
        email = options.get("email")

        if not (username and email and password):
            raise CommandError(
                "--username, --email and --password are required options"
            )

        user_data = {
            "username": username,
            "email": email,
            "password": password,
        }

        exists = (
            self.UserModel._default_manager.db_manager(database)
            .filter(username=username)
            .exists()
        )
        if not exists:
            self.UserModel._default_manager.db_manager(database).create_superuser(
                **user_data
            )
            print(f"new superuser {username} created.")
            print(f"password: {password}")
            print(
                f"exist: {self.UserModel._default_manager.db_manager(database).filter(username=username).exists()}"
            )

        else:
            print(f"superuser {username} already exists")
