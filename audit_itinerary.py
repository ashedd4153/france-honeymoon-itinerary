import re
import sys
from pathlib import Path
from typing import List, Dict, Set

def get_slug(header_text: str) -> str:
    """
    Simulates GitHub-style markdown header slugification.
    - Lowercase
    - Remove non-alphanumeric chars (except spaces/hyphens)
    - Replace spaces with hyphens
    """
    # Remove all non-word characters (everything except numbers and letters)
    # text = re.sub(r'[^\w\s-]', '', header_text.lower())
    # Actually, GitHub allows some chars but strips others.
    # A simplified version that works for standard ASCII headers:
    text = header_text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text

def audit_file(file_path: Path) -> List[str]:
    errors = []
    content = file_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    # Map slug -> context text (the header title or the line containing the anchor)
    targets: Dict[str, str] = {}

    # 1. Find all Headers
    header_pattern = re.compile(r'^(#+)\s+(.+)$')
    # 2. Find HTML Anchors <span id="slug"> or <a name="slug">
    anchor_pattern = re.compile(r'<(?:a|div|span)[^>]+(?:name|id)=["\']([^"\']+)["\']', re.IGNORECASE)

    for line in lines:
        # Check for Header
        h_match = header_pattern.match(line)
        if h_match:
            header_text = h_match.group(2)
            slug = get_slug(header_text)
            targets[slug] = header_text
            continue

        # Check for Anchors in line
        for a_match in anchor_pattern.finditer(line):
            slug = a_match.group(1)
            # Use the entire line as context (strip HTML tags for cleaner matching later if we wanted, 
            # but raw text is usually fine for "contains" checks)
            targets[slug] = line

    # 3. Check Internal Links
    link_pattern = re.compile(r'\[([^\]]+)\]\(#([^)]+)\)')
    
    for i, line in enumerate(lines, 1):
        for match in link_pattern.finditer(line):
            link_text = match.group(1).strip()
            target_slug = match.group(2)
            
            # Skip ignored slugs
            if target_slug in ["top", "overview", "itinerary", "detailed-daily-itinerary"]: 
                continue

            if target_slug not in targets:
                errors.append(f"Line {i}: 🚫 Broken Link `[{link_text}](#{target_slug})` - Target not found.")
            else:
                # Semantic Check: Does the link text appear in the target context?
                # Normalize both: lowercase, basic cleanup
                n_link = link_text.lower()
                n_target = targets[target_slug].lower()
                
                # Loose check: if the link text acts like "Here" or "Day 1", we might skip.
                # But for granular items "Holybelly", it should be in the target line.
                if len(n_link) > 3 and n_link not in n_target:
                     # Check if it's a known non-matching type (e.g. "Day 1" linking to a date title)
                     # For now, flag it as a warning
                     errors.append(f"Line {i}: ⚠️ Semantic Mismatch? `[{link_text}](#{target_slug})` points to text: \"{targets[target_slug].strip()[:50]}...\"")

def main():
    base_dir = Path(__file__).parent
    md_files = list(base_dir.glob("*.md"))
    
    total_errors = 0
    print(f"🔍 Scanning {len(md_files)} markdown files for broken internal links...\n")
    
    for md_file in md_files:
        if md_file.name == "README.md": continue # Skip README usually
        
        errors = audit_file(md_file)
        if errors:
            print(f"❌ {md_file.name}: {len(errors)} broken links")
            for err in errors:
                print(f"   - {err}")
            total_errors += len(errors)
        else:
            print(f"✅ {md_file.name}: OK")
            
    print("-" * 40)
    if total_errors > 0:
        print(f"🚫 FAILED: Found {total_errors} broken links.")
        sys.exit(1)
    else:
        print("✨ SUCCESS: All internal links valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()
