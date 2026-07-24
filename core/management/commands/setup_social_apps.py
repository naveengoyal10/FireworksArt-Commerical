import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Create SocialApp records for Google, Facebook, and Apple from environment variables.'

    def handle(self, *args, **options):
        site = Site.objects.get_current()

        providers = {
            'google': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'name': 'Google',
            },
            'facebook': {
                'client_id': os.getenv('FACEBOOK_APP_ID'),
                'secret': os.getenv('FACEBOOK_APP_SECRET'),
                'name': 'Facebook',
            },
            'apple': {
                'client_id': os.getenv('APPLE_CLIENT_ID'),
                'secret': os.getenv('APPLE_SECRET'),
                'name': 'Apple',
            },
        }

        for provider, values in providers.items():
            client_id = values.get('client_id')
            secret = values.get('secret')
            if not client_id or not secret:
                self.stdout.write(self.style.WARNING(f'Skipping {provider}: missing env credentials.'))
                continue

            app, created = SocialApp.objects.update_or_create(
                provider=provider,
                defaults={
                    'name': values['name'],
                    'client_id': client_id,
                    'secret': secret,
                    'key': '',
                },
            )
            if app.sites.filter(id=site.id).exists():
                pass
            else:
                app.sites.add(site)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} SocialApp for {provider}"
                )
            )
