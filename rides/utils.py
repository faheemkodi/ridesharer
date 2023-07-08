from .tasks import update_ride_location


def start_ride_tracking(ride_id):
    update_ride_location.apply_async(args=[ride_id], countdown=3)
    return


def stop_ride_tracking(ride_id):
    update_ride_location.revoke(ride_id, terminate=True)
    return
