class PublisherOptions:
    class Selector:
        CREATE = "create"
        READ = "read"
        READ_FILTER = "readfilter"
        UPDATE = "update"
        DELETE = "delete"
        SUBSCRIBE = "subscribe"

    create: bool = False
    read: bool = True
    read_filter: bool = False
    update: bool = False
    delete: bool = False
    subscribe: bool = False

    def __init__(
        self,
        create=False,
        read=False,
        readfilter=False,
        update=False,
        delete=False,
        subscribe=False,
    ) -> None:
        self.create = create
        self.read = read
        self.readfilter = readfilter
        self.update = update
        self.delete = delete
        self.subscribe = subscribe
