from typing import Optional

from .md_utils import read_md_files_from_dir, aggregate_md_contents
import typer
from enum import Enum
import os
from openai import OpenAI


class ProviderType(str, Enum):
    openai = "openai"
    deepseek = "deepseek"


app = typer.Typer()


@app.command()
def summarize(
    path: str = typer.Option(".", help="directory path of project"),
    provider: ProviderType = typer.Option(ProviderType.openai, help="provider model type, current support: openai, deepseek"),
    api_key: str = typer.Option(None, help="api key (env: OPENAI_API_KEY or DEEPSEEK_API_KEY)"),
    save_path: str = typer.Option(None, help="where to save the generated summary"),
):
    api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        typer.echo("please provide api key or set env variable", err=True)
        raise typer.Exit(code=1)

    assistant = AIAssistant(api_key, provider)
    answer = assistant.ask(assistant.generate_project_overview(path))
    if answer:
        typer.echo(answer)
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(answer)
                typer.echo(f"Summary saved to {save_path}")
            except Exception as e:
                typer.echo(f"Failed to save summary: {e}", err=True)
    else:
        typer.echo("No answer generated.", err=True)


class AIAssistant:
    def __init__(self, api_key: str, provider: ProviderType):
        self.api_key = api_key
        self.provider = provider.lower()
        if self.provider == "deepseek":
            self.base_url = "https://api.deepseek.com"
            self.model = "deepseek-chat"
        else:
            self.base_url = None  # openai default
            self.model = "gpt-4o"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        ) if self.base_url else OpenAI(api_key=self.api_key)

    def ask(self, question: str, system_prompt: str = "You are an expert technical writer.") -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def generate_project_overview(self, directory):
        md_files = read_md_files_from_dir(directory)
        context = aggregate_md_contents(md_files)
        prompt = (
            "Given the following collection of markdown documents from a code repository, "
            "generate a high-level, concise project overview. Your summary should include:\n"
            "- The project's main purpose and core architecture.\n"
            "- The primary components and their relationships.\n"
            "- Any notable subsystems or features.\n"
            "- Suggestions for where to find more detailed information (e.g., specific files or docs).\n\n"
            "Do not copy large sections of text verbatim. Instead, synthesize and summarize the most important information. "
            "Use clear, professional language suitable for a project overview.\n\n"
            "Here are the documents:\n"
            f"{context}"
        )
        answer = self.ask(prompt)
        return answer


def main():
    app()


if __name__ == "__main__":
    main()
