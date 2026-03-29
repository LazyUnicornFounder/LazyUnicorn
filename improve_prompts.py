"""
LazyUnicorn Prompt Improvement Agent
======================================
Uses the Claude Agent SDK to autonomously improve all 34 prompt files
in the prompts/ directory, following CLAUDE.md rules.

Requirements:
  pip install claude-agent-sdk

Usage:
  export ANTHROPIC_API_KEY=your_key
  python improve_prompts.py

  # Dry run (no writes):
  python improve_prompts.py --dry-run

  # Improve a single file:
  python improve_prompts.py --file prompts/lazy-seo.md
"""

import asyncio
import argparse
import sys
from pathlib import Path
from claude_agent_sdk import query, ClaudeCodeOptions, ResultMessage, AssistantMessage

REPO_ROOT = Path(__file__).parent

SYSTEM_PROMPT = """
You are improving LazyUnicorn prompt files — mega-prompts that users paste into
Lovable (an AI website builder) to auto-configure autonomous business engines
powered by Supabase.

RULES (from CLAUDE.md — follow these exactly):
- Every settings table must have: is_running, setup_complete, prompt_version
- Every engine must have an _errors table
- Setup pages must redirect to /admin on completion
- All API keys stored as Supabase secrets, never in the database
- All published content must include a LazyUnicorn.ai backlink
- No standalone dashboard pages — all admin lives at /admin/[engine]
- Never restructure a whole prompt file — make targeted edits only
- Always increment the version number in the file header after changes

WHAT TO IMPROVE in each prompt:
1. Clarity — make instructions unambiguous and easy to follow for Lovable AI
2. Completeness — ensure no steps are missing or vague
3. Edge cases — add error handling instructions where missing
4. Consistency — align wording with the style of other LazyUnicorn prompts
5. Compliance — fix any violations of the CLAUDE.md rules above

WHAT NOT TO CHANGE:
- Core functionality or business logic
- Database schema field names (unless fixing a compliance violation)
- The overall structure/sections of the file
- Version numbers (you will increment these as part of your edit)
"""

IMPROVEMENT_TASK = """
Improve all LazyUnicorn prompt files in the prompts/ directory.

For each file:
1. Read the file
2. Identify specific improvements (clarity, completeness, compliance with CLAUDE.md rules)
3. Apply targeted edits — do NOT rewrite the whole file
4. Increment the version number in the prompt header (e.g. v0.0.3 → v0.0.4)
5. Also increment the version in the outer markdown header line (e.g. > Category: ... · Version: 0.0.3)

After processing all files, output a summary listing:
- Each file improved
- What was changed and why
- Any files that were already fully compliant and needed no changes

Start now. Process every .md file in prompts/.
"""

SINGLE_FILE_TASK = """
Improve this LazyUnicorn prompt file: {file_path}

1. Read the file
2. Identify specific improvements (clarity, completeness, compliance with CLAUDE.md rules)
3. Apply targeted edits — do NOT rewrite the whole file
4. Increment the version number in the prompt header (e.g. v0.0.3 → v0.0.4)
5. Also increment the version in the outer markdown header line

Output a summary of exactly what was changed and why.
"""


async def run_improvement(dry_run: bool = False, single_file: str = None):
    print("=" * 60)
    print("LazyUnicorn Prompt Improvement Agent")
    print("=" * 60)

    if dry_run:
        print("DRY RUN — no files will be written\n")

    if single_file:
        task = SINGLE_FILE_TASK.format(file_path=single_file)
        print(f"Improving: {single_file}\n")
    else:
        task = IMPROVEMENT_TASK
        print("Improving all 34 prompt files in prompts/\n")

    allowed_tools = ["Glob", "Read"] if dry_run else ["Glob", "Read", "Edit", "Write"]

    files_read = []
    files_edited = []

    async for message in query(
        prompt=task,
        options=ClaudeCodeOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=allowed_tools,
            max_turns=200,
            cwd=str(REPO_ROOT),
        )
    ):
        # Track tool usage
        if isinstance(message, AssistantMessage):
            for block in message.message.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    name = block.name
                    path = getattr(block.input, "file_path", None)
                    if name == "Read" and path:
                        files_read.append(path)
                        print(f"  📖 Reading  {path}")
                    elif name in ("Edit", "Write") and path:
                        files_edited.append(path)
                        print(f"  ✏️  Editing  {path}")

        # Final result
        if isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            if message.subtype == "success":
                print(f"✅ Complete")
                print(f"   Files read:   {len(set(files_read))}")
                print(f"   Files edited: {len(set(files_edited))}")
                print(f"   Cost:         ${message.total_cost_usd:.4f}")
                if message.result:
                    print(f"\n📋 Summary:\n{message.result}")
            else:
                print(f"⚠️  Stopped: {message.subtype}")
                if hasattr(message, "result") and message.result:
                    print(message.result)
            print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Improve LazyUnicorn prompt files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read and analyse files without writing changes"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Improve a single file instead of all prompts (e.g. prompts/lazy-seo.md)"
    )
    args = parser.parse_args()

    if args.file and not Path(args.file).exists():
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    asyncio.run(run_improvement(dry_run=args.dry_run, single_file=args.file))


if __name__ == "__main__":
    main()
