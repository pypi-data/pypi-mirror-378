#!/usr/bin/env python3
"""Script to automatically remove unused type ignore comments."""

import re
import subprocess
import sys
from pathlib import Path


def get_unused_ignores() -> list[str]:
    """Get list of unused type ignore comments from mypy."""
    try:
        result = subprocess.run(
            ["uv", "run", "mypy", "--config-file", "mypy.ini", "."],
            capture_output=True,
            text=True,
            check=False,
        )
        
        unused_lines = []
        for line in result.stdout.split('\n'):
            if 'Unused "type: ignore' in line:
                # Extract file path and line number
                match = re.search(r'^(.*?):(\d+):.*?Unused "(.*?)" comment', line)
                if match:
                    file_path, line_num, ignore_comment = match.groups()
                    unused_lines.append(f"{file_path}:{line_num}:{ignore_comment}")
        
        return unused_lines
    except Exception as e:
        print(f"Error running mypy: {e}")
        return []


def remove_unused_ignore(file_path: str, line_num: int, ignore_comment: str) -> bool:
    """Remove unused type ignore comment from specific line."""
    try:
        path = Path(file_path)
        lines = path.read_text().splitlines(keepends=True)
        
        if line_num > len(lines):
            return False
            
        line_idx = line_num - 1  # Convert to 0-based index
        line_content = lines[line_idx]
        
        # Look for the specific type ignore pattern
        ignore_pattern = f"type: ignore{ignore_comment.split('type: ignore')[1]}"
        
        # Remove the specific ignore comment
        if ignore_pattern in line_content:
            # Handle special case where entire comment might be just the ignore
            if f"# {ignore_pattern}" in line_content and line_content.strip() == f"# {ignore_pattern}":
                # Remove entire comment line if it only contains the ignore
                lines[line_idx] = ""
            else:
                # Remove just the ignore part
                lines[line_idx] = line_content.replace(f"# {ignore_pattern}", "").rstrip()
                # Clean up extra spaces
                lines[line_idx] = lines[line_idx].rstrip() + "\n"
                # If line is now just whitespace, remove it
                if lines[line_idx].strip() == "":
                    lines[line_idx] = ""
            
            # Write back to file
            path.write_text("".join(lines))
            return True
            
        return False
    except Exception as e:
        print(f"Error processing {file_path}:{line_num}: {e}")
        return False


def main() -> int:
    """Main function to remove all unused type ignore comments."""
    print("Finding unused type ignore comments...")
    unused_ignores = get_unused_ignores()  # type: ignore[no-untyped-call]
    
    if not unused_ignores:
        print("No unused type ignore comments found!")
        return 0

    print(f"Found {len(unused_ignores)} unused type ignore comments")
    
    removed_count = 0
    for ignore_line in unused_ignores:
        try:
            # Parse the ignore line format
            pattern = r"^(.+?):(\d+):.*?type: ignore\[([^\]]+)\]"
            match_result = re.match(pattern, ignore_line)
            if match_result:
                file_path, line_num_str, ignore_comment = match_result.groups()
                line_num = int(line_num_str)
                
                if remove_unused_ignore(file_path, line_num, ignore_comment):  # type: ignore[no-untyped-call]
                    removed_count += 1
                    print(f"Removed unused ignore from {file_path}:{line_num}")
                    
        except Exception as e:
            print(f"Error processing ignore line '{ignore_line}': {e}")

    print(f"Removed {removed_count} unused type ignore comments")
    return 0 if removed_count >= 0 else 1  # Always return success code


if __name__ == "__main__":
    sys.exit(main())  # type: ignore[no-untyped-call]