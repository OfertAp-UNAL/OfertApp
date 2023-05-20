from django.apps import AppConfig

class PublicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'publications'

    # So this code will be executed once
    def ready(self):

        # IMPORTANT: Seems like you'll have to comment this code, run
        # django_scheduler migrations (normal migrate command) and then
        # uncomment this code again and run the server
        # from scheduler import scheduler
        # scheduler.start()
        pass