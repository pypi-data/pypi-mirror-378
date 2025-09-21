from __future__ import annotations

import logging
import subprocess
from datetime import datetime
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from core import mailer
from core import github_issues
from django.utils import timezone

from nodes.models import NetMessage


logger = logging.getLogger(__name__)


@shared_task
def heartbeat() -> None:
    """Log a simple heartbeat message."""
    logger.info("Heartbeat task executed")


@shared_task
def birthday_greetings() -> None:
    """Send birthday greetings to users via Net Message and email."""
    User = get_user_model()
    today = timezone.localdate()
    for user in User.objects.filter(birthday=today):
        NetMessage.broadcast("Happy bday!", user.username)
        if user.email:
            mailer.send(
                "Happy bday!",
                f"Happy bday! {user.username}",
                [user.email],
                settings.DEFAULT_FROM_EMAIL,
                fail_silently=True,
            )


@shared_task
def check_github_updates() -> None:
    """Check the GitHub repo for updates and upgrade if needed."""
    base_dir = Path(__file__).resolve().parent.parent
    mode_file = base_dir / "locks" / "auto_upgrade.lck"
    mode = "version"
    if mode_file.exists():
        mode = mode_file.read_text().strip()

    branch = "main"
    subprocess.run(["git", "fetch", "origin", branch], cwd=base_dir, check=True)

    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "auto-upgrade.log"
    with log_file.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} check_github_updates triggered\n")

    notify = None
    startup = None
    try:  # pragma: no cover - optional dependency
        from core.notifications import notify  # type: ignore
    except Exception:
        notify = None
    try:  # pragma: no cover - optional dependency
        from nodes.apps import _startup_notification as startup  # type: ignore
    except Exception:
        startup = None

    if mode == "latest":
        local = (
            subprocess.check_output(["git", "rev-parse", branch], cwd=base_dir)
            .decode()
            .strip()
        )
        remote = (
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    f"origin/{branch}",
                ],
                cwd=base_dir,
            )
            .decode()
            .strip()
        )
        if local == remote:
            if startup:
                startup()
            return
        if notify:
            notify("Upgrading...", "")
        args = ["./upgrade.sh", "--latest", "--no-restart"]
    else:
        local = "0"
        version_file = base_dir / "VERSION"
        if version_file.exists():
            local = version_file.read_text().strip()
        remote = (
            subprocess.check_output(
                [
                    "git",
                    "show",
                    f"origin/{branch}:VERSION",
                ],
                cwd=base_dir,
            )
            .decode()
            .strip()
        )
        if local == remote:
            if startup:
                startup()
            return
        if notify:
            notify("Upgrading...", "")
        args = ["./upgrade.sh", "--no-restart"]

    with log_file.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} running: {' '.join(args)}\n")

    subprocess.run(args, cwd=base_dir, check=True)

    service_file = base_dir / "locks/service.lck"
    if service_file.exists():
        service = service_file.read_text().strip()
        subprocess.run(
            [
                "sudo",
                "systemctl",
                "kill",
                "--signal=TERM",
                service,
            ]
        )
    else:
        subprocess.run(["pkill", "-f", "manage.py runserver"])


@shared_task
def poll_email_collectors() -> None:
    """Poll all configured email collectors for new messages."""
    try:
        from .models import EmailCollector
    except Exception:  # pragma: no cover - app not ready
        return

    for collector in EmailCollector.objects.all():
        collector.collect()


@shared_task
def report_runtime_issue(
    title: str,
    body: str,
    labels: list[str] | None = None,
    fingerprint: str | None = None,
):
    """Report a runtime issue to GitHub using :mod:`core.github_issues`."""

    try:
        response = github_issues.create_issue(
            title,
            body,
            labels=labels,
            fingerprint=fingerprint,
        )
    except Exception:
        logger.exception("Failed to report runtime issue '%s'", title)
        raise

    if response is None:
        logger.info("Skipped GitHub issue creation for fingerprint %s", fingerprint)
    else:
        logger.info("Reported runtime issue '%s' to GitHub", title)

    return response


@shared_task
def run_client_report_schedule(schedule_id: int) -> None:
    """Execute a :class:`core.models.ClientReportSchedule` run."""

    from core.models import ClientReportSchedule

    schedule = ClientReportSchedule.objects.filter(pk=schedule_id).first()
    if not schedule:
        logger.warning("ClientReportSchedule %s no longer exists", schedule_id)
        return

    try:
        schedule.run()
    except Exception:
        logger.exception("ClientReportSchedule %s failed", schedule_id)
        raise
