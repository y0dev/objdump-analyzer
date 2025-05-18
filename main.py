import click
from src.objdump_analyzer import ObjdumpAnalyzer

@click.command()
@click.option('--file', '-f', required=True, help='Path to the object file.')
@click.option('--arch', '-a', required=True, help='Objdump architecture (e.g., riscv-objdump, arm32-objdump).')
@click.option('--register', '-r', multiple=True, help='Filter disassembly by registers.')
def main(file, arch, register):
    """ Main entry point for Objdump Analyzer """
    analyzer = ObjdumpAnalyzer(file, arch, list(register))
    analyzer.run_objdump()

if __name__ == '__main__':
    main()
