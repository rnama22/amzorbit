class ProductHealthStatus:
    """ Class having HTTP response status codes"""
    OK = 'Ok'
    UNHEALTHY = 'Unhealthy'
    NOT_MONITORED = 'Not Monitored'


class ProductInfoStatus:
    """ Class having HTTP response status codes"""
    IN_PROGRESS = 'In Progress'
    UPDATED = 'Updated'
    PENDING_UPDATE = 'Pending Update'


class Market:
    """ Class having HTTP response status codes"""
    USA = 'USA'
    CANADA = 'Canada'


class Platform:
    """ Class having HTTP response status codes"""
    AMAZON = 'Amazon'


class FEED_TYPE:
    """ Class having HTTP response status codes"""
    ERROR = 'Error'
    INFO = 'Info'
    WARNING = 'Warning'


class FEED_STATUS:
    """ Class having HTTP response status codes"""
    UNREAD = 'Un Read'
    READ = 'Read'
    ARCHIVED = 'Archived'
