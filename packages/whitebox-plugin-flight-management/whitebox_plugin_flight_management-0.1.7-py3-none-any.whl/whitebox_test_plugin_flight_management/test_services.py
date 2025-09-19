from contextlib import nullcontext
from unittest.mock import patch
from django.test.testcases import TransactionTestCase

from whitebox_plugin_flight_management.models import FlightSession
from whitebox_plugin_flight_management.services import FlightService


@patch(
    "whitebox_plugin_flight_management.services.FlightService._lock",
    nullcontext,
)
class TestFlightService(TransactionTestCase):
    async def test_current_flight_session(self):
        # GIVEN that on a clean DB, there are no active flight sessions
        initial = await FlightService.get_current_flight_session()
        self.assertIsNone(initial)

        # But then,
        # WHEN you have a flight session active (has no `ended_at` by default)
        created = await FlightSession.objects.acreate()

        # THEN the current flight session should be the one that was created
        current = await FlightService.get_current_flight_session()
        self.assertEqual(current.pk, created.pk)

    async def test_start_flight_session(self):
        initial_count = await FlightSession.objects.acount()

        await FlightService.start_flight_session()

        self.assertEqual(await FlightSession.objects.acount(), initial_count + 1)

    async def test_start_flight_session_when_existing(self):
        # GIVEN that a flight session already exists that is currently in
        #       progress (by default, it won't have `ended_at`)
        await FlightSession.objects.acreate()

        # WHEN trying to start another flight session
        # THEN an error will occur
        with self.assertRaises(ValueError):
            await FlightService.start_flight_session()

    async def test_end_flight_session(self):
        # GIVEN that a flight session was started
        created = await FlightService.start_flight_session()

        # WHEN ending the flight session
        ended = await FlightService.end_flight_session()

        # THEN the flight session should be actually ended in the database
        self.assertEqual(created.pk, ended.pk)
        self.assertTrue(created.is_active)
        await created.arefresh_from_db()
        self.assertFalse(created.is_active)
