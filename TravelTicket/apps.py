from django.apps import AppConfig


class TravelticketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TravelTicket'

    def ready(self):
        print("App TravelTicket ready")

        import TravelTicket.signals          