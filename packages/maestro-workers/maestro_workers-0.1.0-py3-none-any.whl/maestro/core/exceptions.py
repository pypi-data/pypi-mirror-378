class BaseWorkerError(Exception):
    pass


class IncorrectConfiguring(BaseWorkerError):
    pass


class WorkerStillRunning(BaseWorkerError):
    pass


class ImproperUsage(BaseWorkerError):
    pass


class TaskHaveNotInputToStart(BaseWorkerError):
    pass
