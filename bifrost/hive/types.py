import graphene


class GenerationTypes:
    class HiveState(graphene.Enum):
        PENDING = "PENDING"
        STARTED = "STARTED"
        RETRY = "RETRY"
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"
