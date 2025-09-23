from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from zoneinfo import ZoneInfo

from monty.dev import requires

try:
    import fasthtml
    from fasthtml.common import (
        H1,
        H3,
        H4,
        A,
        Button,
        Card,
        CheckboxX,
        Dialog,
        Div,
        Favicon,
        Form,
        Group,
        Img,
        Input,
        Label,
        Li,
        Link,
        Main,
        Option,
        P,
        Script,
        Select,
        Span,
        Table,
        Td,
        Th,
        Title,
        Tr,
        Ul,
        fast_app,
        serve,
    )
except ImportError:
    fasthtml = None

    # fake rt decorator
    def rt_fake(*args, **kwargs):
        def wrapper(func):
            return func

        return wrapper

    def fast_app(*args, **kwargs):
        return lambda x: x, rt_fake

    def fake_function(*args, **kwargs):
        return None

    Title = Link = Script = Favicon = fake_function


from jobflow_remote import ConfigManager
from jobflow_remote.jobs.daemon import DaemonManager, DaemonStatus
from jobflow_remote.jobs.graph import get_mermaid
from jobflow_remote.jobs.jobcontroller import JobController
from jobflow_remote.jobs.report import JobsReport
from jobflow_remote.jobs.state import JobState

id_curr = "current-info"
id_list = "info-list"


PAGE_TITLE = Title("Jobflow remote manager")

mermaid_js = """
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({ startOnLoad: false });
window.mermaid = mermaid;
"""


def error_handler(req, exc):
    error_message = f"{exc}"
    return Dialog(
        Div(
            H3("An error occurred:"),
            P(f"{error_message}"),
            Button(
                "Cancel",
                hx_get="/test/close_dialog",
                hx_target="#dialog-container",
                style="font-weight: bold",
            ),
            cls="card-dialog",
        ),
        id="my-dialog",
        open="open",  # This attribute opens the dialog
        cls="dialog",
    )


exception_handlers = {500: error_handler}

app, rt = fast_app(
    pico=False,  # Disable Pico CSS to use custom styles
    hdrs=(
        Link(rel="stylesheet", href="./style.css", type="text/css"),
        Script(mermaid_js, type="module"),
        Favicon("jfr_favicon.ico", "jfr_favicon.ico"),
    ),  # Add custom CSS as a header
    exception_handlers=exception_handlers,
    static_path=Path(__file__).parent,
)


# javascript
js_timezone = """
document.getElementById('timezone_in').value = Intl.DateTimeFormat().resolvedOptions().timeZone;
"""

# change color on click
js_set_color = """
  function setActiveLink(clickedLink) {
    // Remove active class from all links
    document.querySelectorAll('.navbar-link').forEach(link => {
      link.classList.remove('active');
    });

    // Add active class to clicked link
    clickedLink.classList.add('active');
  }
"""

start_stop_btn_lbl = {
    "RUNNING": "Stop",
    "SHUT_DOWN": "Start",
    "STOPPED": "Start",
}

status_colors = {
    DaemonStatus.STOPPED: "red",
    DaemonStatus.STOPPING: "aqua",
    DaemonStatus.SHUT_DOWN: "red",
    DaemonStatus.PARTIALLY_RUNNING: "lawngreen",
    DaemonStatus.STARTING: "aqua",
    DaemonStatus.RUNNING: "limegreen",
}

cm = ConfigManager()

list_projects = list(cm.projects.keys())

job_controllers = {}
daemon_managers = {}
job_controller = None
job_controller_actions = None
daemon_manager = None


def set_job_controller_deamon(project_name):
    global job_controller, job_controller_actions, daemon_manager  # # noqa: PLW0603

    if project_name not in job_controllers:
        job_controllers[project_name] = JobController.from_project_name(
            project_name=project_name
        )
        daemon_managers[project_name] = DaemonManager.from_project(
            cm.get_project(project_name)
        )

    daemon_manager = daemon_managers[project_name]
    job_controller = job_controllers[project_name]
    job_controller_actions = {
        "jobs": {
            "Resume": job_controller.resume_jobs,
            "Pause": job_controller.pause_jobs,
            "Stop": job_controller.stop_jobs,
            "Retry": job_controller.retry_jobs,
            "Rerun": job_controller.rerun_jobs,
        },
        "flows": {
            "Delete": job_controller.delete_flows,
        },
    }


jfreport = None


def update_jfreport(interval: str = "days", ni: int = 7):
    global jfreport  # noqa: PLW0603

    jfreport = JobsReport().generate_report(
        job_controller, interval=interval, num_intervals=ni
    )


# Navigation bar component
def projectbar(proj_name: str = "", what: str = ""):
    if proj_name:
        status, color = get_runner_status(proj_name)
    return Div(
        Script(js_set_color),
        Ul(
            A(Img(src="./logo_jfr.png", height=50), href="/"),
            Li("Projects:"),
            Li(
                Select(
                    Option("Pick one"),
                    *[
                        Option(prj, value=prj, selected=(proj_name == prj))
                        for prj in list_projects
                    ],
                    name="proj_name",
                    hx_push_url="true",
                    hx_get="/projects",
                    hx_target="body",
                )
            ),
            (
                Li(
                    A(
                        "Report",
                        hx_get=f"/projects?proj_name={proj_name}",
                        hx_push_url="true",
                        hx_target="body",
                        # _="on click remove .active from .navbar a then add .active to me",
                        onclick="setActiveLink(this)",
                        cls="navbar-link",
                    )
                ),
                Group(
                    Ul(
                        Li("Query: "),
                        Li(
                            A(
                                "Jobs",
                                hx_get=f"/{proj_name}/jobs/query",
                                hx_target="#prj-container",
                                hx_push_url="true",
                                # _="on click remove .active from .navbar a then add .active to me",
                                onclick="setActiveLink(this)",
                                cls="navbar-link",
                            )
                        ),
                        Li(
                            A(
                                "Flows",
                                hx_get=f"/{proj_name}/flows/query",
                                hx_target="#prj-container",
                                hx_push_url="true",
                                # _="on click remove .active from .navbar a then add .active to me",
                                onclick="setActiveLink(this)",
                                cls="navbar-link",
                            )
                        ),
                    ),
                    cls="group",
                ),
                Group(
                    Ul(
                        Li("Runner:"),
                        Li(
                            f"{status}",
                            style=f"color: {color}; background-color: black; padding: 3px 5px; border-radius: 4px;",
                        ),
                        Li(
                            Button(
                                f"{start_stop_btn_lbl[status]}",
                                hx_post=f"/runner/{proj_name}/{start_stop_btn_lbl[status].lower()}",
                                hx_target="#runner-status",
                            )
                        ),
                    ),
                    hx_get=f"/runner/{proj_name}/status",
                    hx_trigger="every 30s",
                    hx_swap="outerHTML",
                    id="runner-status",
                    cls="group",
                ),
            )
            if proj_name
            else None,
        ),
        cls="navbar",
    )


def ScrollableArea(*content, height="300px"):
    return Div(
        *content,
        style=f"height: {height}; overflow-y: auto; border: 1px solid #ccc; padding: 10px;",
    )


@rt("/")
def get_home():
    return PAGE_TITLE, Main(
        projectbar(),
        Div(
            H4(
                "Select project from the navigation bar above to view and query Jobs and Flows."
            ),
            P("Add here some general information, e.g. the list of available projects"),
            cls="container",
            id="prj-container",
        ),
        id="page",
    )


@rt("/actions/{action}/{what}/open_dialog", methods=["POST"])
def open_dialog(action: str, what: str, kwargs: dict):
    selected = [f"{v}" for k, v in kwargs.items()]

    # Add checkboxes for delete_flow options
    delete_options = ""
    if action == "Delete" and what == "flows":
        delete_options = Div(
            CheckboxX(
                id="delete_output",
                name="delete_options",
                value="delete_output",
                label="Delete Output",
            ),
            CheckboxX(
                id="delete_files",
                name="delete_options",
                value="delete_files",
                label="Delete Files",
            ),
        )

    return Dialog(
        Div(
            H3(f"Action Selected: {action}"),
            P(f"{what} selected:"),
            P(", ".join(selected) if selected else "No options selected"),
            P("Options:"),
            delete_options,
            Button(
                "Cancel",
                hx_get="/test/close_dialog",
                hx_target="#dialog-container",
                style="",
            ),
            Button(
                "Confirm",
                hx_post=f"/actions/{action}/{what}/run",
                hx_include="[name='ckbx_action'],[name='delete_options']",
                hx_target="#dialog-container",
                hx_swap="innerHTML",
                style="font-weight: bold",
            )
            if selected
            else None,
            cls="card-dialog",
        ),
        id="my-dialog",
        open="open",  # This attribute opens the dialog
        cls="dialog",
    )


@rt("/actions/{action}/{what}/run", methods=["POST"])
def run_action(action: str, what: str, kwargs: dict):
    selected = [v for k, v in kwargs.items() if k != "delete_options"]
    delete_options = kwargs.get("delete_options", [])

    if action == "Delete" and what == "flows":
        delete_output = "delete_output" in delete_options
        delete_files = "delete_files" in delete_options
        response = job_controller_actions[what][action](
            selected, delete_output=delete_output, delete_files=delete_files
        )
    else:
        response = job_controller_actions[what][action](db_ids=selected)

    return Dialog(
        Div(
            H3(f"Action Selected: {action}"),
            P(f"Applied on {response} {what}"),
            P(f"{delete_options}"),
            Button(
                "Cancel",
                hx_get="/test/close_dialog",
                hx_target="#dialog-container",
                style="font-weight: bold",
            ),
            cls="card-dialog",
        ),
        id="my-dialog",
        open="open",  # This attribute opens the dialog
        cls="dialog",
    )


@rt("/test/close_dialog")
def close_dialog():
    return ""


# handle starting and stopping the runner
@rt("/runner/{proj_name}/start", methods=["POST"])
def start_runner_route(proj_name: str):
    dm = daemon_managers[proj_name]
    dm.start()
    status = "STARTING"
    color = status_colors[DaemonStatus(status)]
    return Group(
        Ul(
            Li("Runner:"),
            Li(
                status,
                style=f"color: {color}; background-color: black; padding-right: 10px; border-radius: 4px;",
            ),
        ),
        id="runner-status",
        hx_get=f"/runner/{proj_name}/status",
        hx_trigger="every 5s",
        hx_swap="outerHTML",
        cls="group",
    )


@rt("/runner/{proj_name}/stop", methods=["POST"])
def stop_runner_route(proj_name: str):
    dm = daemon_managers[proj_name]
    dm.shut_down()
    status = "STOPPING"
    color = status_colors[DaemonStatus(status)]
    return Group(
        Ul(
            Li("Runner:"),
            Li(
                status,
                style=f"color: {color}; background-color: black; padding-right: 10px; border-radius: 4px;",
            ),
        ),
        id="runner-status",
        hx_get=f"/runner/{proj_name}/status",
        hx_trigger="every 5s",
        hx_swap="outerHTML",
        cls="group",
    )


@rt("/runner/{proj_name}/status")
def get_runner_status_update(proj_name: str):
    status, color = get_runner_status(proj_name)
    return Group(
        Ul(
            Li("Runner:"),
            Li(
                f"{status}",
                style=f"color: {color}; background-color: black; padding-right: 10px; border-radius: 4px;",
            ),
            Li(
                Button(
                    f"{start_stop_btn_lbl[status]}",
                    hx_post=f"/runner/{proj_name}/{start_stop_btn_lbl[status].lower()}",
                    hx_target="#runner-status",
                )
            ),
        ),
        hx_get=f"/runner/{proj_name}/status",
        hx_trigger="every 30s",
        hx_swap="outerHTML",
        id="runner-status",
        cls="group",
    )


def get_runner_status(proj_name: str):
    dm = daemon_managers[proj_name]
    current_status = dm.check_status()
    color = status_colors[current_status]

    return current_status.name, color


@rt("/projects")
def get_proj_home(proj_name: str = ""):
    if proj_name not in list_projects:
        return PAGE_TITLE, Main(
            projectbar(),
            Div(
                H1(f"The project: {proj_name} does not exists"),
                P("Select an available project from the navigation bar above."),
                id="prj-container",
            ),
        )

    set_job_controller_deamon(proj_name)

    if jfreport:
        interval = jfreport.trends.interval
        ni = jfreport.trends.num_intervals
    else:
        interval = "days"
        ni = 7

    return PAGE_TITLE, Main(
        Script(mermaid_js, type="module"),
        projectbar(proj_name),
        Div(
            H3(f"Report for the Project: {proj_name}"),
            P("Description of the project"),
            Div(
                H3("Jobs Report"),
                Ul(
                    Li(
                        Button(
                            "Summary Jobs Report",
                            hx_get=f"/{proj_name}/jobs/sum_report",
                            hx_target="#jobs-report",
                        )
                    ),
                    Li(
                        Button(
                            "Jobs State Distribution",
                            hx_get=f"/{proj_name}/jobs/state_distro",
                            hx_target="#jobs-report",
                        )
                    ),
                    Li(
                        Form(
                            Button(
                                "Jobs Trend for the last",
                                hx_post=f"/{proj_name}/jobs/trends/",
                                hx_include="[name='interval'],[name='ni']",
                                hx_target="#jobs-report",
                            ),
                            Select(
                                *[
                                    Option(i, selected=i == interval)
                                    for i in ("days", "hours", "months", "years")
                                ],
                                name="interval",
                            ),
                            Input(type="number", value=ni, name="ni"),
                        )
                    ),
                ),
                Div(id="jobs-report"),
                id="buttons-jobs-report",
                cls="card",
            ),
            Div(
                H3("Flows Report"),
                Ul(
                    Li(
                        Button(
                            "Summary Flows Report",
                            hx_get=f"/{proj_name}/flows/sum_report",
                            hx_target="#flows-report",
                        )
                    ),
                    Li(
                        Button(
                            "Flows State Distribution",
                            hx_get=f"/{proj_name}/flows/state_distro",
                            hx_target="#flows-report",
                        )
                    ),
                    Li(
                        Form(
                            Button(
                                "Flows Trend for the last",
                                hx_post=f"/{proj_name}/flows/trends/",
                                hx_include="[name='interval'],[name='ni']",
                                hx_target="#flows-report",
                            ),
                            Select(
                                *[
                                    Option(i, selected=i == interval)
                                    for i in ("days", "hours", "months", "years")
                                ],
                                name="interval",
                            ),
                            Input(type="number", value=ni, name="ni"),
                        )
                    ),
                ),
                Div(id="flows-report"),
                id="buttons-flows-report",
                cls="card",
            ),
            id="prj-container",
        ),
    )


@rt("/{proj_name}/{what}/sum_report")
def sum_report(proj_name: str, what: str):
    if not jfreport:
        update_jfreport()

    state_counts = Counter(jfreport.state_counts)

    # Find the most common state
    most_common_state, most_common_count = state_counts.most_common(1)[0]

    running_count = jfreport.running
    completed_count = jfreport.completed
    error_count = jfreport.error
    active_count = jfreport.active

    # Calculate percentages
    total_jobs = state_counts.total()
    state_percentages = {
        state: (count / total_jobs) * 100 for state, count in state_counts.items()
    }

    # Create the report
    report = Div(
        Button(
            "Update",
            hx_get=f"/{proj_name}/{what}/sum_report",
            hx_target=f"#{what}-report",
        ),
        Table(
            Tr(Td(f"Total number of {what}:"), Td(f"{total_jobs}")),
            Tr(
                Td("Most common state:"),
                Td(
                    f"{most_common_state.name} ({most_common_count} {what}, {state_percentages[most_common_state]:.2f}%)"
                ),
            ),
            Tr(Td(f"Running {what}:"), Td(f"{running_count}")),
            Tr(Td(f"Completed {what}:"), Td(f"{completed_count}")),
            Tr(
                Td(f"Sum of failed, remote error, and paused {what}:"),
                Td(f"{error_count}"),
            ),
            Tr(Td(f"Sum of all active {what}:"), Td(f"{active_count}")),
            Tr(Td("Longest running:"), Td(f"{jfreport.longest_running}")),
            Tr(Td("Worker utilization:"), Td(f"{jfreport.worker_utilization}")),
        ),
        cls="job-state-report",
    )

    return Div(report, cls="container")


@rt("/{proj_name}/{what}/trends/", methods=["POST"])
def trends(proj_name: str, what: str, interval: str = "days", ni: int = 7):
    if not jfreport:
        update_jfreport()

    if jfreport.trends.interval != interval or jfreport.trends.num_intervals != ni:
        update_jfreport(interval, ni)

    # trends table
    trend_table = Table(
        Tr(Th("Dates"), Th("Completed"), Th("Failed"), Th("Remote error")),
        *[
            Tr(Td(d), Td(c), Td(f), Td(r))
            for d, c, f, r in zip(
                jfreport.trends.dates,
                jfreport.trends.completed,
                jfreport.trends.failed,
                jfreport.trends.remote_error,
            )
        ],
        cls="trend-table",
    )

    report = Div(
        H3(f"{what.capitalize()} Trend Table:"), trend_table, cls="job-state-report"
    )

    return Div(report, cls="container")


@rt("/{proj_name}/{what}/state_distro")
def state_distro(proj_name: str, what: str):
    if not jfreport:
        update_jfreport()

    state_counts = Counter(jfreport.state_counts)

    # Calculate percentages
    total_jobs = state_counts.total()
    state_percentages = {
        state: (count / total_jobs) * 100 for state, count in state_counts.items()
    }

    # Create the report
    report = Div(
        Table(
            Tr(Th("State"), Th("Count"), Th("Percentage")),
            *[
                Tr(
                    Td(state.name),
                    Td(str(count)),
                    Td(f"{state_percentages[state]:.2f}%"),
                )
                for state, count in state_counts.items()
            ],
            cls="state-distribution-table",
        ),
        cls="job-state-report",
    )
    return Div(
        Button(
            "Update",
            hx_get=f"/{proj_name}/{what}/state_distro",
            hx_target=f"#{what}-report",
        ),
        report,
        cls="container",
    )


@rt("/{proj_name}/{what}/info/{jf_id}")
def get_info_job_flow(jf_id: str, what: str, proj_name: str):
    info = None

    if what == "jobs":
        info = job_controller.get_job_info(db_id=jf_id).dict()
    elif what == "flows":
        info = job_controller.get_flow_info_by_flow_uuid(jf_id)

    if info:
        return Div(
            H3(f"Job {jf_id} details"),
            H3(f"Job name: {info.pop('name')}"),
            ScrollableArea(
                *[
                    Ul(
                        Li(f"{k}:", style="font-weight: bold"),
                        Li(f"{v}", style="margin-left: 10px; al"),
                    )
                    for k, v in info.items()
                ]
            ),
            cls="card-dialog active",
        )

    return P("Job not found")


@rt("/{proj_name}/flows/graph/{jf_id}")
def get_graph_job_flow(jf_id: str, proj_name: str):
    flowinfo = job_controller.get_flows_info(limit=1, full=True)[0]
    graph = get_mermaid(flowinfo)
    m_script = f"""
(async function() {{
    const container = document.getElementById('flow-graph');
    const {{ svg }} = await window.mermaid.render('graphDiv', `{graph}`);
    container.innerHTML = svg;
}})();
"""
    return Div(
        ScrollableArea(Div(id="flow-graph"), Script(m_script)), cls="card-dialog"
    )


@rt("/{proj_name}/{what}/dialog/{jf_id}")
def get_info_graph_dialog(jf_id: str, what: str, proj_name: str):
    return Dialog(
        Card(
            Button(
                "Close",
                hx_get="/test/close_dialog",
                hx_target="#dialog-container",
                style="float: right; font-weight: bold",
                cls="btn",
            ),
            Div(
                Button(
                    f"Details {what}",
                    cls="tab active",
                    hx_get=f"/{proj_name}/{what}/info/{jf_id}",
                    hx_target="#tab-content",
                    hx_swap="innerHTML",
                    _="on click remove .active from .tab then add .active to me",
                ),
                Button(
                    "Graph Flow",
                    cls="tab",
                    hx_get=f"/{proj_name}/flows/graph/{jf_id}",
                    hx_target="#tab-content",
                    hx_swap="innerHTML",
                    _="on click remove .active from .tab then add .active to me",
                ),
                cls="tab-buttons btn",
            )
            if what == "flows"
            else None,
            Div(
                get_info_job_flow(jf_id, what, proj_name),
                id="tab-content",
                cls="tab-content",
            ),
            cls="tabbed-card",
        ),
        id="my-dialog",
        open="open",
        cls="dialog",
    )


@rt("/{proj_name}/{what}/close_info")
def close_info():
    return ""


@rt("/{proj_name}/{what}/query")
def get(proj_name: str, what: str):
    form = Form(
        Group(
            Input(name="db_id", placeholder="DB ID")
            if what == "jobs"
            else Input(name="flow_id", placeholder="Flow ID"),
            Input(name="uuid", placeholder="UUID") if what == "jobs" else None,
            Input(name="name", placeholder="Job Name"),
            cls="group",
        ),
        Group(
            Label("State"),
            Select(
                Option("Any", value=""),
                *[Option(state.name, value=state.value) for state in JobState],
                name="state",
                id="select-job-state",
            ),
            Input(name="worker", placeholder="Worker") if what == "jobs" else None,
            cls="group",
        ),
        # Date and time for start and end time
        Group(
            Label("Start Date/Time"),
            Input(type="date", name="start_date"),
            Input(type="time", name="start_time", label="Start Time"),
            Label("End Date/Time"),
            Input(type="date", name="end_date", label="End Date"),
            Input(type="time", name="end_time", label="End Time"),
            cls="group",
        ),
        # Input for entries per page
        Group(
            Label("Entries per page"),
            Select(
                *[
                    Option(str(i), value=str(i), selected=(i == 20))
                    for i in (10, 20, 50, 100)
                ],
                name="entries_per_page",
                id="select-npages",
            ),
            cls="group",
        ),
        # Hidden input to store the user's timezone (populated by JavaScript)
        Input(type="hidden", name="timezone_in", value="", id="timezone_in"),
        Input(type="hidden", name="sort_by", value="updated_on"),
        Input(type="hidden", name="sort_order", value="-1"),
        Button("Search", cls="btn"),
        Script(js_timezone),
        Script(mermaid_js, type="module"),
        hx_post=f"/{proj_name}/{what}/query",
        hx_target="#query-results",
        cls="card",
        id="search-form",
    )

    if what == "jobs":
        total_entries = job_controller.count_jobs()
    elif what == "flows":
        total_entries = job_controller.count_flows()

    return Div(
        H3(f"{what.capitalize()} Query"),
        H3(f"Total number of {what}: {total_entries}"),
        form,
        Div(id="query-results"),
        id="prj-container",
    )


@rt("/{proj_name}/{what}/query")
def post(
    proj_name: str,
    what: str,
    db_id: str = "",
    uuid: str = "",
    name: str = "",
    state: str = "",
    worker: str = "",
    start_date: str = "",
    start_time: str = "",
    end_date: str = "",
    end_time: str = "",
    max_results: int = 100,
    timezone_in: str = "",
    sort_by: str = "updated_on",
    sort_order: int = -1,
    page: int = 1,
    entries_per_page: int = 10,
):
    query: dict[
        str,
        str
        | list[str]
        | tuple[str, None]
        | list[tuple[str, None]]
        | None
        | JobState
        | dict[str, str]
        | datetime,
    ] = {}
    if db_id:
        query["db_ids"] = [db_id]
    if uuid:
        query["job_ids"] = [(uuid, None)]
    if name:
        query["name"] = name
    if state:
        query["states"] = None if state == "Any" else JobState(state)
    if worker:
        query["metadata"] = {"worker": worker}

    if timezone_in:
        tz = ZoneInfo(timezone_in)
    else:
        # TODO this should be fixed
        # tz = ZoneInfo(datetime.now(timezone.utc).astimezone().tzname())
        raise NotImplementedError

    if start_time and not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    if start_date:
        if start_time:
            start_date = f"{start_date} {start_time}"
            query["start_date"] = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        else:
            query["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")

    if end_time and not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if end_date:
        if end_time:
            end_date = f"{end_date} {end_time}"
            query["end_date"] = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        else:
            query["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")

    skip = (page - 1) * entries_per_page

    if what == "jobs":
        jobs_flows = job_controller.get_jobs_info(
            **query, sort=[[sort_by, sort_order]], limit=entries_per_page, skip=skip
        )
    elif what == "flows":
        jobs_flows = job_controller.get_flows_info(
            **query, sort=[[sort_by, sort_order]], limit=entries_per_page, skip=skip
        )

    if not jobs_flows:
        return Div(P("No jobs found matching the criteria."), cls="card")

    # Toggle sort direction for next click
    next_sort_order = -sort_order

    # prepare all entries
    all_entries = list(jobs_flows)

    # prepare table
    info_table = Table(
        Tr(
            Th(
                A(
                    "DB id",
                    hx_post=f"/{proj_name}/{what}/query",
                    hx_include="previous form",
                    hx_vals=f'{{"sort_by":"db_id", "sort_order":"{next_sort_order if sort_by == "db_id" else 1}"}}',
                    hx_swap="innerHTML",
                    hx_target="#query-results",
                )
            )
            if what == "jobs"
            else None,
            Th(
                A(
                    "UUID",
                    hx_post=f"/{proj_name}/{what}/query",
                    hx_include="previous form",
                    hx_vals=f'{{"sort_by":"uuid", "sort_order":"{next_sort_order if sort_by == "uuid" else 1}"}}',
                    hx_swap="innerHTML",
                    hx_target="#query-results",
                )
            ),
            Th(
                A(
                    "Name",
                    hx_post=f"/{proj_name}/{what}/query",
                    hx_include="previous form",
                    hx_vals=f'{{"sort_by":"job.name", "sort_order":"{next_sort_order if sort_by == "job.name" else 1}"}}',
                    hx_swap="innerHTML",
                    hx_target="#query-results",
                )
            ),
            Th(
                A(
                    "State",
                    hx_post=f"/{proj_name}/{what}/query",
                    hx_include="previous form",
                    hx_vals=f'{{"sort_by":"state", "sort_order":"{next_sort_order if sort_by == "state" else 1}"}}',
                    hx_swap="innerHTML",
                    hx_target="#query-results",
                )
            ),
            Th(
                A(
                    "Worker",
                    hx_post=f"/{proj_name}/{what}/query",
                    hx_include="previous form",
                    hx_vals=f'{{"sort_by":"worker", "sort_order":"{next_sort_order if sort_by == "worker" else 1}"}}',
                    hx_swap="innerHTML",
                    hx_target="#query-results",
                )
            )
            if what == "jobs"
            else None,
            Th(
                A(
                    "Updated",
                    hx_post=f"/{proj_name}/{what}/query",
                    hx_include="previous form",
                    hx_vals=f'{{"sort_by":"updated_on", "sort_order":"{next_sort_order if sort_by == "updated_on" else 1}"}}',
                    hx_swap="innerHTML",
                    hx_target="#query-results",
                )
            ),
            Th(
                Label("Action", Input(type="checkbox", onclick="toggleAll(this)")),
                style="text-align: right",
            ),
        ),
        *[
            Tr(
                Td(
                    A(
                        entry.db_id,
                        hx_get=f"/{proj_name}/{what}/dialog/{entry.db_id}",
                        hx_target="#dialog-container",
                        hx_swap="innerHTML",
                    )
                )
                if what == "jobs"
                else None,
                Td(entry.uuid)
                if what == "jobs"
                else Td(
                    A(
                        entry.flow_id,
                        hx_get=f"/{proj_name}/{what}/dialog/{entry.flow_id}",
                        hx_target="#dialog-container",
                        hx_swap="innerHTML",
                    )
                ),
                Td(entry.name),
                Td(entry.state.value),
                Td(entry.worker) if what == "jobs" else None,
                Td(
                    entry.updated_on.replace(tzinfo=timezone.utc)
                    .astimezone(tz)
                    .strftime("%Y-%m-%d %H:%M:%S")
                ),
                Td(
                    Input(
                        type="checkbox",
                        name="ckbx_action",
                        value=f"{entry.db_id if what=='jobs' else entry.flow_id}",
                        id=f"{entry.db_id if what=='jobs' else entry.flow_id}",
                    ),
                    style="text-align: right",
                ),
                style="background-color: #f5f5f5;" if i % 2 == 0 else "",
            )
            for i, entry in enumerate(all_entries)
        ],
        cls="card",
    )

    if what == "jobs":
        total_entries = job_controller.count_jobs(**query)
    elif what == "flows":
        total_entries = job_controller.count_flows(**query)

    total_pages = ceil(total_entries / entries_per_page)

    if what == "jobs":
        # all_job_flow_ids = [entry.db_id for entry in all_entries]
        action_btns_lbl = ("Rerun", "Play", "Pause", "Stop", "Retry")
    elif what == "flows":
        # all_job_flow_ids = [entry.flow_id for entry in all_entries]
        action_btns_lbl = ("Delete",)  # type: ignore[assignment]

    action_btns = Group(
        Label("Actions:   "),
        *[
            Button(
                name,
                hx_post=f"/actions/{name}/{what}/open_dialog",
                hx_target="#dialog-container",
                hx_include="[name='ckbx_action']",
                cls="btn",
            )
            for name in action_btns_lbl
        ],
        style="float: right",
        cls="group",
    )

    pagination = Div(
        A(
            "Previous",
            hx_post=f"/{proj_name}/{what}/query",
            hx_include="previous form",
            hx_vals=f'{{"page":{page-1}}}',
            hx_swap="innerHTML",
            hx_target="#query-results",
        )
        if page > 1
        else Span("Previous"),
        *[
            A(
                str(i),
                hx_post=f"/{proj_name}/{what}/query",
                hx_include="previous form",
                hx_vals=f'{{"page":{i}}}',
                hx_swap="innerHTML",
                hx_target="#query-results",
            )
            for i in range(max(1, page - 2), min(total_pages + 1, page + 3))
        ],
        A(
            "Next",
            hx_post=f"/{proj_name}/{what}/query",
            hx_include="previous form",
            hx_vals=f'{{"page":{page+1}}}',
            hx_swap="innerHTML",
            hx_target="#query-results",
        )
        if page < total_pages
        else Span("Next"),
        cls="pagination",
    )

    toggle_all_ckbx = Script("""
        function toggleAll(source) {
        var checkboxes = document.querySelectorAll('input[type="checkbox"][name="ckbx_action"]');
        for (var i = 0; i < checkboxes.length; i++) {checkboxes[i].checked = source.checked;}}
    """)
    return Div(
        H4(f"Total after filter:{total_entries}"),
        action_btns,
        info_table,
        pagination,
        toggle_all_ckbx,
        id="query-results",
        cls="card",
    ), Div(Script(mermaid_js, type="module"), id="dialog-container")


@requires(
    fasthtml is not None, "The 'python-fasthtml' package is required to run the gui."
)
def start_gui(port: int | None = None):
    serve(
        appname="jobflow_remote.webgui.webgui",
        port=port,
        reload_includes=[Path(__file__).parent],
    )


if __name__ == "__main__":
    serve()
