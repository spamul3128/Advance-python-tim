#!/bin/bash
export PATH="$PATH:/Users/spamul002c/Library/Python/3.9/bin"

BASE="/Users/spamul002c/python/Advance-python-tim"

find "$BASE" -name "README.md" -not -path "*/node_modules/*" | while read -r readme; do
    dir=$(dirname "$readme")
    project=$(basename "$dir")
    output="$dir/${project}.pdf"
    echo "Converting: $readme -> $output"
    mdpdf -o "$output" "$readme" 2>&1
done

echo ""
echo "Done! All README.md files have been converted to PDF."

