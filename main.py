# In main.py or wherever main() is defined
import argparse
import json
from src.objdump_analyzer import ObjdumpAnalyzer

def main():
    parser = argparse.ArgumentParser(description='Objdump Analyzer CLI')
    parser.add_argument('--file', '-f', required=True, help='Path to the object file')
    parser.add_argument('--arch', '-a', help='Objdump binary (e.g., riscv-objdump)')
    parser.add_argument('--register', '-r', nargs='*', help='Registers to filter by')
    parser.add_argument('--config', help='Path to JSON config file')

    args = parser.parse_args()

    config = {}
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    obj_file = args.file
    arch = args.arch or config.get('arch', 'objdump')
    registers = args.register or config.get('registers', [])

    analyzer = ObjdumpAnalyzer(obj_file, arch, registers)
    analyzer.run_objdump()