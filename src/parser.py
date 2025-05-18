import logging

class ObjdumpParser:
    def __init__(self, registers=[]):
        self.registers = registers

    def parse_line(self, line):
        """Parse individual lines from objdump output."""
        if any(reg in line for reg in self.registers):
            logging.info(f"Register match: {line.strip()}")
            print(line.strip())
