import os

with open('translate.py', 'w') as f:
    f.write('''
import os
import yaml
import sys
from argparse import Namespace
from MarkdownTranslator import MdTranslater

def main():
    config_path = '.github/config.yml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    args = Namespace(**config)
    translator = MdTranslater(args)
    translator.run()

if __name__ == "__main__":
    main()
''')
