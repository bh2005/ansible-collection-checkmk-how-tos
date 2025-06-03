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
            # Kopiere .github/config.yaml nach config.yaml, falls erforderlich
            config_path = '.github/config.yaml'
            root_config_path = 'config.yaml'
            if os.path.exists(config_path) and not os.path.exists(root_config_path):
                import shutil
                shutil.copyfile(config_path, root_config_path)
            
            if not os.path.exists(root_config_path):
                print(f"Error: {root_config_path} not found", file=sys.stderr)
                sys.exit(1)
            try:
                with open(root_config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error: Failed to parse {root_config_path}: {e}", file=sys.stderr)
                sys.exit(1)
            
            if not config:
                print(f"Error: {root_config_path} is empty or invalid", file=sys.stderr)
                sys.exit(1)
                
            args = Namespace(**config)
            try:
                translator = MdTranslater(args)
                translator.translate()  # Änderung von run() zu translate()
            except Exception as e:
                print(f"Error during translation: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))