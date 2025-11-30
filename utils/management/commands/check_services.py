import socket

from django.core.management.base import BaseCommand
from django.db import connections
from django_redis import get_redis_connection


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=5,
            help="Timeout in seconds for service checks (defaults: 5)",
        )

    def handle(self, *args, **options):
        timeout = options["timeout"]

        try:
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            try:
                connections["default"].cursor()
                self.stdout.write(self.style.SUCCESS("✅ Database Connected"))
            except Exception as e:
                self.stderr.write(f"❌ Database connection failed: {e}")
                raise
            try:
                get_redis_connection("default").ping()
                self.stdout.write(self.style.SUCCESS("✅ Redis Connected"))
            except Exception as e:
                self.stderr.write(f"❌ Redis connection failed: {e}")
                raise
        finally:
            socket.setdefaulttimeout(original_timeout)
