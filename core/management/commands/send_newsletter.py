from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from core.models import NewsletterCampaign, NewsletterSubscriber


class Command(BaseCommand):
    help = 'Send promotional newsletter emails to subscribers.'

    def add_arguments(self, parser):
        parser.add_argument('--campaign-id', type=int, help='ID of a saved NewsletterCampaign to send')
        parser.add_argument('--subject', type=str, help='Subject for the promotional email')
        parser.add_argument('--message', type=str, help='Body of the promotional email')
        parser.add_argument('--dry-run', action='store_true', help='Show subscriber count without sending emails')

    def handle(self, *args, **options):
        campaign_id = options.get('campaign_id')
        dry_run = options['dry_run']

        if campaign_id:
            try:
                campaign = NewsletterCampaign.objects.get(pk=campaign_id)
            except NewsletterCampaign.DoesNotExist:
                raise CommandError(f'NewsletterCampaign with id {campaign_id} does not exist.')
            subject = campaign.subject
            message = campaign.body
        else:
            subject = options.get('subject')
            message = options.get('message')
            if not subject or not message:
                raise CommandError('Either --campaign-id or both --subject and --message must be provided.')

        subscribers = list(NewsletterSubscriber.objects.values_list('email', flat=True))
        if not subscribers:
            self.stdout.write(self.style.WARNING('No newsletter subscribers found.'))
            return

        self.stdout.write(f'Found {len(subscribers)} subscriber(s).')
        if dry_run:
            self.stdout.write(self.style.SUCCESS('Dry run complete. No emails sent.'))
            return

        from_email = settings.DEFAULT_FROM_EMAIL or 'webmaster@localhost'
        for email in subscribers:
            send_mail(subject, message, from_email, [email], fail_silently=False)

        if campaign_id:
            campaign.sent = True
            campaign.sent_date = timezone.now()
            campaign.save(update_fields=['sent', 'sent_date'])

        self.stdout.write(self.style.SUCCESS(f'Successfully sent newsletter to {len(subscribers)} subscriber(s).'))
