# Shared Context Files

Place large reference documents here that will be sent once to establish context.

These files are loaded via `get_shared_context_files()` in your benchmark.py and sent before processing individual items.

**Example use case:**
- Large essay that all test items reference
- Reference documentation
- Background material

The files here save tokens by being sent once and cached (especially with Anthropic's prompt caching).
