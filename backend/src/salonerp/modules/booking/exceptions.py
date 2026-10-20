class BookingError(Exception):
    pass


class SlotTakenError(BookingError):
    pass



class ServiceNotFoundError(BookingError):
    pass


class AppointmentNotFound(BookingError):
    pass


