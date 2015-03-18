from django.dispatch import receiver
from django.db.models.signals import post_save
from bowling_entry import models as bowling_models


@receiver(post_save, sender=bowling_models.League)
def update_weeks(sender, **kwargs):
    league = kwargs['instance']
    league.update_weeks()