# HowTo: Automate Translation of German Markdown Files to English with GitHub Actions

This guide provides a step-by-step process to set up a GitHub Actions CI/CD pipeline that automatically translates German Markdown (*.md*) files into English. The pipeline is triggered when a Markdown file in a `DE/` directory is added or modified, uses the DeepL API for translation, and saves the translated files in an `EN/` directory. The translated files are then committed to the repository.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **GitHub Repository**: A repository containing your German Markdown files in a `DE/` directory.
- **DeepL API Key**: Sign up for a DeepL API account (https://www.deepl.com/pro-api) to obtain an API key (free tier available with limits, or paid for higher usage).
- **Python Knowledge**: Basic understanding of Python for the translation script (optional, as the provided script is ready to use).
- **GitHub Actions**: Familiarity with GitHub Actions workflows (basic setup is explained below).

## Overview
The pipeline performs the following tasks:
1. Detects changes to Markdown files in the `DE/` directory.
2. Uses a Python script to read each German Markdown file and translate it using the DeepL API.
3. Saves the translated file in the `EN/` directory with the same filename.
4. Commits and pushes the translated files to the repository.
5. (Optional) Creates a pull request for review instead of directly pushing changes.

## Step-by-Step Instructions

### Step 1: Set Up the DeepL API Key
1. **Obtain a DeepL API Key**:
   - Register at https://www.deepl.com/pro-api and create an API key.
   - Note the key for use in GitHub Secrets.
2. **Store the API Key in GitHub Secrets**:
   - Go to your GitHub repository.
   - Navigate to `Settings > Secrets and variables > Actions > New repository secret`.
   - Add a secret named `DEEPL_API_KEY` with your DeepL API key as the value.

### Step 2: Create the Repository Structure
Organize your repository as follows:
```plaintext
├── .github/
│   ├── scripts/
│   │   └── translate_md.py  # Python script for translation
│   └── workflows/
│       └── translate_md.yml  # GitHub Actions workflow
├── DE/
│   └── example.md  # German Markdown files
├── EN/
│   └── example.md  # Translated English Markdown files (auto-generated)
```
- Create a `DE/` directory for German Markdown files.
- The `EN/` directory will be created automatically by the pipeline if it doesn’t exist.

### Step 3: Create the Translation Script
Create a Python script to handle the translation of Markdown files using the DeepL API. Save it as `.github/scripts/translate_md.py`:

```python
import os
import requests
import glob

# DeepL API configuration
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate'

def translate_text(text, source_lang='DE', target_lang='EN'):
    """Translate text using DeepL API."""
    headers = {
        'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}'
    }
    data = {
        'text': text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'preserve_formatting': 1  # Preserve Markdown formatting
    }
    response = requests.post(DEEPL_API_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['translations'][0]['text']

def translate_markdown_file(input_file, output_file):
    """Translate a Markdown file while preserving structure."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content into chunks to avoid API limits (e.g., 128 KB per request)
    max_chunk_size = 5000  # Adjust based on API limits
    chunks = [content[i:i + max_chunk_size] for i in range(0, len(content), max_chunk_size)]
    translated_chunks = [translate_text(chunk) for chunk in chunks]

    # Combine translated chunks
    translated_content = ''.join(translated_chunks)

    # Write to output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)

def main():
    """Process all Markdown files in DE/ and save translations in EN/."""
    for input_file in glob.glob('DE/*.md'):
        # Generate output file path (e.g., DE/HowTo.md -> EN/HowTo.md)
        output_file = input_file.replace('DE/', 'EN/')
        print(f"Translating {input_file} to {output_file}")
        translate_markdown_file(input_file, output_file)

if __name__ == '__main__':
    main()
```

This script:
- Reads all *.md* files in the `DE/` directory.
- Translates the content using the DeepL API, preserving Markdown formatting.
- Saves the translated files in the `EN/` directory.

### Step 4: Create the GitHub Actions Workflow
Create a workflow file to automate the translation process. Save it as `.github/workflows/translate_md.yml`:

```yaml
name: Translate Markdown from German to English

on:
  push:
    branches:
      - main
    paths:
      - 'DE/**.md'  # Trigger only for changes in DE/*.md files
  pull_request:
    branches:
      - main
    paths:
      - 'DE/**.md'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install requests

      - name: Create EN directory if it doesn't exist
        run: mkdir -p EN

      - name: Translate Markdown files
        env:
          DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
        run: |
          python .github/scripts/translate_md.py

      - name: Commit translated files
        run: |
          git config --global user.name 'GitHub Action'
          git config --global user.email 'action@github.com'
          git add EN/*.md
          git diff --staged --quiet || git commit -m "Add translated Markdown files"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This workflow:
- Triggers on pushes or pull requests affecting files in `DE/*.md`.
- Sets up a Python environment and installs the `requests` library.
- Runs the translation script.
- Commits and pushes the translated files to the `EN/` directory.

### Step 5: (Optional) Use Pull Requests Instead of Direct Push
To create a pull request for the translated files instead of directly pushing them, replace the `Commit translated files` step with:

```yaml
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "Add translated Markdown files"
          branch: "translated-files"
          title: "Add translated Markdown files"
          body: "Automated translation of Markdown files from DE to EN."
          token: ${{ secrets.GITHUB_TOKEN }}
```

This creates a new branch (`translated-files`) and opens a pull request for review.

### Step 6: Test the Pipeline
1. **Add a German Markdown File**:
   - Create a file like `DE/test.md` with some German content, e.g.:
     ```markdown
     # Beispielüberschrift
     Dies ist ein Testdokument auf Deutsch.
     ```
   - Commit and push the file to the `main` branch.
2. **Monitor the Pipeline**:
   - Go to the `Actions` tab in your GitHub repository to check the workflow execution.
   - Verify that a corresponding `EN/test.md` file is created with the translated content.
3. **Check the Translation**:
   - Ensure the translated file in `EN/` is correctly formatted and accurately translated.

### Troubleshooting
- **API Key Issues**: Verify that the `DEEPL_API_KEY` is correctly set in GitHub Secrets and accessible in the workflow.
- **Markdown Formatting Errors**: If formatting (e.g., tables, code blocks) is broken, adjust the chunk size in `translate_md.py` or preprocess the Markdown to handle specific elements separately.
- **API Limits**: DeepL’s free tier has a 500,000-character limit per month. Monitor usage and consider upgrading to a paid plan for higher volumes.
- **Pipeline Failures**: Check the workflow logs in GitHub Actions for errors (e.g., network issues, invalid API responses).
- **Debugging**: Add print statements to `translate_md.py` or use verbose logging in the workflow to diagnose issues.

### Best Practices
- **Preserve Markdown Structure**:
  - DeepL’s `preserve_formatting` option helps, but test complex Markdown files (e.g., with tables or code blocks) to ensure accuracy.
  - Consider using a Markdown parser (e.g., `markdown-it` or `mistune`) to split content into translatable and non-translatable parts.
- **Handle API Limits**:
  - Split large files into smaller chunks (as shown in the script) to stay within DeepL’s request size limits (e.g., 128 KB).
  - Monitor API usage to avoid exceeding the free tier’s character limit.
- **Version Control**:
  - Ensure translated files in `EN/` remain synchronized with their `DE/` counterparts.
  - Use consistent filenames to avoid conflicts (e.g., `DE/HowTo.md` → `EN/HowTo.md`).
- **Quality Assurance**:
  - Manually review initial translations to validate quality, especially for technical or domain-specific content.
  - Consider adding a human review step via pull requests.
- **Error Handling**:
  - Add robust error handling in `translate_md.py` to manage API failures or invalid inputs.
  - Log errors in the workflow for easier debugging.

### Alternative Translation Tools
If DeepL is not suitable, consider these alternatives:
- **Google Cloud Translate**:
  - Use the `google-cloud-translate` Python library.
  - Replace the `translate_text` function in `translate_md.py` with Google Translate API calls.
  - Requires a Google Cloud project and API key.
- **Open-Source Libraries**:
  - Use `googletrans` for non-commercial projects (less reliable, unofficial API).
  - Example: `pip install googletrans==4.0.0-rc1`.
- **Custom Models**:
  - Use open-source translation models (e.g., Hugging Face’s `transformers`) for offline or custom translation, but this requires more setup and resources.

### Example Output
For an input file `DE/test.md`:
```markdown
# Beispielüberschrift
Dies ist ein Testdokument auf Deutsch.
```
The pipeline generates `EN/test.md`:
```markdown
# Example Heading
This is a test document in English.
```

## Conclusion
This GitHub Actions pipeline automates the translation of German Markdown files into English using the DeepL API. The setup is flexible and can be adapted for other languages or translation tools. By following this guide, you can streamline content translation while maintaining Markdown formatting. Ensure you securely store API keys, validate translations, and monitor API usage to optimize the process. For further details on DeepL, visit https://www.deepl.com/docs-api.