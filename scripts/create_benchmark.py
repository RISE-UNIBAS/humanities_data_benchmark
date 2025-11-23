#!/usr/bin/env python3
"""CLI tool to create a new benchmark with all necessary files and structure.

Usage:
    python scripts/create_benchmark.py
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def get_input(prompt: str, default: Optional[str] = None, required: bool = True) -> str:
    """Get user input with optional default value."""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt} [{default}]:{Colors.END} "
    else:
        full_prompt = f"{Colors.CYAN}{prompt}:{Colors.END} "

    while True:
        try:
            value = input(full_prompt).strip()

            if not value and default:
                return default

            if not value and required:
                print_error("This field is required. Please provide a value.")
                continue

            return value
        except EOFError:
            if default:
                return default
            elif not required:
                return ""
            else:
                print_error("Input required but EOF encountered.")
                continue
        except KeyboardInterrupt:
            raise


def get_int_input(prompt: str, default: int = 1, min_val: int = 1, max_val: int = 100) -> int:
    """Get integer input with validation."""
    while True:
        try:
            full_prompt = f"{Colors.CYAN}{prompt} [{default}]:{Colors.END} "
            value = input(full_prompt).strip()

            if not value:
                return default

            try:
                int_value = int(value)
                if min_val <= int_value <= max_val:
                    return int_value
                else:
                    print_error(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print_error(f"Invalid input. Please enter a number between {min_val} and {max_val}.")
        except EOFError:
            return default
        except KeyboardInterrupt:
            raise


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user."""
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{Colors.CYAN}{prompt} [{default_str}]:{Colors.END} "

    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        try:
            value = input(full_prompt).strip().lower()

            if not value:
                return default

            if value in ['y', 'yes']:
                return True
            elif value in ['n', 'no']:
                return False
            else:
                print_error("Please enter 'y' or 'n'.")
                attempts += 1
        except EOFError:
            return default
        except KeyboardInterrupt:
            raise

    # If max attempts reached, return default
    print_warning(f"Max attempts reached, using default: {'yes' if default else 'no'}")
    return default


def get_multiline_input(prompt: str) -> str:
    """Get multiline input from user."""
    print(f"{Colors.CYAN}{prompt}")
    print(f"(Press Enter twice to finish):{Colors.END}")

    lines = []
    empty_count = 0

    try:
        while True:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
    except EOFError:
        # Handle Ctrl+D or EOF
        pass
    except KeyboardInterrupt:
        # Re-raise KeyboardInterrupt to be handled by main
        raise

    return '\n'.join(lines)


def get_list_input(prompt: str) -> List[str]:
    """Get comma-separated list input."""
    try:
        value = get_input(prompt, required=False)
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    except Exception as e:
        print_warning(f"Error parsing list input: {e}")
        return []


def validate_benchmark_name(name: str) -> tuple[bool, str]:
    """Validate benchmark name (must be lowercase with underscores)."""
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        return False, "Benchmark name must start with a letter and contain only lowercase letters, numbers, and underscores."
    return True, ""


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to CamelCase."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def collect_benchmark_info() -> Dict:
    """Collect all benchmark information from user."""
    print_header("Create New Benchmark")

    info = {}

    # Benchmark name (directory name)
    print(f"{Colors.BOLD}Directory Name Guidelines:{Colors.END}")
    print("  • Name should describe the SOURCE, not the task")
    print("  • Use short, descriptive names (e.g., 'personal_letters', 'company_registers')")
    print("  • Bad example: 'date_recognition' (describes task, not source)")
    print("  • Good example: 'personal_letters' (describes source)")
    print(f"  {Colors.YELLOW}• Folder names cannot be changed later - choose carefully!{Colors.END}")
    print()

    while True:
        name = get_input("Benchmark directory name (e.g., personal_letters)")
        valid, error_msg = validate_benchmark_name(name)
        if valid:
            try:
                benchmarks_dir = Path("benchmarks")
                if (benchmarks_dir / name).exists():
                    print_error(f"Benchmark '{name}' already exists!")
                    continue
                info['name'] = name
                info['class_name'] = to_camel_case(name)
                print_info(f"Class name will be: {info['class_name']}")
                break
            except Exception as e:
                print_error(f"Error checking directory: {e}")
                continue
        else:
            print_error(error_msg)

    # Title and description
    print_info("\nBasic Information:")
    info['title'] = get_input("Full title")
    info['title_short'] = get_input("Short title", default=info['title'][:50])

    print()
    print(f"{Colors.BOLD}Description should briefly describe:{Colors.END}")
    print("  1. The SOURCES (what kind of documents/materials)")
    print("  2. The TASK (what needs to be extracted/analyzed)")
    info['description'] = get_multiline_input("Description")

    # Tags
    print_info("\nTags - Select from these categories:")
    print(f"{Colors.BOLD}Source Type:{Colors.END} index-cards, letter-pages, manuscript-pages, book-pages, registers, lists, ...")
    print(f"{Colors.BOLD}Structure:{Colors.END} text-like, list-like, table-like, mixed, ...")
    print(f"{Colors.BOLD}Text Type:{Colors.END} handwritten-source, typed-source, printed-source, ...")
    print(f"{Colors.BOLD}Century:{Colors.END} century-16th, century-17th, century-18th, century-19th, century-20th, ...")
    print(f"{Colors.BOLD}Task:{Colors.END} ner-extraction, metadata-extraction, transcription, classification, ...")
    print()
    print("Enter tags as comma-separated values (e.g., 'letter-pages, handwritten-source, century-19th, ner-extraction')")
    info['tags'] = get_list_input("Tags")

    # Contributors
    print_info("\nContributors:")
    print(f"Contributor IDs use format: {Colors.BOLD}firstname_lastname{Colors.END}")
    print("(Details of non-existing users can be added later)")
    print()

    contributors = []
    roles = ["Domain Expert", "Data Curator", "Annotator", "Analyst", "Engineer"]

    print("Available roles:")
    for i, role in enumerate(roles, 1):
        print(f"  {i}. {role}")
    print()

    add_contributors = get_yes_no("Add contributors?", default=True)
    while add_contributors:
        role_idx = get_int_input("Select role number", default=1, min_val=1, max_val=len(roles)) - 1
        role = roles[role_idx]
        user_ids = get_list_input(f"User IDs for {role} (e.g., john_doe, jane_smith)")
        if user_ids:
            contributors.append({
                "role": role,
                "contributors": user_ids
            })
        add_contributors = get_yes_no("Add more contributors?", default=False)

    info['contributors'] = contributors

    # Scoring configuration (default values)
    info['ranking_metric'] = 'fuzzy'
    info['ranking_order'] = 'desc'
    print_info("\nScoring Configuration: Using default (fuzzy/descending)")
    print("(This can be customized later in meta.json)")

    # Dataclass
    print()
    print(f"{Colors.BOLD}Dataclass/Schema:{Colors.END}")
    print("A dataclass defines the expected structure of the model's output using Pydantic.")
    print("This enables automatic validation and ensures consistent output format.")
    print(f"{Colors.GREEN}Strongly recommended: Use a dataclass for structured outputs.{Colors.END}")
    print()
    info['use_dataclass'] = get_yes_no("Use a structured dataclass/schema?", default=True)
    if info['use_dataclass']:
        print()
        print(f"{Colors.BOLD}Dataclass Name Guidelines:{Colors.END}")
        print("  • Should reflect the contents of the result")
        print("  • If you process pages, the result might be 'Page'")
        print("  • If you process letters, the result might be 'Letter'")
        print("  • Use CamelCase (e.g., 'Document', 'CompanyEntry', 'LetterMetadata')")
        info['dataclass_name'] = get_input("Main dataclass name", default="Document")

    # Image-based or text-based
    info['use_images'] = get_yes_no("Will this benchmark use images?", default=True)
    info['use_texts'] = get_yes_no("Will this benchmark use text files?", default=False)

    # Default prompt
    print_info("\nDefault Prompt:")
    print("(This prompt will be saved in prompts/prompt.txt and can be edited later)")
    info['default_prompt'] = get_multiline_input("Enter default prompt text")

    # Default role description
    print()
    info['role_description'] = get_input("Default role description",
                                         default="You are a historian analyzing historical documents.")

    return info


def display_configuration(info: Dict):
    """Display all collected information."""
    print_header("Benchmark Configuration")

    print(f"{Colors.BOLD}1. Benchmark Name:{Colors.END} {info['name']}")
    print(f"   {Colors.BOLD}Class Name:{Colors.END} {info['class_name']}")
    print(f"{Colors.BOLD}2. Title:{Colors.END} {info['title']}")
    print(f"{Colors.BOLD}3. Short Title:{Colors.END} {info['title_short']}")
    print(f"{Colors.BOLD}4. Description:{Colors.END}")
    desc_preview = info['description'][:150] + ('...' if len(info['description']) > 150 else '')
    print(f"   {desc_preview}")
    print(f"{Colors.BOLD}5. Tags:{Colors.END} {', '.join(info['tags']) if info['tags'] else 'None'}")
    print(f"{Colors.BOLD}6. Contributors:{Colors.END}")
    if info['contributors']:
        for contrib in info['contributors']:
            print(f"   - {contrib['role']}: {', '.join(contrib['contributors'])}")
    else:
        print("   None")
    print(f"{Colors.BOLD}7. Ranking Metric:{Colors.END} {info['ranking_metric']} ({info['ranking_order']})")
    print(f"{Colors.BOLD}8. Use Dataclass:{Colors.END} {'Yes' if info['use_dataclass'] else 'No'}")
    if info['use_dataclass']:
        print(f"   {Colors.BOLD}Dataclass Name:{Colors.END} {info['dataclass_name']}")
    print(f"{Colors.BOLD}9. Use Images:{Colors.END} {'Yes' if info['use_images'] else 'No'}")
    print(f"{Colors.BOLD}10. Use Text Files:{Colors.END} {'Yes' if info['use_texts'] else 'No'}")
    print(f"{Colors.BOLD}11. Role Description:{Colors.END}")
    print(f"   {info['role_description']}")
    print(f"{Colors.BOLD}12. Default Prompt:{Colors.END}")
    prompt_preview = info['default_prompt'][:150] + ('...' if len(info['default_prompt']) > 150 else '')
    print(f"   {prompt_preview}")
    print()


def edit_configuration(info: Dict) -> Dict:
    """Allow user to edit configuration before finalizing."""
    while True:
        display_configuration(info)

        print(f"{Colors.YELLOW}Options:{Colors.END}")
        print("  • Enter a number (1-12) to edit that field")
        print("  • Enter 'c' to continue and create benchmark")
        print("  • Enter 'q' to quit without creating")
        print()

        choice = input(f"{Colors.CYAN}Your choice:{Colors.END} ").strip().lower()

        if choice == 'c':
            return info
        elif choice == 'q':
            return None
        elif choice == '1':
            print()
            print_warning("Benchmark name cannot be changed. Please cancel and start over if needed.")
        elif choice == '2':
            info['title'] = get_input("Full title", default=info['title'])
        elif choice == '3':
            info['title_short'] = get_input("Short title", default=info['title_short'])
        elif choice == '4':
            print()
            print(f"{Colors.BOLD}Current description:{Colors.END}")
            print(info['description'])
            print()
            if get_yes_no("Edit description?", default=True):
                info['description'] = get_multiline_input("New description")
        elif choice == '5':
            print()
            print(f"{Colors.BOLD}Current tags:{Colors.END} {', '.join(info['tags'])}")
            print_info("Tag categories:")
            print("  Source Type: index-cards, letter-pages, manuscript-pages, ...")
            print("  Structure: text-like, list-like, table-like, ...")
            print("  Text Type: handwritten-source, typed-source, printed-source, ...")
            print("  Century: century-16th, century-17th, century-18th, ...")
            print("  Task: ner-extraction, metadata-extraction, transcription, ...")
            info['tags'] = get_list_input("New tags (comma-separated)")
        elif choice == '6':
            print()
            print(f"{Colors.BOLD}Current contributors:{Colors.END}")
            for contrib in info['contributors']:
                print(f"  - {contrib['role']}: {', '.join(contrib['contributors'])}")
            if get_yes_no("Re-enter all contributors?", default=True):
                contributors = []
                roles = ["Domain Expert", "Data Curator", "Annotator", "Analyst", "Engineer"]
                print("\nAvailable roles:")
                for i, role in enumerate(roles, 1):
                    print(f"  {i}. {role}")
                print()
                add_contributors = True
                while add_contributors:
                    role_idx = get_int_input("Select role number", default=1, min_val=1, max_val=len(roles)) - 1
                    role = roles[role_idx]
                    user_ids = get_list_input(f"User IDs for {role} (e.g., john_doe, jane_smith)")
                    if user_ids:
                        contributors.append({
                            "role": role,
                            "contributors": user_ids
                        })
                    add_contributors = get_yes_no("Add more contributors?", default=False)
                info['contributors'] = contributors
        elif choice == '7':
            print()
            print("Available metrics: fuzzy, f1_macro, f1_micro, exact")
            new_metric = get_input("Ranking metric", default=info['ranking_metric'])
            if new_metric in ['fuzzy', 'f1_macro', 'f1_micro', 'exact']:
                info['ranking_metric'] = new_metric
            new_order = get_input("Ranking order (desc/asc)", default=info['ranking_order'])
            if new_order in ['desc', 'asc']:
                info['ranking_order'] = new_order
        elif choice == '8':
            info['use_dataclass'] = get_yes_no("Use a structured dataclass/schema?",
                                              default=info['use_dataclass'])
            if info['use_dataclass']:
                info['dataclass_name'] = get_input("Dataclass name",
                                                   default=info.get('dataclass_name', 'Document'))
            elif 'dataclass_name' in info:
                del info['dataclass_name']
        elif choice == '9':
            info['use_images'] = get_yes_no("Use images?", default=info['use_images'])
        elif choice == '10':
            info['use_texts'] = get_yes_no("Use text files?", default=info['use_texts'])
        elif choice == '11':
            info['role_description'] = get_input("Role description", default=info['role_description'])
        elif choice == '12':
            print()
            print(f"{Colors.BOLD}Current prompt:{Colors.END}")
            print(info['default_prompt'])
            print()
            if get_yes_no("Edit prompt?", default=True):
                info['default_prompt'] = get_multiline_input("New prompt")
        else:
            print_error("Invalid choice. Please enter a number 1-12, 'c' to continue, or 'q' to quit.")

        print()


def generate_meta_json(info: Dict) -> str:
    """Generate meta.json content."""
    meta = {
        "title": info['title'],
        "title_short": info['title_short'],
        "description": info['description'],
        "tags": info['tags'],
        "contributors": info['contributors'],
        "ranking": {
            "metric": info['ranking_metric'],
            "order": info['ranking_order']
        }
    }

    return json.dumps(meta, indent=2, ensure_ascii=False)


def generate_benchmark_py(info: Dict) -> str:
    """Generate benchmark.py content."""
    template = f'''"""Benchmark implementation for {info['title']}.

{info['description']}
"""

from typing import Dict, List
from scripts.benchmark_base import Benchmark


class {info['class_name']}(Benchmark):
    """Benchmark for {info['title']}."""

    def score_request_answer(self, image_name: str, response: dict, ground_truth: dict) -> dict:
        """Score a single request against ground truth.

        Args:
            image_name: Name of the image/file being processed
            response: The model's response (parsed JSON)
            ground_truth: The expected ground truth (parsed JSON)

        Returns:
            Dictionary containing scores for this request
        """
        # TODO: Implement scoring logic
        # Example structure:
        scores = {{
            "image_name": image_name,
            "score": 0.0,
            # Add more metrics as needed
        }}

        return scores

    def score_benchmark(self, all_scores: list) -> dict:
        """Aggregate scores from all requests.

        Args:
            all_scores: List of score dictionaries from score_request_answer

        Returns:
            Dictionary containing aggregated benchmark scores
        """
        # TODO: Implement aggregation logic
        if not all_scores:
            return {{"overall_score": 0.0}}

        # Calculate average score
        avg_score = sum(s.get("score", 0.0) for s in all_scores) / len(all_scores)

        return {{
            "overall_score": avg_score,
            "num_samples": len(all_scores),
            # Add more aggregated metrics as needed
        }}

    # Optional: Override these methods if needed

    # def remove_none_values(self) -> bool:
    #     """Whether to remove None values from parsed responses."""
    #     return True

    # def convert_result_to_json(self) -> bool:
    #     """Whether to convert response to JSON before scoring."""
    #     return True

    # def get_title(self) -> str:
    #     """Get benchmark title."""
    #     return "{info['title']}"
'''

    return template


def generate_dataclass_py(info: Dict) -> str:
    """Generate dataclass.py content."""
    if not info['use_dataclass']:
        return ""

    class_name = info['dataclass_name']

    template = f'''"""Pydantic models for {info['title']} benchmark output validation.

This module defines the expected structure of model outputs.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class {class_name}(BaseModel):
    """Main output structure for {info['title']}."""

    # TODO: Define your schema fields here
    # Example:
    # field_name: str = Field(description="Description of this field")
    # items: List[str] = Field(default_factory=list)
    # metadata: Optional[Dict[str, Any]] = None

    pass


# Add additional models as needed:
#
# class SubItem(BaseModel):
#     """Sub-item structure."""
#     name: str
#     value: str
'''

    return template


def generate_readme(info: Dict) -> str:
    """Generate README.md content."""
    template = f'''# {info['title']}

## Overview

{info['description']}

## Benchmark Structure

**Tags:** {', '.join(info['tags']) if info['tags'] else 'None'}

**Scoring Metric:** {info['ranking_metric']} ({info['ranking_order']}ending)

## Data

'''

    if info['use_images']:
        template += "- **Images:** Store images in the `images/` directory\n"
    if info['use_texts']:
        template += "- **Texts:** Store text files in the `texts/` directory\n"

    template += "- **Ground Truths:** Store JSON ground truth files in `ground_truths/` directory\n"
    template += "  - Each ground truth filename must match the corresponding image/text filename (minus extension)\n\n"

    template += '''## Ground Truth Format

```json
{
  "field1": "value1",
  "field2": ["item1", "item2"]
}
```

## Scoring

TODO: Describe how scoring works for this benchmark.

## Examples

TODO: Add example inputs and expected outputs.

## Contributors

'''

    if info['contributors']:
        for contrib in info['contributors']:
            template += f"- **{contrib['role']}:** {', '.join(contrib['contributors'])}\n"
    else:
        template += "TODO: Add contributors\n"

    return template


def generate_prompt_txt(info: Dict) -> str:
    """Generate prompt.txt content."""
    return info['default_prompt']


def create_benchmark_structure(info: Dict) -> bool:
    """Create all directories and files for the benchmark."""
    benchmark_dir = None
    try:
        benchmark_dir = Path("benchmarks") / info['name']

        # Create main directory
        print_info(f"Creating directory: {benchmark_dir}")
        benchmark_dir.mkdir(parents=True, exist_ok=False)

        # Create subdirectories
        subdirs = ['prompts', 'ground_truths']
        if info['use_images']:
            subdirs.append('images')
        if info['use_texts']:
            subdirs.append('texts')

        for subdir in subdirs:
            subdir_path = benchmark_dir / subdir
            print_info(f"Creating directory: {subdir_path}")
            subdir_path.mkdir(exist_ok=True)

        # Create files
        files = {
            'meta.json': generate_meta_json(info),
            'benchmark.py': generate_benchmark_py(info),
            'README.md': generate_readme(info),
            'prompts/prompt.txt': generate_prompt_txt(info),
        }

        if info['use_dataclass']:
            files['dataclass.py'] = generate_dataclass_py(info)

        for filename, content in files.items():
            file_path = benchmark_dir / filename
            print_info(f"Creating file: {file_path}")
            file_path.write_text(content, encoding='utf-8')

        # Create placeholder files
        if info['use_images']:
            placeholder = benchmark_dir / 'images' / '.gitkeep'
            placeholder.write_text('# Add your images here\n')

        if info['use_texts']:
            placeholder = benchmark_dir / 'texts' / '.gitkeep'
            placeholder.write_text('# Add your text files here\n')

        placeholder = benchmark_dir / 'ground_truths' / '.gitkeep'
        placeholder.write_text('# Add your ground truth JSON files here\n')

        print_success(f"\nBenchmark structure created successfully at: {benchmark_dir}")
        return True

    except FileExistsError:
        print_error(f"Directory already exists: {benchmark_dir}")
        return False
    except PermissionError:
        print_error(f"Permission denied when creating files. Check your permissions.")
        return False
    except OSError as e:
        print_error(f"Filesystem error: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error creating benchmark structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_next_steps(info: Dict):
    """Print next steps for the user."""
    print_header("Next Steps")

    print(f"{Colors.BOLD}1. Add your data:{Colors.END}")
    if info['use_images']:
        print(f"   - Add images to: benchmarks/{info['name']}/images/")
    if info['use_texts']:
        print(f"   - Add text files to: benchmarks/{info['name']}/texts/")
    print(f"   - Add ground truth JSON files to: benchmarks/{info['name']}/ground_truths/")
    print(f"     (Filenames must match your image/text filenames)")

    print(f"\n{Colors.BOLD}2. Implement scoring logic:{Colors.END}")
    print(f"   - Edit: benchmarks/{info['name']}/benchmark.py")
    print(f"   - Implement: score_request_answer() and score_benchmark()")

    if info['use_dataclass']:
        print(f"\n{Colors.BOLD}3. Define your data schema:{Colors.END}")
        print(f"   - Edit: benchmarks/{info['name']}/dataclass.py")
        print(f"   - Add fields to the {info['dataclass_name']} class")

    print(f"\n{Colors.BOLD}4. Create and run tests:{Colors.END}")
    print(f"   - Use the benchmark testing CLI to create test configurations")
    print(f"   - Tests can be run against different models and providers")

    print(f"\n{Colors.BOLD}5. Review and refine:{Colors.END}")
    print(f"   - Check README: benchmarks/{info['name']}/README.md")
    print(f"   - Adjust prompt: benchmarks/{info['name']}/prompts/prompt.txt")

    print(f"\n{Colors.GREEN}{Colors.BOLD}Benchmark '{info['name']}' is ready for development!{Colors.END}\n")


def main():
    """Main CLI entry point."""
    try:
        # Collect information
        info = collect_benchmark_info()

        # Allow editing and confirm
        info = edit_configuration(info)
        if info is None:
            print_warning("Benchmark creation cancelled.")
            return

        # Create structure
        if not create_benchmark_structure(info):
            print_error("Failed to create benchmark structure.")
            return

        # Print next steps
        print_next_steps(info)

    except KeyboardInterrupt:
        print_warning("\n\nBenchmark creation cancelled by user.")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
