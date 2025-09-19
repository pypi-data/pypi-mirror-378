import asyncio
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress

from haiku.rag.client import HaikuRAG
from haiku.rag.config import Config
from haiku.rag.mcp import create_mcp_server
from haiku.rag.monitor import FileWatcher
from haiku.rag.research.orchestrator import ResearchOrchestrator
from haiku.rag.store.models.chunk import Chunk
from haiku.rag.store.models.document import Document


class HaikuRAGApp:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.console = Console()

    async def list_documents(self):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            documents = await self.client.list_documents()
            for doc in documents:
                self._rich_print_document(doc, truncate=True)

    async def add_document_from_text(self, text: str):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            doc = await self.client.create_document(text)
            self._rich_print_document(doc, truncate=True)
            self.console.print(
                f"[b]Document with id [cyan]{doc.id}[/cyan] added successfully.[/b]"
            )

    async def add_document_from_source(self, source: str):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            doc = await self.client.create_document_from_source(source)
            self._rich_print_document(doc, truncate=True)
            self.console.print(
                f"[b]Document with id [cyan]{doc.id}[/cyan] added successfully.[/b]"
            )

    async def get_document(self, doc_id: str):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            doc = await self.client.get_document_by_id(doc_id)
            if doc is None:
                self.console.print(f"[red]Document with id {doc_id} not found.[/red]")
                return
            self._rich_print_document(doc, truncate=False)

    async def delete_document(self, doc_id: str):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            deleted = await self.client.delete_document(doc_id)
            if deleted:
                self.console.print(f"[b]Document {doc_id} deleted successfully.[/b]")
            else:
                self.console.print(
                    f"[yellow]Document with id {doc_id} not found.[/yellow]"
                )

    async def search(self, query: str, limit: int = 5):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            results = await self.client.search(query, limit=limit)
            if not results:
                self.console.print("[red]No results found.[/red]")
                return
            for chunk, score in results:
                self._rich_print_search_result(chunk, score)

    async def ask(self, question: str, cite: bool = False):
        async with HaikuRAG(db_path=self.db_path) as self.client:
            try:
                answer = await self.client.ask(question, cite=cite)
                self.console.print(f"[bold blue]Question:[/bold blue] {question}")
                self.console.print()
                self.console.print("[bold green]Answer:[/bold green]")
                self.console.print(Markdown(answer))
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    async def research(
        self, question: str, max_iterations: int = 3, verbose: bool = False
    ):
        """Run multi-agent research on a question."""
        async with HaikuRAG(db_path=self.db_path) as client:
            try:
                # Create orchestrator with default config or fallback to QA
                orchestrator = ResearchOrchestrator()

                if verbose:
                    self.console.print(
                        f"[bold cyan]Starting research with {orchestrator.provider}:{orchestrator.model}[/bold cyan]"
                    )
                    self.console.print(f"[bold blue]Question:[/bold blue] {question}")
                    self.console.print()

                # Conduct research
                report = await orchestrator.conduct_research(
                    question=question,
                    client=client,
                    max_iterations=max_iterations,
                    verbose=verbose,
                )

                # Display the report
                self.console.print("[bold green]Research Report[/bold green]")
                self.console.rule()

                # Title and Executive Summary
                self.console.print(f"[bold]{report.title}[/bold]")
                self.console.print()
                self.console.print("[bold cyan]Executive Summary:[/bold cyan]")
                self.console.print(report.executive_summary)
                self.console.print()

                # Main Findings
                if report.main_findings:
                    self.console.print("[bold cyan]Main Findings:[/bold cyan]")
                    for finding in report.main_findings:
                        self.console.print(f"• {finding}")
                    self.console.print()

                # (Themes section removed)

                # Conclusions
                if report.conclusions:
                    self.console.print("[bold cyan]Conclusions:[/bold cyan]")
                    for conclusion in report.conclusions:
                        self.console.print(f"• {conclusion}")
                    self.console.print()

                # Recommendations
                if report.recommendations:
                    self.console.print("[bold cyan]Recommendations:[/bold cyan]")
                    for rec in report.recommendations:
                        self.console.print(f"• {rec}")
                    self.console.print()

                # Limitations
                if report.limitations:
                    self.console.print("[bold yellow]Limitations:[/bold yellow]")
                    for limitation in report.limitations:
                        self.console.print(f"• {limitation}")
                    self.console.print()

                # Sources Summary
                if report.sources_summary:
                    self.console.print("[bold cyan]Sources:[/bold cyan]")
                    self.console.print(report.sources_summary)

            except Exception as e:
                self.console.print(f"[red]Error during research: {e}[/red]")

    async def rebuild(self):
        async with HaikuRAG(db_path=self.db_path, skip_validation=True) as client:
            try:
                documents = await client.list_documents()
                total_docs = len(documents)

                if total_docs == 0:
                    self.console.print(
                        "[yellow]No documents found in database.[/yellow]"
                    )
                    return

                self.console.print(
                    f"[b]Rebuilding database with {total_docs} documents...[/b]"
                )
                with Progress() as progress:
                    task = progress.add_task("Rebuilding...", total=total_docs)
                    async for _ in client.rebuild_database():
                        progress.update(task, advance=1)

                self.console.print("[b]Database rebuild completed successfully.[/b]")
            except Exception as e:
                self.console.print(f"[red]Error rebuilding database: {e}[/red]")

    async def vacuum(self):
        """Run database maintenance: optimize and cleanup table history."""
        try:
            async with HaikuRAG(db_path=self.db_path, skip_validation=True) as client:
                await client.vacuum()
            self.console.print("[b]Vacuum completed successfully.[/b]")
        except Exception as e:
            self.console.print(f"[red]Error during vacuum: {e}[/red]")

    def show_settings(self):
        """Display current configuration settings."""
        self.console.print("[bold]haiku.rag configuration[/bold]")
        self.console.print()

        # Get all config fields dynamically
        for field_name, field_value in Config.model_dump().items():
            # Format the display value
            if isinstance(field_value, str) and (
                "key" in field_name.lower()
                or "password" in field_name.lower()
                or "token" in field_name.lower()
            ):
                # Hide sensitive values but show if they're set
                display_value = "✓ Set" if field_value else "✗ Not set"
            else:
                display_value = field_value

            self.console.print(f"  [cyan]{field_name}[/cyan]: {display_value}")

    def _rich_print_document(self, doc: Document, truncate: bool = False):
        """Format a document for display."""
        if truncate:
            content = doc.content.splitlines()
            if len(content) > 3:
                content = content[:3] + ["\n…"]
            content = "\n".join(content)
            content = Markdown(content)
        else:
            content = Markdown(doc.content)
        self.console.print(
            f"[repr.attrib_name]id[/repr.attrib_name]: {doc.id} [repr.attrib_name]uri[/repr.attrib_name]: {doc.uri} [repr.attrib_name]meta[/repr.attrib_name]: {doc.metadata}"
        )
        self.console.print(
            f"[repr.attrib_name]created at[/repr.attrib_name]: {doc.created_at} [repr.attrib_name]updated at[/repr.attrib_name]: {doc.updated_at}"
        )
        self.console.print("[repr.attrib_name]content[/repr.attrib_name]:")
        self.console.print(content)
        self.console.rule()

    def _rich_print_search_result(self, chunk: Chunk, score: float):
        """Format a search result chunk for display."""
        content = Markdown(chunk.content)
        self.console.print(
            f"[repr.attrib_name]document_id[/repr.attrib_name]: {chunk.document_id} "
            f"[repr.attrib_name]score[/repr.attrib_name]: {score:.4f}"
        )
        if chunk.document_uri:
            self.console.print("[repr.attrib_name]document uri[/repr.attrib_name]:")
            self.console.print(chunk.document_uri)
        if chunk.document_meta:
            self.console.print("[repr.attrib_name]document meta[/repr.attrib_name]:")
            self.console.print(chunk.document_meta)
        self.console.print("[repr.attrib_name]content[/repr.attrib_name]:")
        self.console.print(content)
        self.console.rule()

    async def serve(self, transport: str | None = None):
        """Start the MCP server."""
        async with HaikuRAG(self.db_path) as client:
            monitor = FileWatcher(paths=Config.MONITOR_DIRECTORIES, client=client)
            monitor_task = asyncio.create_task(monitor.observe())
            server = create_mcp_server(self.db_path)

            try:
                if transport == "stdio":
                    await server.run_stdio_async()
                elif transport == "sse":
                    await server.run_sse_async()
                else:
                    await server.run_http_async(transport="streamable-http")
            except KeyboardInterrupt:
                pass
            finally:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
