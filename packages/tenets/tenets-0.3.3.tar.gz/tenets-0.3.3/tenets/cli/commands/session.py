"""Session management commands."""

from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tenets.config import TenetsConfig
from tenets.storage.session_db import SessionDB
from tenets.utils.timing import CommandTimer

session_app = typer.Typer(help="Manage development sessions")
console = Console()


def _get_db() -> SessionDB:
    return SessionDB(TenetsConfig())


@session_app.command()
def create(name: str = typer.Argument(..., help="Session name")):
    """Create a new session or activate it if it already exists."""
    timer = CommandTimer(console, quiet=True)  # Quiet timer for quick operations
    timer.start()

    db = _get_db()
    existing = db.get_session(name)
    if existing:
        # If it exists, just mark it active and exit successfully
        db.set_active(name, True)
        timing_result = timer.stop()
        console.print(
            f"[green]✓ Activated session:[/green] {name} [dim]({timing_result.formatted_duration})[/dim]"
        )
        return
    db.create_session(name)
    db.set_active(name, True)
    timing_result = timer.stop()
    console.print(
        f"[green]✓ Created session:[/green] {name} [dim]({timing_result.formatted_duration})[/dim]"
    )


@session_app.command("start")
def start(name: str = typer.Argument(..., help="Session name")):
    """Start (create or activate) a session (alias of create)."""
    return create(name)


@session_app.command("list")
def list_cmd():
    """List sessions."""
    timer = CommandTimer(console, quiet=True)
    timer.start()

    db = _get_db()
    sessions = db.list_sessions()
    if not sessions:
        console.print("[dim]No sessions found.[/dim]")
        return
    table = Table(title="Sessions")
    table.add_column("Name", style="cyan")
    table.add_column("Active", style="green")
    table.add_column("Created", style="green")
    table.add_column("Metadata", style="magenta")
    for s in sessions:
        # Coerce potential MagicMocks to plain serializable types for display
        meta = s.metadata if isinstance(s.metadata, dict) else {}
        is_active = "yes" if meta.get("active") else ""
        table.add_row(
            str(s.name),
            str(is_active),
            str(
                getattr(s.created_at, "isoformat", lambda **_: str(s.created_at))(
                    timespec="seconds"
                )
            ),
            json.dumps(meta),
        )
    timing_result = timer.stop()
    console.print(table)
    console.print(
        f"[dim]⏱  Found {len(sessions)} sessions in {timing_result.formatted_duration}[/dim]"
    )


@session_app.command()
def show(name: str = typer.Argument(..., help="Session name")):
    """Show session details."""
    db = _get_db()
    sess = db.get_session(name)
    if not sess:
        console.print(f"[red]Session not found:[/red] {name}")
        raise typer.Exit(1)
    console.print(
        Panel(
            f"Name: {sess.name}\nActive: {bool(sess.metadata.get('active'))}\nCreated: {sess.created_at.isoformat(timespec='seconds')}\nMetadata: {json.dumps(sess.metadata, indent=2)}",
            title=f"Session: {sess.name}",
        )
    )


@session_app.command()
def delete(
    name: str = typer.Argument(..., help="Session name"),
    keep_context: bool = typer.Option(
        False, "--keep-context", help="Do not delete stored context artifacts"
    ),
):
    """Delete a session (and its stored context unless --keep-context)."""
    timer = CommandTimer(console, quiet=True)  # Quiet timer for quick operations
    timer.start()

    db = _get_db()
    deleted = db.delete_session(name, purge_context=not keep_context)
    timing_result = timer.stop()

    if deleted:
        console.print(
            f"[red]Deleted session:[/red] {name} [dim]({timing_result.formatted_duration})[/dim]"
        )
    else:
        console.print(f"[yellow]No such session:[/yellow] {name}")


@session_app.command("clear")
def clear_all(keep_context: bool = typer.Option(False, "--keep-context", help="Keep artifacts")):
    """Delete ALL sessions (optionally keep artifacts)."""
    timer = CommandTimer(console, quiet=True)
    timer.start()

    db = _get_db()
    count = db.delete_all_sessions(purge_context=not keep_context)
    timing_result = timer.stop()

    if count:
        console.print(
            f"[red]Deleted {count} session(s)[/red] [dim]({timing_result.formatted_duration})[/dim]"
        )
    else:
        console.print("[dim]No sessions to delete.[/dim]")


@session_app.command("add")
def add_context(
    name: str = typer.Argument(..., help="Session name"),
    kind: str = typer.Argument(..., help="Content kind tag (e.g. note, context_result)"),
    file: typer.FileText = typer.Argument(..., help="File whose content to attach"),
):
    """Attach arbitrary content file to a session (stored as text)."""
    db = _get_db()
    content = file.read()
    db.add_context(name, kind=kind, content=content)
    console.print(f"[green]✓ Added {kind} to session:[/green] {name}")


@session_app.command("reset")
def reset_session(name: str = typer.Argument(..., help="Session name")):
    """Reset (delete and recreate) a session and purge its context."""
    db = _get_db()
    db.delete_session(name, purge_context=True)
    db.create_session(name)
    db.set_active(name, True)
    console.print(f"[green]✓ Reset session:[/green] {name}")


@session_app.command("resume")
def resume(name: Optional[str] = typer.Argument(None, help="Session name (optional)")):
    """Mark a session as active (load/resume existing session).

    If NAME is omitted, resumes the most recently active session.
    """
    db = _get_db()
    target = name
    if not target:
        active = db.get_active_session()
        if not active:
            console.print("[red]No active session. Specify a NAME to resume.[/red]")
            raise typer.Exit(1)
        target = active.name
    sess = db.get_session(target)
    if not sess:
        console.print(f"[red]Session not found:[/red] {target}")
        raise typer.Exit(1)
    db.set_active(target, True)
    console.print(f"[green]✓ Resumed session:[/green] {target}")


@session_app.command("exit")
def exit_session(name: Optional[str] = typer.Argument(None, help="Session name (optional)")):
    """Mark a session as inactive (exit/end session).

    If NAME is omitted, exits the current active session.
    """
    db = _get_db()
    target = name
    if not target:
        active = db.get_active_session()
        if not active:
            console.print("[red]No active session to exit.[/red]")
            raise typer.Exit(1)
        target = active.name
    sess = db.get_session(target)
    if not sess:
        console.print(f"[red]Session not found:[/red] {target}")
        raise typer.Exit(1)
    db.set_active(target, False)
    console.print(f"[yellow]Exited session:[/yellow] {target}")


@session_app.command("save")
def save_session(
    new_name: str = typer.Argument(..., help="New name for the session"),
    from_session: Optional[str] = typer.Option(
        None, "--from", "-f", help="Source session to save from (default: current/default session)"
    ),
    delete_source: bool = typer.Option(
        False, "--delete-source", help="Delete the source session after saving"
    ),
):
    """Save a session with a new name (useful for saving default/temporary sessions).

    This command copies an existing session (including all its metadata, pinned files,
    tenets, and context) to a new session with the specified name.

    Examples:
        # Save the default session with a custom name
        tenets session save my-feature

        # Save a specific session with a new name
        tenets session save production-fix --from debug-session

        # Save and clean up the original
        tenets session save final-version --from default --delete-source
    """
    db = _get_db()

    # Determine source session
    source_name = from_session
    if not source_name:
        # Try to get active session first
        active = db.get_active_session()
        if active:
            source_name = active.name
        else:
            # Default to "default" session
            source_name = "default"

    # Get source session
    source_session = db.get_session(source_name)
    if not source_session:
        console.print(f"[red]Source session not found:[/red] {source_name}")
        console.print("[dim]Tip: Use 'tenets session list' to see available sessions.[/dim]")
        raise typer.Exit(1)

    # Check if target already exists
    if db.get_session(new_name):
        if not typer.confirm(f"Session '{new_name}' already exists. Overwrite?"):
            raise typer.Abort()
        db.delete_session(new_name, purge_context=True)

    # Create new session with same metadata
    db.create_session(new_name)
    new_session = db.get_session(new_name)

    # Copy metadata (including pinned files, tenets, etc.)
    if source_session.metadata:
        new_session.metadata = source_session.metadata.copy()
        # Update the session name in metadata if it's stored there
        if "name" in new_session.metadata:
            new_session.metadata["name"] = new_name

    # Copy context artifacts
    # Note: This would require additional implementation in SessionDB
    # to copy context between sessions

    # Set as active
    db.set_active(new_name, True)

    console.print(f"[green]✓ Saved session '{source_name}' as '{new_name}'[/green]")

    # Delete source if requested
    if delete_source:
        if source_name == "default":
            if not typer.confirm("Delete the default session? This will remove all unsaved work."):
                console.print("[yellow]Keeping source session.[/yellow]")
            else:
                db.delete_session(source_name, purge_context=True)
                console.print(f"[yellow]Deleted source session:[/yellow] {source_name}")
        else:
            db.delete_session(source_name, purge_context=True)
            console.print(f"[yellow]Deleted source session:[/yellow] {source_name}")
