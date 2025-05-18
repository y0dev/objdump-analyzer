# Objdump Analyzer

Objdump Analyzer is a Python application for efficient analysis of large object dump (`objdump`) files. It supports multiple architectures such as `mb-objdump`, `arm32-objdump`, and `riscv-objdump`.

## Features

- Fast parsing of large objdump files
- Architecture-specific analysis
- Register-based disassembly filtering
- Configurable output and logging

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py --file <object_file> --arch riscv-objdump --register a0 a1
```
