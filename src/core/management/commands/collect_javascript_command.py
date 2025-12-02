import os
import time
from pathlib import Path

from protectapp import settings
from src.core.management.commands.base_command import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        directory = settings.STATICFILES_DIRS[0]
        exclude_files = [
            'push_notifications.js',
            'service_worker.js',
            'install_app.js'
        ]
        file_min_js = f'{directory}/js/all.min.js'
        if os.path.exists(file_min_js):
            os.unlink(file_min_js)

        # Just to delete the file properly
        time.sleep(1)

        js_content = []
        for root, _, files in os.walk(directory):
            for filename in files:  # loop through files in the current directory
                full_path = Path(os.path.join(root, filename))

                if full_path.suffix != '.js':
                    continue

                if filename in exclude_files:
                    self.warning('Excluding file {}'.format(full_path))
                    continue

                with open(full_path, 'r') as file:
                    js_content.append(file.read())

        with open(file_min_js, 'w') as f:
            f.write('\n\n'.join(js_content))

        # @TODO obfuscate

        self.success('File written')
