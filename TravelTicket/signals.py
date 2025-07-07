import datetime
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from TravelTicket.models import Date
print("create_dates_for_year")
@receiver(post_migrate)
def create_dates_for_year(sender, **kwargs):
    if sender.name != "TravelTicket":
        return

    year = datetime.date.today().year
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    print("create_dates_for_year", year)

    current = start
    created_count = 0
    while current <= end:
        obj, created = Date.objects.get_or_create(date=current)
        if created:
            created_count += 1
        current += datetime.timedelta(days=1)

    print(f"✔ {created_count} dates créées pour l'année {year}")