from django.contrib import admin
from .models import Contact, NewsletterCampaign, NewsletterSubscriber, InstagramPost, SiteSettings, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'active')


@admin.register(InstagramPost)
class InstagramAdmin(admin.ModelAdmin):
    list_display = ('caption', 'order', 'active')


@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'created')


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'scheduled_send', 'sent', 'sent_date', 'created')
    list_filter = ('sent',)
    search_fields = ('subject', 'body')
    actions = ['send_selected_campaigns']

    def send_selected_campaigns(self, request, queryset):
        total_sent = 0
        for campaign in queryset:
            if not campaign.sent:
                sent_count = campaign.send()
                total_sent += sent_count
        self.message_user(request, f'Sent {total_sent} emails for selected campaign(s).')
    send_selected_campaigns.short_description = 'Send selected newsletter campaigns'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'updated')
    readonly_fields = ('updated',)
    search_fields = ('site_name', 'contact_email')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'handled', 'created')
    list_filter = ('handled', 'created')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created',)
