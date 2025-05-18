import subprocess
import logging
from src.parser import ObjdumpParser
from src.utils import ensure_directories

class ObjdumpAnalyzer:
    def __init__(self, obj_file, architecture, registers=[]):
        self.obj_file = obj_file
        self.architecture = architecture
        self.registers = registers
        self.parser = ObjdumpParser(registers)
        ensure_directories()

    def run_objdump(self):
        """Execute objdump and stream the output for efficient parsing."""
        try:
            logging.info(f"Running objdump for {self.obj_file} with arch {self.architecture}")
            process = subprocess.Popen(
                [self.architecture, '-x', '-d', self.obj_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            for line in process.stdout:
                self.parser.parse_line(line)
        except FileNotFoundError:
            logging.error(f"Error: {self.obj_file} not found.")
        except Exception as e:
            logging.error(f"Error running objdump: {e}")
