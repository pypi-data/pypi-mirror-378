from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer

from .client import make_client, Provider
from .translator import Translator, ensure_user_prompt, DEFAULT_PROMPT_PATH

app = typer.Typer(add_completion=False)

def initialize_prompt() -> Path:
    return ensure_user_prompt()

@app.command()
def init() -> None:
    p = ensure_user_prompt()
    print(str(p))


def start_translation(
        docs_src: Path,
        out_dir: Path,
        base_language: str,
        languages: list[str],
        model: str = "gpt-4o-mini",
        provider: Provider = "openai",
        api_key: str | None = None,
        base_url: str | None = None,
        prompt_path: Path | None = None,
):
    client = make_client(provider=provider, api_key=api_key, base_url=base_url)
    translator = Translator(
        client=client,
        base_language=base_language,
        languages=languages,
        model=model,
        prompt_path=prompt_path or DEFAULT_PROMPT_PATH,
    )
    asyncio.run(translator.translate_directory(docs_src, out_dir))



@app.command()
def run(
        docs_src: Path = typer.Argument(),
        out_dir: Path = typer.Argument(),
        base_language: str = typer.Option("en"),
        languages: list[str] = typer.Option(["de"]),
        model: str = typer.Option("gpt-4o-mini"),
        provider: Provider = typer.Option("openai"),
        api_key: str | None = typer.Option(None),
        api_env_key: str = typer.Option("OPENAI_API_KEY"),
        base_url: str | None = typer.Option(None),
        prompt_path: Path | None = typer.Option(None),
) -> None:
    api_key = api_key or os.getenv(api_env_key)
    client = make_client(provider=provider, api_key=api_key, base_url=base_url)
    translator = Translator(
        client=client,
        base_language=base_language,
        languages=languages,
        model=model,
        prompt_path=prompt_path or DEFAULT_PROMPT_PATH,
    )
    asyncio.run(translator.translate_directory(docs_src, out_dir))
