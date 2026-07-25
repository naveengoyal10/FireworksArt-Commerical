import os
from pathlib import Path

import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Upload local media files from the project media directory to Cloudinary.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--media-dir',
            type=str,
            default=str(Path(settings.BASE_DIR) / 'media'),
            help='Local media directory to upload files from.',
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Upload without confirmation.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing Cloudinary assets with the same public ID.',
        )

    def handle(self, *args, **options):
        if not (os.getenv('CLOUDINARY_URL') or (
                os.getenv('CLOUDINARY_CLOUD_NAME') and os.getenv('CLOUDINARY_API_KEY') and os.getenv('CLOUDINARY_API_SECRET'))):
            raise CommandError(
                'Cloudinary credentials are required. Set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.'
            )

        media_dir = Path(options['media_dir']).resolve()
        if not media_dir.exists() or not media_dir.is_dir():
            raise CommandError(f'Media directory does not exist: {media_dir}')

        if not options['yes']:
            self.stdout.write(self.style.WARNING('This command will upload all files from your local media directory to Cloudinary.'))
            self.stdout.write(f'Media directory: {media_dir}')
            confirm = input('Continue? [y/N]: ').strip().lower()
            if confirm != 'y':
                raise CommandError('Upload cancelled.')

        success_count = 0
        skip_count = 0
        error_count = 0

        for file_path in sorted(media_dir.rglob('*')):
            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(media_dir)
            public_id = relative_path.with_suffix('').as_posix()
            folder = relative_path.parent.as_posix()
            if folder == '.':
                folder = None

            self.stdout.write(f'Uploading {relative_path} -> public_id={public_id} folder={folder or "(root)"}')
            try:
                upload_options = {
                    'use_filename': True,
                    'unique_filename': False,
                    'overwrite': options['overwrite'],
                    'resource_type': 'image',
                }
                if folder:
                    upload_options['folder'] = folder

                cloudinary.uploader.upload(str(file_path), public_id=public_id, **upload_options)
                success_count += 1
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'Failed to upload {relative_path}: {exc}'))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Upload complete: {success_count} files uploaded, {skip_count} skipped, {error_count} errors.'
        ))
