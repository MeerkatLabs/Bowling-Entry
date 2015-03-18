from django.apps import AppConfig


class BowlingEntryApp(AppConfig):
    name = 'bowling_entry'
    verbose_name = 'Bowling Entry'

    def ready(self):
        """
        This is where the signals go.
        :return:
        """

        # Register all of the signal handlers.
        import bowling_entry.signals.handlers