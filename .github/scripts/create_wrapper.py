import os
import textwrap 

with open('translate.py', 'w') as f:
    f.write(textwrap.dedent(''' # <-- textwrap.dedent hinzugefügt
        import os
        import yaml
        import sys
        from argparse import Namespace
        from MarkdownTranslator import MdTranslater

        def main():
            config_path = '.github/config.yaml' # <-- Pfad ist korrekt
            if not os.path.exists(config_path): # <-- Gute Prüfung hinzugefügt
                print(f"Error: {config_path} not found")
                sys.exit(1)
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            args = Namespace(**config)
            translator = MdTranslater(args)
            translator.run()

        if __name__ == "__main__":
            main()
    '''))