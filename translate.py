import os
import argparse
import glob
from transformers import pipeline

def translate_markdown_file(file_path, translator):
    """Translates the content of a single Markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple approach: translate line by line.
    # For complex Markdown (e.g., lists spanning lines, tables),
    # a more robust Markdown parser might be needed to preserve structure.
    lines = content.split('\n')
    translated_lines = []
    for line in lines:
        if line.strip().startswith(('!', '#', '[', '>', '---', '```')):
            # Heuristics to skip or keep Markdown syntax elements as is
            # (e.g., images, links, headings, blockquotes, horizontal rules, code blocks)
            translated_lines.append(line)
        elif not line.strip():
            # Keep empty lines as is
            translated_lines.append(line)
        else:
            # Translate actual text lines
            try:
                # The translation pipeline typically returns a list of dicts
                # e.g., [{'translation_text': 'Translated text.'}]
                translation_result = translator(line)
                translated_lines.append(translation_result[0]['translation_text'])
            except Exception as e:
                print(f"Warning: Could not translate line in {file_path}: '{line.strip()}'. Error: {e}")
                translated_lines.append(line) # Fallback: keep original line

    return '\n'.join(translated_lines)

def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files from German to English.")
    parser.add_argument('--input-dir', type=str, required=True,
                        help="Input directory containing German Markdown files.")
    parser.add_argument('--output-dir', type=str, required=True,
                        help="Output directory to save translated English Markdown files.")
    args = parser.parse_args()

    # Initialize the translation pipeline
    # We use 'Helsinki-NLP/opus-mt-de-en' for German to English
    print("Loading translation model (Helsinki-NLP/opus-mt-de-en)...")
    translator = pipeline("translation_de_to_en", model="Helsinki-NLP/opus-mt-de-en")
    print("Model loaded.")

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Find all Markdown files in the input directory
    md_files = glob.glob(os.path.join(args.input_dir, '**', '*.md'), recursive=True)
    
    if not md_files:
        print(f"No Markdown files found in {args.input_dir}. Exiting.")
        return

    print(f"Found {len(md_files)} Markdown files in '{args.input_dir}'.")

    for md_file_path in md_files:
        relative_path = os.path.relpath(md_file_path, args.input_dir)
        output_file_path = os.path.join(args.output_dir, relative_path)
        
        # Ensure output subdirectory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        print(f"Translating '{md_file_path}' to '{output_file_path}'...")
        translated_content = translate_markdown_file(md_file_path, translator)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        print("Done.")

if __name__ == "__main__":
    main()