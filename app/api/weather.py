from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from requests import Session


class Weather(object):
    def __init__(self, location: tuple[float, float]) -> None:
        self._session = Session()
        self.location = location

    def _get(self, endpoint, **kwargs) -> dict:
        kwargs['params'] = {} | kwargs.get('params', {})
        response = self._session.get(f'https://api.brightsky.dev{endpoint}', **kwargs)
        response.raise_for_status()
        return response.json()

    def current(self, location: tuple[float, float] = None) -> dict:
        lat, lon = location or self.location
        return self._get('/current_weather', params={'lat': lat, 'lon': lon})

    def forecast(
            self, start: datetime | date, end: datetime | date = None, location: tuple[float, float] = None
    ) -> dict:
        start = (
            datetime.combine(start, datetime.min.time(), timezone(datetime.utcnow().astimezone().utcoffset()))
            if isinstance(start, date)
            else start.replace(tzinfo=timezone(datetime.utcnow().astimezone().utcoffset()))
        )
        if end is None:
            end = start + timedelta(hours=1)
        else:
            end = (
                datetime.combine(end, datetime.min.time(), timezone(datetime.utcnow().astimezone().utcoffset()))
                if isinstance(end, date)
                else end.replace(tzinfo=timezone(datetime.utcnow().astimezone().utcoffset()))
            )
        lat, lon = location or self.location
        return self._get(
            '/weather',
            params={'date': start.isoformat(), 'last_date': end.isoformat(), 'lat': lat, 'lon': lon}
        )
