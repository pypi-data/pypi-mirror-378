#!/usr/bin/env python3

"""Format AsciiDoc spacing - ensures blank lines after headings and around include directives"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


def print_colored(message: str, color: str = Colors.NC) -> None:
    """Print message with color"""
    print(f"{color}{message}{Colors.NC}")


def process_file(file_path: Path, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Process a single AsciiDoc file to fix spacing issues.
    
    Args:
        file_path: Path to the file to process
        dry_run: If True, show what would be changed without modifying
        verbose: If True, show detailed output
    
    Returns:
        True if changes were made (or would be made in dry-run), False otherwise
    """
    if verbose:
        print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, UnicodeDecodeError) as e:
        print_colored(f"Error reading {file_path}: {e}", Colors.RED)
        return False
    
    # Remove trailing newlines from lines for processing
    lines = [line.rstrip('\n\r') for line in lines]
    
    new_lines = []
    changes_made = False
    in_block = False  # Track if we're inside a block (admonition, listing, etc.)
    in_conditional = False  # Track if we're inside a conditional block
    
    for i, current_line in enumerate(lines):
        prev_line = lines[i-1] if i > 0 else ""
        next_line = lines[i+1] if i + 1 < len(lines) else ""
        
        # Check for conditional start (ifdef:: or ifndef::)
        if re.match(r'^(ifdef::|ifndef::)', current_line):
            in_conditional = True
            # Add blank line before conditional if needed
            if (prev_line and 
                not re.match(r'^\s*$', prev_line) and
                not re.match(r'^(ifdef::|ifndef::|endif::)', prev_line)):
                new_lines.append("")
                changes_made = True
                if verbose:
                    print(f"  Added blank line before conditional block")
            new_lines.append(current_line)
        
        # Check for conditional end (endif::)
        elif re.match(r'^endif::', current_line):
            new_lines.append(current_line)
            in_conditional = False
            # Add blank line after conditional if needed
            if (next_line and 
                not re.match(r'^\s*$', next_line) and
                not re.match(r'^(ifdef::|ifndef::|endif::)', next_line)):
                new_lines.append("")
                changes_made = True
                if verbose:
                    print(f"  Added blank line after conditional block")
        
        # Check for block delimiters (====, ----, ...., ____)
        # These are used for admonitions, listing blocks, literal blocks, etc.
        elif re.match(r'^(====+|----+|\.\.\.\.+|____+)$', current_line):
            in_block = not in_block  # Toggle block state
            new_lines.append(current_line)
        # Check if current line is a heading (but not if we're in a block)
        elif not in_block and re.match(r'^=+\s+', current_line):
            new_lines.append(current_line)
            
            # Check if next line is not empty and not another heading
            if (next_line and 
                not re.match(r'^=+\s+', next_line) and 
                not re.match(r'^\s*$', next_line)):
                new_lines.append("")
                changes_made = True
                if verbose:
                    truncated = current_line[:50] + "..." if len(current_line) > 50 else current_line
                    print(f"  Added blank line after heading: {truncated}")
        
        # Check if current line is a comment (AsciiDoc comments start with //)
        elif re.match(r'^//', current_line):
            # Skip special handling if we're inside a conditional block
            if in_conditional:
                new_lines.append(current_line)
            else:
                # Check if next line is an include directive
                if next_line and re.match(r'^include::', next_line):
                    # This comment belongs to the include, add blank line before comment if needed
                    if (prev_line and 
                        not re.match(r'^\s*$', prev_line) and 
                        not re.match(r'^//', prev_line) and
                        not re.match(r'^:', prev_line)):  # Don't add if previous is attribute
                        new_lines.append("")
                        changes_made = True
                        if verbose:
                            print(f"  Added blank line before comment above include")
                new_lines.append(current_line)
        
        # Check if current line is an attribute (starts with :)
        elif re.match(r'^:', current_line):
            # Skip special handling if we're inside a conditional block
            if in_conditional:
                new_lines.append(current_line)
            else:
                # Check if next line is an include directive
                if next_line and re.match(r'^include::', next_line):
                    # This attribute belongs to the include, add blank line before attribute if needed
                    if (prev_line and 
                        not re.match(r'^\s*$', prev_line) and 
                        not re.match(r'^//', prev_line) and
                        not re.match(r'^:', prev_line)):  # Don't add if previous is comment or attribute
                        new_lines.append("")
                        changes_made = True
                        if verbose:
                            print(f"  Added blank line before attribute above include")
                new_lines.append(current_line)
        
        # Check if current line is an include directive
        elif re.match(r'^include::', current_line):
            # Skip special handling if we're inside a conditional block
            if in_conditional:
                new_lines.append(current_line)
            else:
                # Check if this is an attribute include (contains "attribute" in the path)
                is_attribute_include = 'attribute' in current_line.lower()
                
                # Check if this appears near the top of the file (within first 10 lines after H1)
                # Find the H1 heading position
                h1_position = -1
                for j in range(min(i, 10)):  # Look back up to 10 lines or to current position
                    if re.match(r'^=\s+', lines[j]):  # H1 heading starts with single =
                        h1_position = j
                        break
                
                # If this is an attribute include near the H1 heading, don't add surrounding blank lines
                is_near_h1 = h1_position >= 0 and (i - h1_position) <= 2
                
                # Check if previous line is a comment or attribute (which belongs to this include)
                has_comment_above = prev_line and re.match(r'^//', prev_line)
                has_attribute_above = prev_line and re.match(r'^:', prev_line)
                
                # If it's an attribute include near H1, only the heading's blank line is needed
                if not (is_attribute_include and is_near_h1):
                    # Don't add blank line if there's a comment or attribute above (it was handled by the comment/attribute logic)
                    if not has_comment_above and not has_attribute_above:
                        # Add blank line before include if previous line is not empty and not an include
                        if (prev_line and 
                            not re.match(r'^\s*$', prev_line) and 
                            not re.match(r'^include::', prev_line)):
                            new_lines.append("")
                            changes_made = True
                            if verbose:
                                truncated = current_line[:50] + "..." if len(current_line) > 50 else current_line
                                print(f"  Added blank line before include: {truncated}")
                
                new_lines.append(current_line)
                
                # If it's an attribute include near H1, don't add blank line after
                if not (is_attribute_include and is_near_h1):
                    # Add blank line after include if next line exists and is not empty and not an include
                    if (next_line and 
                        not re.match(r'^\s*$', next_line) and 
                        not re.match(r'^include::', next_line)):
                        new_lines.append("")
                        changes_made = True
                        if verbose:
                            truncated = current_line[:50] + "..." if len(current_line) > 50 else current_line
                            print(f"  Added blank line after include: {truncated}")
        
        else:
            new_lines.append(current_line)
    
    # Apply changes if any were made
    if changes_made:
        # Clean up any consecutive blank lines we may have added
        cleaned_lines = []
        for i, line in enumerate(new_lines):
            # Check if this is a blank line we're about to add
            if line == "":
                # Check if the previous line is also a blank line
                if i > 0 and cleaned_lines and cleaned_lines[-1] == "":
                    # Skip this blank line as we already have one
                    continue
            cleaned_lines.append(line)
        
        if dry_run:
            print_colored(f"Would modify: {file_path}", Colors.YELLOW)
        else:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in cleaned_lines:
                        f.write(line + '\n')
                print_colored(f"Modified: {file_path}", Colors.GREEN)
            except IOError as e:
                print_colored(f"Error writing {file_path}: {e}", Colors.RED)
                return False
    else:
        if verbose:
            print("  No changes needed")
    
    return changes_made


def find_adoc_files(path: Path) -> List[Path]:
    """Find all .adoc files in the given path"""
    adoc_files = []
    
    if path.is_file():
        if path.suffix == '.adoc':
            adoc_files.append(path)
        else:
            print_colored(f"Warning: {path} is not an AsciiDoc file (.adoc)", Colors.YELLOW)
    elif path.is_dir():
        adoc_files = list(path.rglob('*.adoc'))
    
    return adoc_files


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Format AsciiDoc files to ensure proper spacing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Format AsciiDoc files to ensure proper spacing:
- Blank line after headings (=, ==, ===, etc.)
- Blank lines around include:: directives

Examples:
  %(prog)s                                    # Process all .adoc files in current directory
  %(prog)s modules/                          # Process all .adoc files in modules/
  %(prog)s assemblies/my-guide.adoc          # Process single file
  %(prog)s --dry-run modules/               # Preview changes without modifying
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='File or directory to process (default: current directory)'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    # Convert path to Path object
    target_path = Path(args.path)
    
    # Check if path exists
    if not target_path.exists():
        print_colored(f"Error: Path does not exist: {target_path}", Colors.RED)
        sys.exit(1)
    
    # Display dry-run mode message
    if args.dry_run:
        print_colored("DRY RUN MODE - No files will be modified", Colors.YELLOW)
    
    # Find all AsciiDoc files
    adoc_files = find_adoc_files(target_path)
    
    if not adoc_files:
        print(f"Processed 0 AsciiDoc file(s)")
        print("AsciiDoc spacing formatting complete!")
        return
    
    # Process each file
    files_processed = 0
    for file_path in adoc_files:
        try:
            process_file(file_path, args.dry_run, args.verbose)
            files_processed += 1
        except KeyboardInterrupt:
            print_colored("\nOperation cancelled by user", Colors.YELLOW)
            sys.exit(1)
        except Exception as e:
            print_colored(f"Unexpected error processing {file_path}: {e}", Colors.RED)
    
    print(f"Processed {files_processed} AsciiDoc file(s)")
    print("AsciiDoc spacing formatting complete!")


if __name__ == "__main__":
    main()