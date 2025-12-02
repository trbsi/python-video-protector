from django.core.management.base import BaseCommand as DjangoBaseCommand


class BaseCommand(DjangoBaseCommand):
    def success(self, string: str) -> None:
        self.stdout.write(self.style.SUCCESS(string))

    def error(self, string: str) -> None:
        self.stdout.write(self.style.ERROR(string))

    def warning(self, string: str) -> None:
        self.stdout.write(self.style.WARNING(string))

    def info(self, string: str) -> None:
        self.stdout.write(self.style.NOTICE(string))
