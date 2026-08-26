from storages.backends.s3 import S3Storage


class TicketStorage(S3Storage):
    location = "tickets"
    default_acl = None
    file_overwrite = False