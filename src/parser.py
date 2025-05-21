import re
import logging

class ObjdumpParser:
    def __init__(self, registers=[]):
        self.registers = registers

    def parse_line(self, line):
        """Parse individual lines from objdump output."""
        for reg in self.registers:
            # Match whole word using word boundaries: \b
            if re.search(rf'\b{re.escape(reg)}\b', line):
                logging.info(f"Register match: {line.strip()}")
                break  # Avoid multiple logs if more than one register matches
