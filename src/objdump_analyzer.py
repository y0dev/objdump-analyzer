import os
import re
import shutil
import logging
import subprocess
from datetime import datetime
from src.parser import ObjdumpParser
from src.utils import ensure_directories

class ObjdumpAnalyzer:
    def __init__(self, obj_file, architecture, registers=[]):
        self.obj_file = obj_file
        self.architecture = architecture
        self.registers = registers

        # Create timestamped output directory
        now = datetime.now()
        date_part = now.strftime("%m_%d_%Y")
        time_part = now.strftime("%H_%M_%S")
        base_name = os.path.splitext(os.path.basename(self.obj_file))[0]
        self.output_dir = os.path.join("output", date_part, f"{base_name}_{time_part}")

        # Ensure the output and log directories exist
        ensure_directories(['logs', self.output_dir])

        self.parser = ObjdumpParser(self.output_dir, registers)

        # Copy the original object/ELF file to the output directory
        try:
            shutil.copy2(self.obj_file, os.path.join(self.output_dir, os.path.basename(self.obj_file)))
        except FileNotFoundError:
            logging.error(f"Input file not found: {self.obj_file}")
        except Exception as e:
            logging.error(f"Failed to copy input file to output directory: {e}")
        
        
        logging.info(f"Initialized ObjdumpAnalyzer for: {self.obj_file}")
        logging.info(f"Architecture: {self.architecture}")
        logging.info(f"Registers: {', '.join(self.registers) if self.registers else 'None'}")
        logging.info(f"Output directory set to: {self.output_dir}")

    def get_elf_size(self):
        """
        Runs the `size` command on the ELF or object file and logs the result.

        Logs the output in the format:
        text	   data	    bss	    dec	    hex	filename
        1234	   567	    89	    1890	762	test.elf
        """
        summary_path = os.path.join(self.output_dir, "summary.txt")

        try:
            result = subprocess.run(
                [self.architecture + 'size', self.obj_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logging.info("ELF Size Report:\n" + result.stdout.strip())

            # Write the result to summary file
            with open(summary_path, "a") as f:
                f.write("=== ELF Size Report ===\n")
                f.write(result.stdout.strip() + "\n\n")

            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            logging.error(f"Error running size on {self.obj_file}: {e.stderr.strip()}")
            return None
        except FileNotFoundError:
            logging.error("The `size` command was not found. Please install binutils.")
            return None

    def run_objdump(self):
        """Execute objdump and stream the output for efficient parsing."""
        try:
            output_file_path = os.path.join(self.output_dir, "objdump.txt")

            logging.info(f"Running objdump for {self.obj_file} with arch {self.architecture}")
            logging.info(f"Writing output to: {output_file_path}")

            with open(output_file_path, 'w') as out_file:
                process = subprocess.Popen(
                    [self.architecture + 'objdump', '-x', '-d', self.obj_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                for line in process.stdout:
                    out_file.write(line)
                    self.parser.parse_line(line)
                self.parser.close()

                # Optionally log stderr
                for err_line in process.stderr:
                    logging.error(err_line.strip())

        except FileNotFoundError:
            logging.error(f"Error: {self.obj_file} not found.")
        except Exception as e:
            logging.error(f"Error running objdump: {e}")

    def gen_symbol_table(self):
        """Generate a symbol table using objdump -t and store it in output/ directory."""
        try:
            symbol_file_path = os.path.join(self.output_dir, "symbols.txt")

            logging.info(f"Generating symbol table for {self.obj_file}")
            logging.info(f"Writing symbol table to: {symbol_file_path}")

            with open(symbol_file_path, 'w') as sym_file:
                process = subprocess.run(
                    [self.architecture + 'objdump', '-t', self.obj_file],
                    stdout=sym_file,
                    stderr=subprocess.PIPE,
                    text=True
                )

            if process.stderr:
                logging.warning("Warnings or errors during symbol table generation:")
                logging.warning(process.stderr.strip())

            return symbol_file_path

        except FileNotFoundError:
            logging.error(f"Error: {self.obj_file} not found.")
            return None
        except Exception as e:
            logging.error(f"Error generating symbol table: {e}")
            return None

        

    def analyze_function_sizes(self, disassembly_lines):
        """
        Analyzes function sizes from objdump disassembly output.

        Args:
            disassembly_lines: A list of strings representing the disassembled lines
                            from an objdump command (e.g., `objdump -d <binary>`).
                            Expected to include function headers and instruction lines.

        Returns:
            A list of dictionaries, each containing:
                - 'name': The function name.
                - 'start': The starting address of the function as a hexadecimal string.
                - 'end': The ending address of the function as a hexadecimal string.
                - 'size': The size of the function in bytes (integer).
        """

        # Pattern to detect function headers: e.g., "80000100 <my_function>:"
        func_pattern = re.compile(r'^([0-9a-fA-F]+) <(.+)>:$')

        # Pattern to detect instruction lines: e.g., "80000100: 13 01 00 00  addi x2,x2,0"
        instruction_pattern = re.compile(r'^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]{2,}')

        functions = []        # Stores the list of detected functions and their size info
        current_func = None   # Stores the currently parsed function's metadata
        current_addr = None   # Tracks the latest instruction address for size calculation

        # Iterate over every line of the disassembly
        for line in disassembly_lines:
            func_match = func_pattern.match(line)
            instr_match = instruction_pattern.match(line)

            # If we encounter a new function definition
            if func_match:
                # If a previous function was being tracked, finalize its end address and size
                if current_func and current_func.get("start") is not None:
                    current_func["end"] = current_addr
                    current_func["size"] = int(current_func["end"], 16) - int(current_func["start"], 16)
                    functions.append(current_func)

                # Start tracking the new function
                current_func = {
                    "name": func_match.group(2),
                    "start": func_match.group(1),
                    "end": None,
                    "size": 0
                }
                current_addr = func_match.group(1)  # Initialize current address

            # If we encounter an instruction and we are inside a function
            elif instr_match and current_func:
                current_addr = instr_match.group(1)  # Update current address to the latest instruction

        # Finalize the last function if it exists
        if current_func and current_func.get("start") is not None:
            current_func["end"] = current_addr
            current_func["size"] = int(current_func["end"], 16) - int(current_func["start"], 16)
            functions.append(current_func)

        return functions

    def analyze_function_symbols(self, symbol_lines):
        """
        Analyzes function symbols and sizes from symbol table output.

        Args:
            symbol_lines: A list of strings representing lines from a symbol table
                        (e.g., output from `objdump -t` or `nm -S`).
                        Expected to include address, size, and symbol name.

        Returns:
            A list of dictionaries, each containing:
                - 'name': The function name.
                - 'address': The starting address of the function as a hexadecimal string.
                - 'size': The size of the function in bytes (integer).
        """

        # Example line formats to match:
        # From `nm -S`:
        # 0000000000001138 00000014 T _start
        # From `objdump -t`:
        # 0000000000001138 g     F .text  00000014 _start
        symbol_pattern = re.compile(
            r'^(?P<addr>[0-9a-fA-F]+)\s+(?:(?:\w+\s+)*F.*)?(?P<size>[0-9a-fA-F]+)?\s+(?P<name>\S+)$'
        )

        functions = []

        for line in symbol_lines:
            match = symbol_pattern.match(line.strip())
            if match:
                addr = match.group('addr')
                size = match.group('size')
                name = match.group('name')

                # Skip if it's not a function (symbol table may contain other symbols)
                if not name or name == '.text':
                    continue

                try:
                    size_int = int(size, 16) if size else 0
                    functions.append({
                        'name': name,
                        'address': addr,
                        'size': size_int
                    })
                except ValueError:
                    continue

        return functions
    

    def analyze_data_sections(self, symbol_lines):
        """
        Analyzes global and static variable sizes from symbol table output.

        Args:
            symbol_lines: A list of strings representing lines from a symbol table
                        (e.g., output from `objdump -t` or `nm -S`).
                        Expected to include address, size, and symbol name, with sections like
                        .data, .bss, or .rodata.

        Returns:
            A list of dictionaries, each containing:
                - 'name': The variable name.
                - 'address': The starting address of the variable as a hexadecimal string.
                - 'size': The size of the variable in bytes (integer).
                - 'section': The section in which the symbol is located (e.g., .data, .bss, .rodata).
        """

        # Example line from `objdump -t`:
        # 0000000000002000 g     O .data  00000004 my_global
        # From `nm -S`:
        # 0000000000003000 00000008 D my_static_var

        symbol_pattern = re.compile(
            r'^(?P<addr>[0-9a-fA-F]+)\s+(?:(?:\w+\s+)*[ODBR])(?:\s+(?P<section>\.\w+))?\s+(?P<size>[0-9a-fA-F]+)?\s+(?P<name>\S+)$'
        )

        data_vars = []

        for line in symbol_lines:
            match = symbol_pattern.match(line.strip())
            if match:
                addr = match.group('addr')
                size = match.group('size')
                name = match.group('name')
                section = match.group('section')

                if not section or section not in ['.data', '.bss', '.rodata']:
                    continue

                try:
                    data_vars.append({
                        'name': name,
                        'address': addr,
                        'size': int(size, 16) if size else 0,
                        'section': section
                    })
                except ValueError:
                    continue

        return data_vars