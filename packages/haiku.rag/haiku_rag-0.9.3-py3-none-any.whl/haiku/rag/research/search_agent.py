from pydantic_ai import RunContext
from pydantic_ai.format_prompt import format_as_xml
from pydantic_ai.run import AgentRunResult

from haiku.rag.research.base import BaseResearchAgent, SearchAnswer
from haiku.rag.research.dependencies import ResearchDependencies
from haiku.rag.research.prompts import SEARCH_AGENT_PROMPT


class SearchSpecialistAgent(BaseResearchAgent[SearchAnswer]):
    """Agent specialized in answering questions using RAG search."""

    def __init__(self, provider: str, model: str) -> None:
        super().__init__(provider, model, output_type=SearchAnswer)

    async def run(
        self, prompt: str, deps: ResearchDependencies, **kwargs
    ) -> AgentRunResult[SearchAnswer]:
        """Execute the agent and persist the QA pair in shared context.

        Pydantic AI enforces `SearchAnswer` as the output model; we just store
        the QA response with the last search results as sources.
        """
        console = deps.console
        if console:
            console.print(f"\t{prompt}")

        result = await super().run(prompt, deps, **kwargs)
        deps.context.add_qa_response(result.output)
        deps.context.sub_questions.remove(prompt)
        if console:
            answer = result.output.answer
            answer_preview = answer[:150] + "…" if len(answer) > 150 else answer
            console.log(f"\n   [green]✓[/green] {answer_preview}")

        return result

    def get_system_prompt(self) -> str:
        return SEARCH_AGENT_PROMPT

    def register_tools(self) -> None:
        """Register search-specific tools."""

        @self.agent.tool
        async def search_and_answer(
            ctx: RunContext[ResearchDependencies],
            query: str,
            limit: int = 5,
        ) -> str:
            """Search the KB and return a concise context pack."""
            search_results = await ctx.deps.client.search(query, limit=limit)
            expanded = await ctx.deps.client.expand_context(search_results)

            snippet_entries = [
                {
                    "text": chunk.content,
                    "score": score,
                    "document_uri": (chunk.document_uri or ""),
                }
                for chunk, score in expanded
            ]

            # Return an XML-formatted payload with the question and snippets.
            if snippet_entries:
                return format_as_xml(snippet_entries, root_tag="snippets")
            else:
                return (
                    f"No relevant information found in the knowledge base for: {query}"
                )
