# Ridesharer

> A basic ride-sharing API that allows users to find nearby rides that would take them to their desired location.

> Interactive API documentation is available at http://127.0.0.1:8000/api/schema/swagger

#### Features

- Registered users who are traveling from A to B can create `rides` to invite others to share their ride. Users who creates the `ride` is the `driver`.
- Registered users are matched with nearby `rides` to their desired destinations that are within a 1km proximity of their location.
- Registered users can create `ride_requests` for nearby `rides` (that don't already have a rider).
- Registered `drivers` can accept `ride_requests` and the `ride` will have a fellow `rider`.
- `drivers` and `riders` can update the `status` of a `ride` from `PENDING` to `STARTED`, `COMPLETED` or `CANCELLED`.
- Real-time ride tracking updates the `current_location` of each `ride` every 3 minutes.

#### Notes

- Storing location coordinates is handled with `GeoDjango` and `PostGIS`.
- User authentication is implemented with `dj-rest-auth` and `django-allauth`.
- Scheduling of the location updates is implemented using `Celery` and `Redis`.
