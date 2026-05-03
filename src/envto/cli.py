import sys
import pathlib
from pathlib import Path
import typer
import os
import shutil
from datetime import datetime
from typing import Optional

# Ensure the project root (src) is on PYTHONPATH when this file is run directly
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from envto import db

app = typer.Typer(help="🔧 .env 파일을 SQLite3 로 관리하는 CLI")


def _fzf_select(label: str, items: list[tuple[str, str, str]]) -> tuple[str, str, str] | None:
    """Show a list of (id, path, update_dt) with fzf and return the chosen record.
    Returns ``None`` when the user aborts.
    """
    if not items:
        typer.echo("⚠️ No records found.", err=True)
        return None

    # Prepare fzf input: "id\tpath\tupdate_dt"
    input_text = "\n".join(f"{i}\t{p}\t{d}" for i, p, d in items)

    import subprocess
    proc = subprocess.Popen(
        ["fzf", "-e", "--with-nth=1..", "--delimiter=\t", "--prompt", f"{label}> "],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, _ = proc.communicate(input_text)
    if proc.returncode != 0 or not out.strip():
        return None

    chosen_id = out.split("\t", 1)[0]
    for rec in items:
        if rec[0] == chosen_id:
            return rec
    return None


@app.command()
def save(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Directory containing .env (default: cwd)",
    )
) -> None:
    """Save the .env file from ``path`` (or cwd) into the SQLite storage."""
    target_dir = str(path) if path else os.getcwd()
    env_file = os.path.join(target_dir, ".env")

    if not os.path.isfile(env_file):
        typer.echo(f"❌ .env not found: {env_file}", err=True)
        raise typer.Exit(code=1)

    with open(env_file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    rec_id = db.save(target_dir, content)
    typer.echo(f"✅ Saved → {rec_id}  (location: {target_dir})")


@app.command()
def load() -> None:
    """Select a stored .env record and write it to ``./.env``.
    Existing ``.env`` is backed up with a timestamped hidden filename.
    """
    rows = db.all_records()
    sel = _fzf_select("Select .env to load", rows)
    if sel is None:
        raise typer.Exit()

    rec_id, rec_path, _ = sel
    env_content = db.view_record(rec_id)
    if env_content is None:
        typer.echo(f"❌ No env content for {rec_id}", err=True)
        raise typer.Exit(code=1)

    dest = os.path.abspath(".env")

    # Backup existing .env if present
    if os.path.exists(dest):
        backup_name = f".{datetime.now().strftime('%Y%m%d%H%M%S')}-env"
        backup_path = os.path.join(os.path.dirname(dest), backup_name)
        shutil.copy2(dest, backup_path)
        typer.echo(f"🔄 Backup created → {backup_path}")

    with open(dest, "w", encoding="utf-8") as f:
        f.write(env_content)
    typer.echo(f"✅ Written → {dest}  (source id={rec_id})")


@app.command()
def view() -> None:
    """Select a stored .env record and display its contents on the terminal."""
    rows = db.all_records()
    sel = _fzf_select("Select .env to view", rows)
    if sel is None:
        raise typer.Exit()

    rec_id, rec_path, _ = sel
    content = db.view_record(rec_id)
    if content is None:
        typer.echo(f"❌ No env content for {rec_id}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"# ID   : {rec_id}")
    typer.echo(f"# Path : {rec_path}")
    typer.echo("#" + "=" * 60)
    typer.echo(content, nl=False)


def main() -> None:
    """Entry point used by the console script.
    It ensures the project root is on ``PYTHONPATH`` and then runs the Typer app.
    """
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
    app()

if __name__ == "__main__":
    main()
