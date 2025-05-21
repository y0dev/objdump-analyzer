import os
import re
import logging

class ObjdumpParser:
    def __init__(self, output_dir, registers=[]):
        self.registers = registers
        self.output_dir = output_dir
        self.register_log_path = os.path.join(output_dir, "register_matches.txt")

        try:
            os.makedirs(output_dir, exist_ok=True)
            self.register_log_file = open(self.register_log_path, "w")
        except Exception as e:
            logging.error(f"Failed to create/open register log file: {e}")
            self.register_log_file = None

    def parse_line(self, line):
        """Parse individual lines from objdump output."""
        if self.register_log_file is None:
            return  # Skip if file isn't ready

        for reg in self.registers:
            # Match register as a standalone word using word boundaries
            if re.search(rf'\b{re.escape(reg)}\b', line):
                self.register_log_file.write(line)
                break  # Write only once per line if any register matches

    def close(self):
        if self.register_log_file:
            self.register_log_file.close()
