import os
import textwrap
import sys

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import yaml
        import sys
        from argparse import Namespace

        # Füge den Pfad zu Free-Markdown-Translator/src zum sys.path hinzu
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        from MarkdownTranslator import MdTranslater

        def main():
            config_path = 'config.yaml'
            if not os.path.exists(config_path):
                print(f"Error: {config_path} not found", file=sys.stderr)
                sys.exit(1)
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error: Failed to parse {config_path}: {e}", file=sys.stderr)
                sys.exit(1)
            
            if not config:
                print(f"Error: {config_path} is empty or invalid", file=sys.stderr)
                sys.exit(1)
                
            args = Namespace(**config)
            try:
                translator = MdTranslater(args)
                translator.process_file()  # Verwende process_file()
            except Exception as e:
                print(f"Error during translation: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))