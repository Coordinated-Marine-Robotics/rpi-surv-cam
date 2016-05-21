from django.conf import settings

# This context processor gives all loaded templates access to the Dropbox URLs.
# It is needed for the base template, so there is no need to explicitly pass
# these settings from each of the views to templates extending the base template.
def dropbox_urls(request):
    return {
        'DROPBOX_VIDEOS_URL': settings.DROPBOX_VIDEOS_URL,
        'DROPBOX_IMAGES_URL': settings.DROPBOX_IMAGES_URL
    }
