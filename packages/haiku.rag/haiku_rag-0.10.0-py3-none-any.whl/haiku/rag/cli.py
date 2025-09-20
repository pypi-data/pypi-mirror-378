import asyncio
import warnings
from importlib.metadata import version
from pathlib import Path

import logfire
import typer
from rich.console import Console

from haiku.rag.app import HaikuRAGApp
from haiku.rag.config import Config
from haiku.rag.logging import configure_cli_logging
from haiku.rag.migration import migrate_sqlite_to_lancedb
from haiku.rag.utils import is_up_to_date

if Config.ENV == "development":
    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()
else:
    warnings.filterwarnings("ignore")

cli = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True
)

console = Console()


def complete_document_ids(ctx: typer.Context, incomplete: str):
    """Autocomplete document IDs from the selected DB."""
    db_path = ctx.params.get("db") or (Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb")

    try:
        from haiku.rag.client import HaikuRAG

        async def _list_ids():
            async with HaikuRAG(db_path) as client:
                docs = await client.list_documents()
                return [d.id for d in docs if d.id]

        ids = asyncio.run(_list_ids())
    except Exception:
        return []

    return [i for i in ids if i and i.startswith(incomplete)]


def complete_local_paths(ctx: typer.Context, incomplete: str) -> list[str]:
    """Autocomplete local filesystem paths.

    Provides directory/file suggestions based on the current incomplete input.
    Does not validate or restrict to specific extensions to keep it flexible
    (URLs are still allowed to be typed manually).
    """
    try:
        text = incomplete or ""

        # Expand user home
        from os.path import expanduser

        expanded = expanduser(text)
        p = Path(expanded)

        # Choose directory to list and prefix to filter
        if text == "" or text.endswith(("/", "\\")):
            directory = p
            prefix = ""
        else:
            directory = p.parent
            prefix = p.name

        if not directory.exists():
            return []

        suggestions: list[str] = []
        for entry in directory.iterdir():
            name = entry.name
            if not prefix or name.startswith(prefix):
                suggestion = str(directory / name)
                if entry.is_dir():
                    suggestion += "/"
                suggestions.append(suggestion)
        return suggestions
    except Exception:
        return []


async def check_version():
    """Check if haiku.rag is up to date and show warning if not."""
    up_to_date, current_version, latest_version = await is_up_to_date()
    if not up_to_date:
        console.print(
            f"[yellow]Warning: haiku.rag is outdated. Current: {current_version}, Latest: {latest_version}[/yellow]"
        )
        console.print("[yellow]Please update.[/yellow]")


def version_callback(value: bool):
    if value:
        v = version("haiku.rag")
        console.print(f"haiku.rag version {v}")
        raise typer.Exit()


@cli.callback()
def main(
    _version: bool = typer.Option(
        False,
        "-v",
        "--version",
        callback=version_callback,
        help="Show version and exit",
    ),
):
    """haiku.rag CLI - Vector database RAG system"""
    # Ensure only haiku.rag logs are emitted in CLI context
    configure_cli_logging()
    # Run version check before any command
    asyncio.run(check_version())


@cli.command("list", help="List all stored documents")
def list_documents(
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.list_documents())


@cli.command("add", help="Add a document from text input")
def add_document_text(
    text: str = typer.Argument(
        help="The text content of the document to add",
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.add_document_from_text(text=text))


@cli.command("add-src", help="Add a document from a file path or URL")
def add_document_src(
    source: str = typer.Argument(
        help="The file path or URL of the document to add",
        autocompletion=complete_local_paths,
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.add_document_from_source(source=source))


@cli.command("get", help="Get and display a document by its ID")
def get_document(
    doc_id: str = typer.Argument(
        help="The ID of the document to get",
        autocompletion=complete_document_ids,
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.get_document(doc_id=doc_id))


@cli.command("delete", help="Delete a document by its ID")
def delete_document(
    doc_id: str = typer.Argument(
        help="The ID of the document to delete",
        autocompletion=complete_document_ids,
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.delete_document(doc_id=doc_id))


# Add alias `rm` for delete
cli.command("rm", help="Alias for delete: remove a document by its ID")(delete_document)


@cli.command("search", help="Search for documents by a query")
def search(
    query: str = typer.Argument(
        help="The search query to use",
    ),
    limit: int = typer.Option(
        5,
        "--limit",
        "-l",
        help="Maximum number of results to return",
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.search(query=query, limit=limit))


@cli.command("ask", help="Ask a question using the QA agent")
def ask(
    question: str = typer.Argument(
        help="The question to ask",
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
    cite: bool = typer.Option(
        False,
        "--cite",
        help="Include citations in the response",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.ask(question=question, cite=cite))


@cli.command("research", help="Run multi-agent research and output a concise report")
def research(
    question: str = typer.Argument(
        help="The research question to investigate",
    ),
    max_iterations: int = typer.Option(
        3,
        "--max-iterations",
        "-n",
        help="Maximum search/analyze iterations",
    ),
    confidence_threshold: float = typer.Option(
        0.8,
        "--confidence-threshold",
        help="Minimum confidence (0-1) to stop",
    ),
    max_concurrency: int = typer.Option(
        1,
        "--max-concurrency",
        help="Max concurrent searches per iteration (planned)",
    ),
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show verbose progress output",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(
        app.research(
            question=question,
            max_iterations=max_iterations,
            confidence_threshold=confidence_threshold,
            max_concurrency=max_concurrency,
            verbose=verbose,
        )
    )


@cli.command("settings", help="Display current configuration settings")
def settings():
    app = HaikuRAGApp(db_path=Path())  # Don't need actual DB for settings
    app.show_settings()


@cli.command(
    "rebuild",
    help="Rebuild the database by deleting all chunks and re-indexing all documents",
)
def rebuild(
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.rebuild())


@cli.command("vacuum", help="Optimize and clean up all tables to reduce disk usage")
def vacuum(
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
):
    app = HaikuRAGApp(db_path=db)
    asyncio.run(app.vacuum())


@cli.command(
    "serve", help="Start the haiku.rag MCP server (by default in streamable HTTP mode)"
)
def serve(
    db: Path = typer.Option(
        Config.DEFAULT_DATA_DIR / "haiku.rag.lancedb",
        "--db",
        help="Path to the LanceDB database file",
    ),
    stdio: bool = typer.Option(
        False,
        "--stdio",
        help="Run MCP server on stdio Transport",
    ),
    sse: bool = typer.Option(
        False,
        "--sse",
        help="Run MCP server on SSE transport",
    ),
) -> None:
    """Start the MCP server."""
    if stdio and sse:
        console.print("[red]Error: Cannot use both --stdio and --http options[/red]")
        raise typer.Exit(1)

    app = HaikuRAGApp(db_path=db)

    transport = None
    if stdio:
        transport = "stdio"
    elif sse:
        transport = "sse"

    asyncio.run(app.serve(transport=transport))


@cli.command("migrate", help="Migrate an SQLite database to LanceDB")
def migrate(
    sqlite_path: Path = typer.Argument(
        help="Path to the SQLite database file to migrate",
    ),
):
    # Generate LanceDB path in same parent directory
    lancedb_path = sqlite_path.parent / (sqlite_path.stem + ".lancedb")

    success = asyncio.run(migrate_sqlite_to_lancedb(sqlite_path, lancedb_path))

    if not success:
        raise typer.Exit(1)


if __name__ == "__main__":
    cli()
