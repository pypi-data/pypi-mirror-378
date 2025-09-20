"""
Command-line interface for running the Yellhorn MCP server.

This module provides a simple command to run the Yellhorn MCP server as a standalone
application, making it easier to integrate with other programs or launch directly.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

import uvicorn

from yellhorn_mcp.server import is_git_repository, mcp

logging.basicConfig(
    stream=sys.stderr, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
)


def main():
    """
    Run the Yellhorn MCP server as a standalone command.

    This function parses command-line arguments, validates environment variables,
    and launches the MCP server.
    """
    parser = argparse.ArgumentParser(description="Yellhorn MCP Server")

    parser.add_argument(
        "--repo-path",
        dest="repo_path",
        default=os.getenv("REPO_PATH", os.getcwd()),
        help="Path to the Git repository (default: current directory or REPO_PATH env var)",
    )

    parser.add_argument(
        "--model",
        dest="model",
        default=os.getenv("YELLHORN_MCP_MODEL", "gemini-2.5-pro"),
        help="Model to use (e.g., gemini-2.5-pro, gemini-2.5-flash, "
        "gpt-4o, gpt-4o-mini, gpt-5, gpt-5-mini, gpt-5-nano, "
        "o4-mini, o3, o3-deep-research, o4-mini-deep-research). "
        "Default: gemini-2.5-pro or YELLHORN_MCP_MODEL env var.",
    )

    parser.add_argument(
        "--codebase-reasoning",
        dest="codebase_reasoning",
        default=os.getenv("YELLHORN_MCP_REASONING", "full"),
        choices=["full", "lsp", "none"],
        help="Control codebase context for AI processing: "
        "'full' (all code), 'lsp' (function signatures only), 'none' (no code). "
        "Default: full or YELLHORN_MCP_REASONING env var.",
    )

    parser.add_argument(
        "--no-search-grounding",
        dest="no_search_grounding",
        action="store_true",
        help="Disable Google Search Grounding for Gemini models. "
        "By default, search grounding is enabled for all Gemini models. "
        "This flag maps to YELLHORN_MCP_SEARCH=off environment variable.",
    )

    parser.add_argument(
        "--reasoning-effort",
        dest="reasoning_effort",
        choices=["low", "medium", "high"],
        default=None,
        help="Set reasoning effort level for GPT-5 models (gpt-5, gpt-5-mini). "
        "Options: low, medium, high. This provides enhanced reasoning capabilities "
        "at higher cost. Has no effect on models that don't support reasoning.",
    )

    parser.add_argument(
        "--host",
        dest="host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    args = parser.parse_args()

    # Validate API keys based on model
    model = args.model
    is_openai_model = model.startswith("gpt-") or model.startswith("o")

    # For Gemini models
    if not is_openai_model:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable is not set")
            logging.error(
                "Please set the GEMINI_API_KEY environment variable with your Gemini API key"
            )
            sys.exit(1)
    # For OpenAI models
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY environment variable is not set")
            logging.error(
                "Please set the OPENAI_API_KEY environment variable with your OpenAI API key"
            )
            sys.exit(1)

    # Set environment variables for the server
    os.environ["REPO_PATH"] = args.repo_path
    os.environ["YELLHORN_MCP_MODEL"] = args.model
    os.environ["YELLHORN_MCP_REASONING"] = args.codebase_reasoning

    # Handle search grounding flag
    if args.no_search_grounding:
        os.environ["YELLHORN_MCP_SEARCH"] = "off"

    # Handle reasoning effort flag
    if args.reasoning_effort:
        os.environ["YELLHORN_MCP_REASONING_EFFORT"] = args.reasoning_effort

    # Validate repository path
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        logging.error(f"Repository path {repo_path} does not exist")
        sys.exit(1)

    # Check if the path is a Git repository (either standard or worktree)
    if not is_git_repository(repo_path):
        logging.error(f"{repo_path} is not a Git repository")
        sys.exit(1)

    logging.info(f"Starting Yellhorn MCP server at http://{args.host}:{args.port}")
    logging.info(f"Repository path: {repo_path}")
    logging.info(f"Using model: {args.model}")

    # Show search grounding status if using Gemini model
    is_openai_model = args.model.startswith("gpt-") or args.model.startswith("o")
    if not is_openai_model:
        search_status = "disabled" if args.no_search_grounding else "enabled"
        logging.info(f"Google Search Grounding: {search_status}")

    # Show reasoning effort status for GPT-5 models
    if args.model.startswith("gpt-5") and args.model != "gpt-5-nano":
        if args.reasoning_effort:
            logging.info(f"Reasoning effort: {args.reasoning_effort}")
        else:
            logging.info("Reasoning effort: disabled")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
