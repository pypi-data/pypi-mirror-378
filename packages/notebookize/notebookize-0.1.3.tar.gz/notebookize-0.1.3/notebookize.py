"""A Python decorator that turns functions back into jupyter notebooks, complete with their context."""

__version__ = "0.1.3"

import ast
import inspect
import functools
import textwrap
import logging
import os
import uuid
import libcst as cst
import time
import subprocess
import threading
import sys

from pathlib import Path
from datetime import datetime
from typing import Callable, Any, Optional, Tuple, List, Union, TypeVar, Dict

# Global list to track JupyterLab processes for cleanup
_jupyter_lab_processes: List[subprocess.Popen] = []


class ReturnToAssignmentTransformer(cst.CSTTransformer):
    """Transform return statements to _return = assignments for notebook execution."""

    def leave_Return(
        self, original_node: cst.Return, updated_node: cst.Return
    ) -> Union[cst.Assign, cst.Return]:
        """Convert return statements to _return = assignments."""
        if updated_node.value is None:
            # return with no value becomes _return = None
            assignment = cst.Assign(
                targets=[cst.AssignTarget(target=cst.Name("_return"))],
                value=cst.Name("None"),
            )
        else:
            # return expr becomes _return = expr
            assignment = cst.Assign(
                targets=[cst.AssignTarget(target=cst.Name("_return"))],
                value=updated_node.value,
            )

        return assignment


class AssignmentToReturnTransformer(cst.CSTTransformer):
    """Transform _return = assignments back to return statements."""

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> Union[cst.Assign, cst.Return]:
        """Convert _return = assignments back to return statements."""
        # Check if it's assigning to _return
        if (
            len(updated_node.targets) == 1
            and isinstance(updated_node.targets[0].target, cst.Name)
            and updated_node.targets[0].target.value == "_return"
        ):
            # Convert back to return statement
            if (
                isinstance(updated_node.value, cst.Name)
                and updated_node.value.value == "None"
            ):
                # _return = None becomes return
                return cst.Return(value=None)
            else:
                # _return = expr becomes return expr
                return cst.Return(value=updated_node.value)

        return updated_node


def _get_logger() -> logging.Logger:
    """Get or create the notebookize logger."""
    logger = logging.getLogger("notebookize")

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def _get_kernel_info(func_name: str) -> Tuple[str, str, str]:
    """Generate consistent kernel ID, display name, and language.

    Args:
        func_name: Name of the function

    Returns:
        Tuple of (kernel_id, display_name, language)
    """
    pid = os.getpid()
    kernel_id = f"notebookize-{func_name.lower()}-{pid}"
    display_name = f"Notebookize: {func_name} (PID {pid})"
    # Use a custom language identifier to prevent auto-starting Python kernels
    language = "python-notebookize"
    return kernel_id, display_name, language


def _get_notebook_dir(source_file: str) -> Path:
    """Get the directory for saving notebooks.

    Args:
        source_file: Optional path to the source file. If provided, notebook will be
                    saved in the same directory as the source file.

    Returns:
        Path to the directory where notebooks should be saved.
    """
    # First check environment variable
    if "NOTEBOOKIZE_PATH" in os.environ:
        notebook_dir = os.environ["NOTEBOOKIZE_PATH"]
        notebook_dir = os.path.expanduser(notebook_dir)
        return Path(notebook_dir)

    return Path(source_file).parent


def _convert_to_percent_format(body_source: str) -> List[str]:
    """
    Convert function body source to jupytext percent format using LibCST.

    Strategy: Use LibCST to find statement boundaries. Combine statements into
    cells where appropriate (not separated by extra newlines nor block
    comments). Move newlines to earlier cells when possible.
    Cells joined with "\n" recreate the original exactly.
    """
    tree = cst.parse_module(body_source)

    cells: List[str] = []

    # Process children (includes both statements and empty lines)
    for idx, child in enumerate(tree.children):
        child_code = tree.code_for_node(child)

        if child_code.endswith("\n"):
            child_code = child_code[:-1]
        else:
            logging.warning(
                f"Statement on shared line may cause diff to be wrong: {child_code}"
            )

        if len(cells) == 0:
            cells.append(child_code)
        else:
            # Move newlines from start of one statement to end of previous statement
            i = 0
            while i < len(child_code) and child_code[i] == "\n":
                cells[-1] = cells[-1] + "\n"
                i += 1
            without_leading_newlines = child_code[i:]

            # If what remains is empty (was just newlines), add a newline to previous cell
            if without_leading_newlines == "":
                cells[-1] = cells[-1] + "\n"
                continue

            if without_leading_newlines.startswith("#") or i > 0:
                cells.append(without_leading_newlines)
            else:
                cells[-1] = cells[-1] + "\n" + without_leading_newlines

    # Special handling to preserve the exact trailing newline behavior
    # Handle edge case: input is just whitespace with no statements
    if not cells:
        cells.append(body_source)

    # To make the invariant work, we need to ensure the last cell preserves trailing newlines
    if body_source.endswith("\n"):
        # The original had a trailing newline
        # Need to add the trailing newline that libCST stripped
        cells[-1] = cells[-1] + "\n"

    return cells


def _generate_jupytext_notebook(
    func_name: str, body_source: str, source_file: str
) -> Path:
    """
    Generate a jupytext .py percent format notebook from function source code.
    Returns the path to the generated notebook.
    """
    import yaml

    # Create notebook directory if it doesn't exist
    notebook_dir = _get_notebook_dir(source_file)
    notebook_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{func_name}_{timestamp}_{unique_id}.nbize.py"
    notebook_path = notebook_dir / filename

    # Transform return statements to _return assignments for notebook execution
    tree = cst.parse_module(body_source)
    transformer = ReturnToAssignmentTransformer()
    modified_tree = tree.visit(transformer)
    transformed_body_source = modified_tree.code

    # Convert body source to cells
    cells = _convert_to_percent_format(transformed_body_source)

    # Create the jupytext percent format content
    content_parts: List[str] = []

    # Build the header metadata as a dictionary
    metadata: Dict[str, Any] = {
        "jupyter": {
            "jupytext": {
                "text_representation": {
                    "extension": ".py",
                    "format_name": "percent",
                    "format_version": "1.3",
                    "jupytext_version": "1.16.0",
                }
            },
            "kernelspec": {},  # Will be populated below
        }
    }

    # Use our custom kernel with custom language
    kernel_id, display_name, language = _get_kernel_info(func_name)
    metadata["jupyter"]["kernelspec"] = {
        "display_name": display_name,
        "language": language,
        "name": kernel_id,
    }

    # Generate YAML header with proper formatting
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)

    # Format as jupytext header comment
    header_lines = ["# ---"]
    for line in yaml_str.strip().split("\n"):
        header_lines.append(f"# {line}")
    header_lines.append("# ---")
    header = "\n".join(header_lines)

    # Log the header for debugging
    logger = _get_logger()
    logger.info(f"Jupytext header:\n{header}")

    content_parts.append(header)

    # Add cells - all are code cells now (including comments)
    for cell in cells:
        content_parts.append("# %%")
        content_parts.append(cell)

    content = "\n".join(content_parts)

    # Write the notebook file
    notebook_path.write_text(content)

    return notebook_path


def _extract_code_from_notebook(notebook_path: Path) -> str:
    """
    Extract code cells from a jupytext percent format notebook.
    Returns the combined code as a string.
    """
    content = notebook_path.read_text()
    lines = content.split("\n")

    code_parts: List[str] = []
    in_code_cell = False
    current_cell: List[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for cell markers
        if line.strip() == "# %%":
            # Start of a code cell
            if current_cell and in_code_cell:
                # Save previous code cell
                code_parts.append("\n".join(current_cell))
                current_cell = []
            in_code_cell = True
            i += 1
            continue
        elif line.strip() == "# %% [markdown]":
            # Start of a markdown cell
            if current_cell and in_code_cell:
                # Save previous code cell
                code_parts.append("\n".join(current_cell))
                current_cell = []
            in_code_cell = False
            i += 1
            continue

        # Collect lines if in code cell
        if in_code_cell:
            current_cell.append(line)

        i += 1

    # Add any remaining code cell
    if current_cell and in_code_cell:
        code_parts.append("\n".join(current_cell))

    # Join cells back with single newline (cells include their own trailing blanks)
    result = "\n".join(code_parts) if code_parts else ""

    # Ensure trailing newline if last line of notebook was not empty
    if result and not result.endswith("\n"):
        result += "\n"

    # Transform _return assignments back to return statements
    tree = cst.parse_module(result)
    transformer = AssignmentToReturnTransformer()
    modified_tree = tree.visit(transformer)
    result = modified_tree.code

    return result


def _rewrite_function_in_file(file_path: str, func_name: str, new_body: str) -> bool:
    """
    Rewrite a function's body in a Python file while preserving everything else.
    Uses LibCST to handle both top-level functions and class methods.
    """
    # Read the file content
    with open(file_path, "r") as f:
        source_content = f.read()

    # Parse with LibCST
    tree = cst.parse_module(source_content)

    # Apply the transformation
    rewriter = FunctionBodyRewriter(func_name, new_body)
    modified_tree = tree.visit(rewriter)

    if not rewriter.replaced:
        raise ValueError(f"Function '{func_name}' not found in {file_path}")

    # Write back the modified content
    with open(file_path, "w") as f:
        f.write(modified_tree.code)

    return True


def _find_function_end_by_dedent(lines: List[str], body_start_line: int) -> int:
    """Find the end of a function by looking for dedentation."""
    if body_start_line >= len(lines):
        return body_start_line

    # Get the indentation of the first body line
    first_body_line = lines[body_start_line] if body_start_line < len(lines) else ""
    base_indent = (
        len(first_body_line) - len(first_body_line.lstrip())
        if first_body_line.strip()
        else 4
    )

    # Look for the next line with less indentation
    for i in range(body_start_line + 1, len(lines)):
        line = lines[i]
        if not line.strip():  # Skip empty lines
            continue

        line_indent = len(line) - len(line.lstrip())
        if line_indent < base_indent:
            return i - 1

    return len(lines) - 1


def _split_file_at_function(
    file_path: str, func_name: str
) -> Tuple[str, str, str, str]:
    """
    Split a file into three parts: before function body, function body, and after function body.
    Returns (before, body, after, indent) where concatenating them gives the original file.
    Uses AST for compatibility, but can find class methods using LibCST fallback.
    """
    with open(file_path, "r") as f:
        original_content = f.read()

    # First try the AST approach for backwards compatibility
    tree = ast.parse(original_content)

    # Find the function node (top-level only with AST)
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_node = node
            break

    if func_node:
        # Get the lines of the original file
        lines = original_content.split("\n")

        # Find where the function signature ends (look for the colon)
        func_start_line = func_node.lineno - 1  # Convert to 0-indexed
        func_def_end_line = func_start_line
        while func_def_end_line < len(lines) and not lines[
            func_def_end_line
        ].rstrip().endswith(":"):
            func_def_end_line += 1

        # The body starts on the next line
        body_start_line = func_def_end_line + 1

        # Find the end of the function body
        if not func_node.body:
            body_end_line = body_start_line
        else:
            # Use AST to find the last line
            ast_end_lineno = func_node.body[-1].end_lineno
            if ast_end_lineno is not None:
                body_end_line = ast_end_lineno - 1
            else:
                body_end_line = -1

            # Handle case where end_lineno is None
            if body_end_line == -1:
                body_end_line = _find_function_end_by_dedent(lines, body_start_line)

        # Get the indentation of the function body
        indent = ""
        for i in range(body_start_line, min(body_end_line + 1, len(lines))):
            if lines[i].strip():
                indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
                break
        if not indent:
            indent = "    "

        # Split into three parts
        before_lines = lines[:body_start_line]
        body_lines = lines[body_start_line : body_end_line + 1]
        after_lines = lines[body_end_line + 1 :]

        before = "\n".join(before_lines)
        body = "\n".join(body_lines)
        after = "\n".join(after_lines) if after_lines else ""

        return before, body, after, indent

    # If AST couldn't find it (e.g., it's a class method), use LibCST
    # Extract the function body using the LibCST-based function
    try:
        body = _extract_function_body_from_source(original_content, func_name)
    except ValueError:
        raise ValueError(f"Function {func_name} not found in {file_path}")

    # For class methods, we can't easily split with AST, so we return simplified values
    # The rewrite function uses LibCST directly anyway
    indent = "    "  # Default indent

    # Try to extract indent from the body
    if body:
        lines = body.split("\n")
        for line in lines:
            if line.strip():
                indent = line[: len(line) - len(line.lstrip())]
                if indent:
                    break

    # For class methods, return empty before/after since we can't easily split
    # This is okay because _rewrite_function_in_file uses LibCST directly now
    return "", body, "", indent


def _extract_function_body(func: Callable[..., Any]) -> str:
    """
    Extract the body source code of a function using LibCST.
    Returns the body source as a string, preserving docstrings and comments.
    """
    # Get the full source of the function
    source = inspect.getsource(func)

    # Dedent the source before parsing (handles functions defined inside other scopes)
    source = textwrap.dedent(source)

    # Parse with LibCST
    tree = cst.parse_module(source)

    # Find the function node (should be the first/only one from getsource)
    for node in tree.body:
        if isinstance(node, cst.FunctionDef):
            if isinstance(node.body, cst.IndentedBlock):
                # Extract all statements in the body
                body_parts = []
                for stmt in node.body.body:
                    stmt_code = tree.code_for_node(stmt)
                    body_parts.append(stmt_code)

                # Join without adding extra newlines - code_for_node already includes them
                body_code = "".join(body_parts)
                return textwrap.dedent(body_code)

    raise ValueError(f"Could not extract body from function {func.__name__}")


class TeeOutStream:
    """Write to both IPython kernel and console stdout/stderr."""

    def __init__(self, kernel_stream: Any, console_stream: Any) -> None:
        self.kernel_stream = kernel_stream
        self.console_stream = console_stream

    def write(self, text: str) -> int:
        # Write to kernel stream (for JupyterLab)
        self.kernel_stream.write(text)
        # Also write to console
        if self.console_stream:
            self.console_stream.write(text)
            self.console_stream.flush()
        return len(text)

    def flush(self) -> None:
        self.kernel_stream.flush()
        if self.console_stream:
            self.console_stream.flush()

    def __getattr__(self, name: str) -> Any:
        # Delegate all other attributes to kernel stream
        return getattr(self.kernel_stream, name)


def _setup_tee_output() -> None:
    """Setup output to go to both kernel and console after kernel init."""
    # Save references to the kernel's OutStreams
    kernel_stdout = sys.stdout
    kernel_stderr = sys.stderr

    # Get the original console streams (saved by Python before redirection)
    original_stdout = sys.__stdout__
    original_stderr = sys.__stderr__

    # Replace with tee versions that write to both
    sys.stdout = TeeOutStream(kernel_stdout, original_stdout)
    sys.stderr = TeeOutStream(kernel_stderr, original_stderr)


def _start_kernel_directly(
    func_name: str,
    logger: logging.Logger,
    user_ns: Optional[Dict[str, Any]] = None,
    user_module: Optional[Any] = None,
) -> Tuple[str, Any]:
    """Start an IPython kernel directly and return the connection file path and app instance.

    Returns:
        Tuple of (connection_file_path, kernel_app) or (None, None) if startup failed
    """
    from ipykernel.kernelapp import IPKernelApp
    import tempfile
    import os

    # Generate a unique connection file path (but don't create the file)
    temp_dir = tempfile.gettempdir()
    connection_file = os.path.join(temp_dir, f"kernel-{os.getpid()}.json")

    # Remove the file if it exists from a previous run
    if os.path.exists(connection_file):
        os.remove(connection_file)

    # Initialize the kernel app with the specific connection file
    app = IPKernelApp.instance()

    # Store the user namespace and module for later injection
    app._user_ns_to_inject = user_ns  # type: ignore[attr-defined]
    app._user_module_to_inject = user_module  # type: ignore[attr-defined]

    # We need to set up a custom initialization to inject our namespace
    original_init_kernel = app.init_kernel

    def custom_init_kernel() -> None:
        # Call the original initialization
        original_init_kernel()

        # Now inject our namespace after kernel is initialized
        if hasattr(app, "_user_ns_to_inject") and app._user_ns_to_inject:
            app.kernel.shell.user_ns.update(app._user_ns_to_inject)
            logger.info(
                f"Setting user namespace with {len(app._user_ns_to_inject)} variables"
            )

        if hasattr(app, "_user_module_to_inject") and app._user_module_to_inject:
            app.kernel.shell.user_module = app._user_module_to_inject
            logger.info(f"Setting user module: {app._user_module_to_inject}")

    # Replace the init method
    app.init_kernel = custom_init_kernel  # type: ignore[method-assign]

    # Pass the connection file and kernel name as command line arguments
    kernel_id, display_name, language = _get_kernel_info(func_name)
    app.initialize(
        [
            "--IPKernelApp.connection_file=" + connection_file,
            "--IPKernelApp.kernel_name=" + kernel_id,
        ]
    )

    # Setup tee output so print statements work in both console and JupyterLab
    _setup_tee_output()

    logger.info(f"Kernel name: {kernel_id}")
    logger.info(f"Kernel initialized with connection file: {connection_file}")

    # Return both the connection file and the app
    # The app will be started in the main thread later
    return connection_file, app


def _find_jupyterlab_start_directory(notebook_path: Path) -> Path:
    """Find the appropriate directory to start JupyterLab from.

    Searches for (in order):
    1. The git top-level directory, if present
    2. The directory above .venv, if present
    3. The site-packages directory it's imported from, if present
    4. The root directory /, if none of the above

    Since we use --ContentsManager.allow_hidden=True, we can serve from hidden directories.

    Args:
        notebook_path: Path to the notebook file

    Returns:
        Path to start JupyterLab from
    """
    # 1. Try to get git repository root using git command
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=str(notebook_path.parent),
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        # Git not available or not in a git repo
        pass

    # 2-4. Walk up looking for other markers
    current = notebook_path.parent.absolute()
    venv_parent = None
    site_packages = None

    while current != current.parent:
        # 2. Track directory above .venv
        if current.name == ".venv" and venv_parent is None:
            venv_parent = current.parent

        # 3. Track site-packages directory
        if current.name == "site-packages" and site_packages is None:
            site_packages = current

        # Move up one directory
        current = current.parent

    # Return based on priority
    if venv_parent:
        return venv_parent
    if site_packages:
        return site_packages

    # 4. Last resort: root directory
    return Path("/")


def _open_notebook_in_jupyterlab(
    notebook_path: Path, logger: logging.Logger, connection_file: str, func_name: str
) -> None:
    """Open the generated .py notebook directly in JupyterLab.

    Args:
        notebook_path: Path to the .py notebook file
        logger: Logger instance
        connection_file: Optional connection file to use with --existing
        func_name: Optional function name for kernel identification
    """
    global _jupyter_lab_processes
    try:
        # Create external kernels directory
        external_kernels_dir = Path("/tmp") / f"notebookize_kernels_{os.getpid()}"
        external_kernels_dir.mkdir(exist_ok=True)

        # Read and modify connection file to add kernel metadata
        import json

        with open(connection_file, "r") as f:
            connection_info = json.load(f)

        # Add kernel metadata for better identification in JupyterLab
        # Use the passed function name or extract from notebook path
        if not func_name:
            func_name = (
                notebook_path.stem.split("_")[0]
                if "_" in notebook_path.stem
                else notebook_path.stem
            )

        # Use consistent kernel naming
        kernel_id, display_name, language = _get_kernel_info(func_name)

        # Generate a UUID for JupyterLab to use as the kernel ID
        import uuid

        jupyter_kernel_id = str(uuid.uuid4())

        connection_info["kernel_name"] = kernel_id
        connection_info["kernel_id"] = jupyter_kernel_id  # JupyterLab needs this
        connection_info["language"] = language  # Custom language to prevent auto-start
        connection_info["metadata"] = {
            "kernel_name": kernel_id,
            "display_name": display_name,
            "language": language,
        }

        # Write the enhanced connection file to external kernels directory
        # Use UUID-based filename that JupyterLab expects
        external_connection_file = (
            external_kernels_dir / f"kernel-{jupyter_kernel_id}.json"
        )
        with open(external_connection_file, "w") as f:
            json.dump(connection_info, f, indent=2)

        logger.info(
            f"Created external kernel connection at: {external_connection_file}"
        )
        logger.info(
            f"External connection file kernel_name: {connection_info.get('kernel_name', 'NOT SET')}"
        )
        logger.info(f"External kernel UUID: {jupyter_kernel_id}")

        # Kernel info is available in the external connection file

        # Find the appropriate directory to start JupyterLab from
        jupyterlab_cwd = _find_jupyterlab_start_directory(notebook_path)
        logger.info(f"Starting JupyterLab from directory: {jupyterlab_cwd}")

        # Create log files next to the notebook
        log_base = notebook_path.with_suffix("")
        stdout_log = open(f"{log_base}.stdout.log", "w")
        stderr_log = open(f"{log_base}.stderr.log", "w")
        logger.info(f"JupyterLab logs: {log_base}.stdout.log and {log_base}.stderr.log")

        # Open JupyterLab with external kernel support
        # Redirect stdout/stderr to log files and stdin to /dev/null
        proc = subprocess.Popen(
            [
                "jupyter",
                "lab",
                str(notebook_path),
                f"--ServerApp.external_connection_dir={external_kernels_dir}",
                "--ServerApp.allow_external_kernels=True",
                "--ContentsManager.allow_hidden=True",  # Allow serving from hidden directories
                # "--debug",  # Enable debug logging
                # "--log-level=DEBUG"  # Set log level to DEBUG
            ],
            stdin=subprocess.DEVNULL,  # No input
            stdout=stdout_log,  # Log stdout to file
            stderr=stderr_log,  # Log stderr to file
            cwd=str(jupyterlab_cwd),  # Start from the determined directory
        )

        # Store the process for cleanup
        _jupyter_lab_processes.append(proc)
        logger.info(f"Opened JupyterLab with notebook: {notebook_path}")
        logger.info(
            f"External kernel '{display_name}' available in: Kernel > Change Kernel > Existing"
        )
        logger.info(f"Kernel UUID: {jupyter_kernel_id}")
    except FileNotFoundError:
        logger.error(
            "JupyterLab not found. Please install with: pip install jupyterlab"
        )


class FunctionFinder(cst.CSTVisitor):
    """Visitor to find all functions/methods with a given name."""

    def __init__(self, func_name: str):
        self.func_name = func_name
        self.matches: List[
            Tuple[cst.FunctionDef, str]
        ] = []  # List of (node, context_path) tuples
        self.context_stack: List[str] = []  # Stack of class names for context

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """Track when we enter a class."""
        self.context_stack.append(node.name.value)
        return True

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        """Track when we leave a class."""
        if self.context_stack and self.context_stack[-1] == node.name.value:
            self.context_stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        """Check if this function matches what we're looking for."""
        if node.name.value == self.func_name:
            # Store the function with its context (e.g., "MyClass.evaluate")
            context = ".".join(self.context_stack + [node.name.value])
            self.matches.append((node, context))
        return True


class FunctionBodyRewriter(cst.CSTTransformer):
    """Transformer to rewrite the body of a specific function/method."""

    def __init__(self, func_name: str, new_body: str):
        self.func_name = func_name
        self.new_body = new_body
        self.context_stack: List[str] = []
        self.replaced = False

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """Track when we enter a class."""
        self.context_stack.append(node.name.value)
        return True

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Track when we leave a class."""
        if self.context_stack and self.context_stack[-1] == original_node.name.value:
            self.context_stack.pop()
        return updated_node

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Replace the function body if this is the target function."""
        if updated_node.name.value == self.func_name and not self.replaced:
            # Parse the new body with proper indentation handling
            # First dedent the new body to normalize it
            import textwrap

            dedented_body = textwrap.dedent(self.new_body)

            # Ensure the body is at module level (no indentation)
            lines = dedented_body.split("\n")
            normalized_lines = []
            min_indent: Optional[int] = None

            # Find minimum indentation of non-empty lines
            for line in lines:
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    if min_indent is None:
                        min_indent = indent
                    else:
                        min_indent = min(min_indent, indent)

            # Remove the minimum indentation from all lines
            if min_indent is not None:
                for line in lines:
                    if line.strip():
                        normalized_lines.append(line[min_indent:])
                    else:
                        normalized_lines.append("")
            else:
                normalized_lines = lines

            normalized_body = "\n".join(normalized_lines)

            # Parse the new body as a module to get the statements
            new_body_module = cst.parse_module(normalized_body)

            # Create a new IndentedBlock with the new body
            if isinstance(updated_node.body, cst.IndentedBlock):
                # Preserve the original indentation and create new body
                new_body_block = updated_node.body.with_changes(
                    body=new_body_module.body
                )
                self.replaced = True
                return updated_node.with_changes(body=new_body_block)

        return updated_node


def _extract_function_body_from_source(source_content: str, func_name: str) -> str:
    """Extract function body from source code content using LibCST."""
    # Parse with LibCST
    tree = cst.parse_module(source_content)

    # Find all functions/methods with the given name
    finder = FunctionFinder(func_name)
    tree.visit(finder)  # Use visit() to walk the tree with the visitor

    if not finder.matches:
        raise ValueError(f"Function '{func_name}' not found in source code.")

    # If there's only one match, use it
    # If there are multiple matches, prefer the one with shortest context (less nested)
    # This prioritizes top-level functions over methods, and methods over nested functions
    best_match = min(finder.matches, key=lambda x: len(x[1].split(".")))
    node = best_match[0]

    if isinstance(node.body, cst.IndentedBlock):
        # Extract all statements in the body
        body_parts = []
        for stmt in node.body.body:
            stmt_code = tree.code_for_node(stmt)
            body_parts.append(stmt_code)

        # Join without adding extra newlines - code_for_node already includes them
        body_code = "".join(body_parts)
        return textwrap.dedent(body_code)

    return ""


def _handle_notebook_change(
    notebook_path: Path, source_file: str, func_name: str, logger: logging.Logger
) -> bool:
    """Handle a detected change in the notebook file."""
    # Extract code from the modified notebook
    new_body = _extract_code_from_notebook(notebook_path)

    if not new_body:
        logger.warning("No code found in notebook")
        return False

    # Get the current function body for diff
    with open(source_file, "r") as f:
        source_content = f.read()
    old_body = _extract_function_body_from_source(source_content, func_name)

    # Remove common leading indentation from old_body for comparison
    # This normalizes the indentation so we can properly compare
    import textwrap

    old_body_dedented = textwrap.dedent(old_body)

    # Check if there are actual changes
    if old_body_dedented.strip() == new_body.strip():
        logger.info(f"No actual changes detected in {func_name} ({source_file})")
        return True  # Return True since there's no error, just no changes

    # Show diff if we have both old and new content
    logger.info(f"Notebook changed, updating {func_name} in {source_file}")
    if old_body_dedented:
        import difflib

        diff_lines = list(
            difflib.unified_diff(
                old_body_dedented.splitlines(keepends=True),
                new_body.splitlines(keepends=True),
                fromfile=f"{source_file}:{func_name} (before)",
                tofile=f"{source_file}:{func_name} (after)",
                lineterm="",
            )
        )

        if diff_lines:
            logger.info("Changes detected:")
            for line in diff_lines:
                logger.info(line.rstrip())

    # Rewrite the function in the source file
    success = _rewrite_function_in_file(source_file, func_name, new_body)

    if success:
        logger.info(f"Successfully updated {func_name}")
    else:
        logger.error(f"Failed to update {func_name}")

    return success


def _watch_notebook_for_changes(
    notebook_path: Path,
    source_file: str,
    func_name: str,
    logger: logging.Logger,
    write_back: bool = True,
) -> None:
    """Watch notebook file for changes and optionally update the source file when detected."""
    logger.info(f"Watching {notebook_path} for changes...")

    if not write_back:
        logger.info(
            "Note: write_back is disabled - changes will NOT be written to source file"
        )

    logger.info("Press Ctrl+C to stop watching")

    last_mtime = notebook_path.stat().st_mtime
    check_interval = float(os.environ.get("NOTEBOOKIZE_CHECK_INTERVAL", "1.0"))

    try:
        while True:
            time.sleep(check_interval)
            try:
                current_mtime = notebook_path.stat().st_mtime
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    if write_back:
                        _handle_notebook_change(
                            notebook_path, source_file, func_name, logger
                        )
                    else:
                        logger.info("Change detected in notebook")
                        logger.info(
                            f"Notebook {notebook_path.name} changed (write_back disabled)"
                        )
            except FileNotFoundError:
                logger.error(f"Notebook {notebook_path} was deleted")
                break
    except KeyboardInterrupt:
        logger.info("Stopped watching for changes")


F = TypeVar("F", bound=Callable[..., Any])


def notebookize(
    func: Optional[F] = None, *, open_jupyterlab: bool = True, write_back: bool = True
) -> Union[F, Callable[[F], F]]:
    """
    Decorator that generates a jupytext notebook and watches for changes,
    optionally updating the original function source when the notebook is modified.

    Args:
        func: The function to decorate
        open_jupyterlab: Whether to open the notebook in JupyterLab
        write_back: Whether to write changes back to the source file (default: True)
    """
    if func is None:
        return functools.partial(  # type: ignore[return-value]
            notebookize, open_jupyterlab=open_jupyterlab, write_back=write_back
        )

    logger = _get_logger()

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
        # Get the source file path of the function
        source_file = inspect.getsourcefile(func)
        if not source_file:
            logger.error(f"Cannot determine source file for {func.__name__}")
            return func(*args, **kwargs)

        # Extract the function body
        try:
            body_source = _extract_function_body(func)
        except ValueError as e:
            logger.error(f"Error extracting function body: {e}")
            return func(*args, **kwargs)

        logger.info(f"Original function body for {func.__name__}:")
        logger.info(body_source)

        # Always set up kernel
        # Capture the function's module namespace
        user_ns = None
        user_module = None
        # Get the function's module
        user_module = inspect.getmodule(func)
        if user_module:
            # Get the module's globals
            user_ns = dict(user_module.__dict__)
            # Add the function arguments
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            user_ns.update(bound_args.arguments)

        # Initialize kernel and get connection file
        connection_file, kernel_app = _start_kernel_directly(
            func.__name__, logger, user_ns, user_module
        )
        logger.info("Kernel Started")

        # Generate jupytext notebook with kernel name (always enabled)
        notebook_path = _generate_jupytext_notebook(
            func.__name__, body_source, source_file
        )
        logger.info(f"Notebook saved to: {notebook_path}")

        # Open in JupyterLab if requested
        if open_jupyterlab:
            _open_notebook_in_jupyterlab(
                notebook_path, logger, connection_file, func.__name__
            )

        # Start file watching in a background thread
        watch_thread = threading.Thread(
            target=_watch_notebook_for_changes,
            args=(notebook_path, source_file, func.__name__, logger, write_back),
            daemon=True,
        )
        watch_thread.start()

        # Run the kernel in the main thread (for JupyterLab mode)
        try:
            logger.info("Starting IPython kernel in main thread...")
            logger.info(f"Connection file: {connection_file}")
            logger.info("Kernel is ready for connections")

            # Set up signal handlers to clean up subprocesses
            import signal

            def cleanup_handler(signum: int, frame: Any) -> None:
                _ = signum, frame  # Required by signal handler signature
                # In JupyterLab mode, exit immediately
                logger.info("Received interrupt signal, cleaning up...")

                # Kill JupyterLab processes if any
                global _jupyter_lab_processes
                for proc in _jupyter_lab_processes:
                    if proc.poll() is None:  # Still running
                        logger.info(f"Terminating JupyterLab process (PID: {proc.pid})")
                        proc.terminate()
                        try:
                            proc.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                # Raise KeyboardInterrupt to stop the kernel
                raise KeyboardInterrupt()

            # Install signal handler
            old_handler = signal.signal(signal.SIGINT, cleanup_handler)

            try:
                kernel_app.start()  # This blocks until kernel is terminated
            finally:
                # Restore original handler
                signal.signal(signal.SIGINT, old_handler)

        except KeyboardInterrupt:
            logger.info("Kernel interrupted by user")
            # Clean up any remaining JupyterLab processes
            for proc in _jupyter_lab_processes:
                if proc.poll() is None:
                    proc.terminate()

        # Execute the function with potentially updated source
        logger.info(f"Watching stopped. Function {func.__name__} was not executed.")

        # Return None since the function was used for notebook editing, not execution
        return None

    return wrapper  # type: ignore[return-value]
