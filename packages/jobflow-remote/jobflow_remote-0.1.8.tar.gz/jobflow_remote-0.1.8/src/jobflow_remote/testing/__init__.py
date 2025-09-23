"""A series of toy workflows that can be used for testing."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, NoReturn, Optional, Union

from jobflow import Job, JobConfig, Maker, OnMissing, Response, job


@job
def add(a, b):
    """Adds two numbers together and writes the answer to a file."""
    return a + b


@job
def always_fails() -> NoReturn:
    """A job that always fails."""
    raise RuntimeError("This job failed.")


@job
def write_file(n) -> None:
    with open("results.txt", "w") as f:
        f.write(str(n))


@job
def arithmetic(
    a: Union[float, list[float]],
    b: Union[float, list[float]],
    op: Optional[Callable] = None,
) -> Optional[float]:
    if op:
        return op(a, b)

    return None


@job
def check_env_var() -> str:
    import os

    return os.environ.get("TESTING_ENV_VAR", "unset")


@job(big_data="data")
def add_big(a: float, b: float):
    """Adds two numbers together and inflates the answer
    to a large list and tries to store that within
    the defined store.
    """
    result = a + b
    big_array = [result] * 5_000
    return Response({"data": big_array, "result": a + b})


@job(undefined_store="data")
def add_big_undefined_store(a: float, b: float):
    """Adds two numbers together and writes the answer to an artificially large file
    which is attempted to be stored in a undefined store.
    """
    result = a + b
    return Response({"data": [result] * 5_000, "result": result})


@job
def add_sleep(a, b):
    """Adds two numbers together and sleeps for "b" seconds."""
    import time

    time.sleep(b)
    return a + b


@job
def create_detour(detour_job: Job):
    """Create a detour based on the passed Job."""
    from jobflow import Flow

    return Response(detour=Flow(detour_job))


@job
def self_replace(n: int):
    """Create a replace Job with the same job n times."""
    if n > 0:
        return Response(replace=self_replace(n - 1))

    return n


@job
def ignore_input(a: int) -> int:
    """
    Can receive an input, but ignores it.

    Allows to test flows with failed parents
    """
    return 1


@job
def current_jobdoc():
    from jobflow_remote.jobs.run import CURRENT_JOBDOC

    return CURRENT_JOBDOC.job_doc


@job(config=JobConfig(resolve_references=False, on_missing_references=OnMissing.NONE))
def no_resolve(ref):
    """
    A job that does not resolve the reference in input
    """
    return ref


@job
def replace_and_stop_jobflow(a=1, b=1) -> Response[None]:
    from jobflow import Flow

    j1 = add(a, b)
    j2 = add(j1.output, 1)
    flow = Flow([j1, j2], output=j2.output)
    return Response(replace=flow, stop_jobflow=True)
    # return Response(replace=flow)


@job
def replace_and_stop_children(a: int = 1, b: int = 1) -> Response[None]:
    from jobflow import Flow

    j1 = add(a, b)
    j2 = add(j1.output, 1)
    flow = Flow([j1, j2], output=j2.output)
    return Response(replace=flow, stop_children=True)


@job
def stop_jobflow(x=None) -> Response[None]:
    return Response(stop_jobflow=True)


class TestEnum(Enum):
    A = "A"
    B = "B"


@dataclass
class EnumMaker(Maker):
    e: TestEnum = TestEnum.A
    name: str = "enum maker"

    @job
    def make(self):
        assert isinstance(self.e, TestEnum)
