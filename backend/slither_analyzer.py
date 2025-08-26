import subprocess
import json
import os

class SlitherAnalysisError(Exception):
    """Custom exception for Slither analysis errors."""
    pass

def analyze_contract(file_path: str) -> dict:
    """
    Analyzes a Solidity contract using Slither and returns the JSON output.

    Args:
        file_path: The path to the Solidity contract file.

    Returns:
        A dictionary containing the Slither analysis results.

    Raises:
        SlitherAnalysisError: If Slither fails to run or returns an error.
    """
    command = ["slither", file_path, "--json", "-"]

    try:
        # Pass the current environment to the subprocess to ensure `solc` is found.
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=os.environ,
            check=False # We will check the return code manually
        )

        # A non-zero exit code from Slither indicates a fatal error.
        if process.returncode != 0:
             # Slither might have already output a JSON with an error message
            try:
                output = json.loads(process.stdout)
                if not output.get("success", False):
                    error_msg = output.get("error", "Unknown error")
                    raise SlitherAnalysisError(f"Slither analysis failed: {error_msg}")
            except json.JSONDecodeError:
                # If the output is not JSON, use stderr as the error message
                raise SlitherAnalysisError(f"Slither exited with code {process.returncode}:\n{process.stderr}")

        # If the command was successful, parse the JSON from stdout
        return json.loads(process.stdout)

    except FileNotFoundError:
        raise SlitherAnalysisError("Slither command not found. Make sure it is installed and in your PATH.")
    except json.JSONDecodeError:
        raise SlitherAnalysisError("Failed to decode Slither's JSON output.")
    except Exception as e:
        raise SlitherAnalysisError(f"An unexpected error occurred during Slither analysis: {e}")
