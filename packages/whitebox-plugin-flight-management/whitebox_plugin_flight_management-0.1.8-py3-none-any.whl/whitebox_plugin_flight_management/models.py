from django.db import models
from django.utils import timezone


class FlightSessionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(ended_at__isnull=True)

    def current(self):
        return self.active().first()

    async def acurrent(self):
        return await self.active().afirst()


class FlightSession(models.Model):
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    objects = FlightSessionQuerySet.as_manager()

    @property
    def is_active(self):
        return self.ended_at is None


class FlightSessionRecordingStatus(models.IntegerChoices):
    NOT_READY = 10
    READY = 50


class FlightSessionRecording(models.Model):
    STATUSES = FlightSessionRecordingStatus

    flight_session = models.ForeignKey(
        FlightSession,
        on_delete=models.CASCADE,
        related_name="recordings",
    )

    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField()

    status = models.IntegerField(
        choices=FlightSessionRecordingStatus.choices,
        default=FlightSessionRecordingStatus.NOT_READY,
    )
