import os
import textwrap
import sys

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys
        from argparse import Namespace
        from dataclasses import asdict

        # Add Free-Markdown-Translator/src to sys.path
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        from config import get_config
        from MarkdownTranslator import MdTranslater

        def main():
            config_path = 'config.yaml'
            if not os.path.exists(config_path):
                print(f"Error: {config_path} not found", file=sys.stderr)
                sys.exit(1)
            try:
                config = get_config(config_path)
            except Exception as e:
                print(f"Error loading config: {e}", file=sys.stderr)
                sys.exit(1)
            args = Namespace(**asdict(config))
            try:
                translator = MdTranslater(args)
                translator.main()  # Call the correct method
            except Exception as e:
                print(f"Error during translation: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))