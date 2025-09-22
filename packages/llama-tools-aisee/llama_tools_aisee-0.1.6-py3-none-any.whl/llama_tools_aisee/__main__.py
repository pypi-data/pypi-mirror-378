import argparse
from llama_tools_aisee.setup_llama_cpp import setup_llama, clone_llama_cpp
from llama_tools_aisee.venv import create_virtualenv
from llama_tools_aisee.convert_and_quantize import convert_model
from llama_tools_aisee.utils import clean_build_dirs, show_status
from llama_tools_aisee.push_gguf import push_gguf
from llama_tools_aisee.server import run_llama_server

# Help message for quantization options
quant_types_help = """\
Quantization type to apply (if any). Options include:
  Q4_0, Q4_1, Q5_0, Q5_1, Q8_0, Q3_K_M, Q4_K_S, Q5_K_M, IQ2_XS, TQ1_0, etc.
See full list at: https://github.com/ggerganov/llama.cpp#quantization
Common options:
  - Q4_0    : 4.34G, basic 4-bit
  - Q4_1    : 4.78G, better quality 4-bit
  - Q5_0    : 5.21G
  - Q5_1    : 5.65G
  - Q8_0    : 7.96G, nearly full precision
  - Q3_K_M  : 3.74G, mixed 3-bit
  - Q4_K_S  : 4.37G, high-quality 4-bit
  - Q5_K_M  : 5.33G, high-quality 5-bit
  - IQ2_XS  : 2.31 bpw
  - TQ1_0   : 1.69 bpw ternary

Full command: llama.cpp/build/bin/llama-quantize --help
"""

def main():
    parser = argparse.ArgumentParser(description="llama-tools CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: setup - Builds llama.cpp using CMake & Ninja
    setup_parser = subparsers.add_parser("setup", help="Build llama.cpp")
    setup_parser.add_argument("-j", "--jobs", type=int, required=True, help="Parallel build jobs (e.g., 4 or 8)")
    setup_parser.add_argument("--create-venv", action="store_true", help="Create and install Python virtual environment")

    # Subcommand: clone - Clones llama.cpp repository and initializes submodules
    subparsers.add_parser("clone", help="Clone llama.cpp repository and submodules")

    # Subcommand: venv - Creates Python virtual environment and installs requirements
    subparsers.add_parser("venv", help="Create virtual environment and install requirements")

    # Subcommand: clean - Removes build and model output directories
    subparsers.add_parser("clean", help="Remove build and model directories")

    # Subcommand: status - Displays current build and environment status
    subparsers.add_parser("status", help="Show current environment and build status")

    # Subcommand: convert - Converts Hugging Face model to GGUF, optionally quantizing it
    convert_parser = subparsers.add_parser("convert", help="Convert HF model to GGUF, optionally quantize")
    convert_parser.add_argument("--hf_model", required=True, help="HF model repo ID or local path")
    convert_parser.add_argument("--gguf_output", required=True, help="Path to save GGUF output")
    convert_parser.add_argument("--quantized_output", help="Optional path to save quantized model")
    convert_parser.add_argument("--quant_type", help=quant_types_help)
    convert_parser.add_argument("--quant_algo", default="8", help="Quantization algorithm (default: 8)")

    # Subcommand: upload - Uploads a GGUF file to Hugging Face Hub
    upload_parser = subparsers.add_parser("upload", help="Upload a GGUF model to Hugging Face Hub")
    upload_parser.add_argument("--repo_id", required=True, help="e.g. username/model-name")
    upload_parser.add_argument("--gguf_path", required=True, help="Path to the .gguf file")
    upload_parser.add_argument("--local_repo_dir", default="./hf_tmp_repo", help="Temporary local repo directory")

    # Subcommand: run-server - Runs llama.cpp server with a selected GGUF model
    run_parser = subparsers.add_parser("run-server", help="Run llama-server with a GGUF model")
    run_parser.add_argument("--gguf_model", required=True, help="Path to the GGUF model file")

    # Parse and dispatch to appropriate function
    args = parser.parse_args()

    if not args.command:
        print("\nWelcome to llama-tools-aisee!")
        print("You need to specify a command to run.")
        print("Available commands: setup, clone, venv, clean, status, convert, upload, run-server")
        print("Use `llama-tools-aisee -h` for more details on each command.\n")
        return  # exit gracefully without error

    if args.command == "setup":
        setup_llama(jobs=args.jobs, create_venv=args.create_venv)
    elif args.command == "clone":
        clone_llama_cpp()
    elif args.command == "venv":
        create_virtualenv()
    elif args.command == "convert":
        convert_model(
            hf_model=args.hf_model,
            gguf_output=args.gguf_output,
            quantized_output=args.quantized_output,
            quant_type=args.quant_type,
            quant_algo=args.quant_algo
        )
    elif args.command == "upload":
        push_gguf(
            repo_id=args.repo_id,
            gguf_path=args.gguf_path,
            local_repo_dir=args.local_repo_dir
        )
    elif args.command == "run-server":
        run_llama_server(gguf_model=args.gguf_model)
    elif args.command == "clean":
        clean_build_dirs()
    elif args.command == "status":
        show_status()
