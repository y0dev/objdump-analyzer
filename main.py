import os
import json
import logging
import argparse
from datetime import datetime
from src.objdump_analyzer import ObjdumpAnalyzer

DEFAULT_CONFIG = './config/default_config.json'


# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Create a timestamped log filename
log_filename = datetime.now().strftime("logs/objdump_%m_%d_%Y_%H_%M_%S.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Also output to console
    ]
)

def main():
    parser = argparse.ArgumentParser(description='Objdump Analyzer CLI')
    parser.add_argument('--file', '-f', required=True, help='Path to the object file')
    parser.add_argument('--arch', '-a', help='Objdump binary (e.g., riscv-objdump)')
    parser.add_argument('--register', '-r', nargs='*', help='Registers to filter by')
    parser.add_argument('--config', help='Path to JSON config file')

    args = parser.parse_args()
    
    config = {}
    config_file = ""
    if args.config:
        config_file = args.config
    else:
        config_file = DEFAULT_CONFIG

    with open(config_file) as f:
        config = json.load(f)

    obj_file = args.file
    arch = args.arch or config.get('arch', 'objdump')
    registers = args.register or config.get('registers', [])

    # Instantiate the analyzer
    analyzer = ObjdumpAnalyzer(obj_file, arch, registers)
    # Determine output directory and file path
    output_file_path = os.path.join(analyzer.output_dir, "objdump.txt")
    summary_file_path = os.path.join(analyzer.output_dir, "symbol_summary.txt")

    # Run objdump (creates disassembly file: output/my_binary/objdump.txt)
    analyzer.run_objdump()

    # Read disassembly lines
    with open(output_file_path, "r") as f:
        disassembly_lines = f.readlines()
    
    # Analyze function sizes
    function_sizes = analyzer.analyze_function_sizes(disassembly_lines)
    if function_sizes:
        with open(summary_file_path, "w") as out_file:
            out_file.write("=== Function Sizes ===")
            for f in function_sizes:
                out_file.write(f"{f['name']}: {f['size']} bytes (0x{f['start']} - 0x{f['end']})")
    
    symbol_path = analyzer.gen_symbol_table()
    if symbol_path:
        with open(symbol_path, "r") as f:
            symbol_lines = f.readlines()

        func_symbols = analyzer.analyze_function_symbols(symbol_lines)
        data_sections = analyzer.analyze_data_sections(symbol_lines)
        

        # Write results to the summary file
        with open(summary_file_path, "a") as out_file:
            out_file.write("=== Function Symbols ===\n")
            for fs in func_symbols:
                out_file.write(f"{fs['name']}: {fs['size']} bytes at {fs['address']}\n")

            out_file.write("\n=== Data Sections ===\n")
            for var in data_sections:
                out_file.write(f"{var['name']} ({var['section']}): {var['size']} bytes at {var['address']}\n")

        print(f"Symbol analysis written to: {summary_file_path}")

if __name__ == "__main__":
    logging.info("=== Objdump Analyzer Started ===")
    main()