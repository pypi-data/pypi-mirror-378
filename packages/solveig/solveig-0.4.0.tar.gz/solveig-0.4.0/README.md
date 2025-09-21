
# Solveig

[![PyPI](https://img.shields.io/pypi/v/solveig)](https://pypi.org/project/solveig)
[![CI](https://github.com/FranciscoSilveira/solveig/workflows/CI/badge.svg)](https://github.com/FranciscoSilveira/solveig/actions)
[![codecov](https://codecov.io/gh/FranciscoSilveira/solveig/branch/main/graph/badge.svg)](https://codecov.io/gh/FranciscoSilveira/solveig)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![demo](solveig-demo.gif)

**A safe bridge between AI assistants and your computer.**

Solveig transforms any LLM into a practical assistant that can read files and run commands—with your explicit approval for every operation. No more copying and pasting between your terminal and ChatGPT.

🔒 **Safe** • Comprehensive test suite • Secure file API • Command validation  
🚀 **Useful** • Works with any OpenAI-compatible API • Handles real tasks efficiently  
🧩 **Extensible** • Drop-in plugin system • Easy to customize and extend

---

## 🚀 Quick start


```bash
# Install from source:
git clone https://github.com/FranciscoSilveira/solveig.git
cd solveig
pip install -e .

# Or install from PyPI:
pip install solveig

# Run a local model:
solveig -u "http://localhost:5001/v1" "Tell me a joke"

# Run from a remote API like OpenRouter:
solveig -u "https://openrouter.ai/api/v1" -k "<API_KEY>" -m "moonshotai/kimi-k2:free" "Summarize my day"
```

---

<a href="https://vshymanskyy.github.io/StandWithUkraine">
	<img src="https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg">
</a>

---

## ❓ FAQ


### What is Solveig?

A terminal AI helper that can request file access and run commands with your explicit approval.

### Is Solveig an LLM like ChatGPT?

No, it's a safe interface between LLM services and your computer. It can use ChatGPT, Claude, or any OpenAI-compatible service.

### Why use Solveig instead of a plain LLM?

LLMs can only work with what you manually provide. If ChatGPT needs a file or command output, you have to copy-paste it yourself. Solveig lets the LLM request exactly what it needs, and you just approve or deny each request.

### Why use Solveig over other LLM‑to‑shell assistants?

Solveig focuses on preventing dangerous operations through explicit user consent and validation. It prefers direct file access over arbitrary commands when possible, and validates commands with Shellcheck before execution.

### Is Solveig safe to run?

Mostly:
- Solveig is unable to read file contents, run commands or send back anything unless you give it explicit consent
- Interacts with files and tools through requirements, enforcing user control and allowing easy validation
- Validates shell commands before they're even requested through the included shellcheck plugin (requires installing CLI tool `shellcheck`)
- Open-source project, proper CI with 200+ test suite with 90%+ coverage and extensive scenario focus

This is still a tool that connects an AI to your terminal - always review what it wants to do.

### How does Solveig work?

Solveig creates a conversation with an LLM using the initial prompt and establishes a loop where the LLM asks for requirements and you choose whether to execute them and send back their results.

Most AI CLI assistants rely only on running Bash obtained from a model, which can be a shaky foundation for a security product. Instead, Solveig focuses on providing a safe interface for most behavior that bypasses shell commands, allowing for proper inspection and interface displaying. Basically, it's much easier to validate a read/write requirement for a file than validating a `cat` command to read or an `echo` pipe to write the same file.

All core filesystem operations are covered by requirements, and you can extend this by adding new requirement plugins or interacting with requirements through hook plugins.

### Why are there 2 kinds of plugins?

You can extend Solveig in any of 2 ways:
- By adding a new requirement, representing a new thing the LLM can request
- By adding a hook that captures the requirement before or after it's been processed

Requirements follow a simple interface with 3 methods and return a corresponding Result class:

```python
from typing import Literal

from solveig.interface import SolveigInterface
from solveig.schema.requirements.base import Requirement
from solveig.schema.results.base import RequirementResult
from solveig.plugins.schema import register_requirement


class MyResult(RequirementResult):
    """Example requirement result."""
    response: str | None = None


@register_requirement
class MyRequirement(Requirement):
    """Example requirement."""
    title: Literal["myreq"] = "myreq"

    def create_error_result(self, error_message: str, accepted: bool) -> MyResult:
        """Create a result with an error."""
        return MyResult(
            requirement=self,
            accepted=accepted,
            error=error_message,
        )

    @classmethod
    def get_description(cls) -> str:
        """Return requirement description, using this format: name(args): description."""
        return (
            "myreq(name): description of what this requirement does"
        )

    def actually_solve(self, config, interface: SolveigInterface) -> MyResult:
        """Solve the requirement and return the result."""
        user_response = interface.ask_user("What to send back")
        return MyResult(
            requirement=self,
            accepted=False,
            response=user_response
        )


# Fix possible forward typing references
MyResult.model_rebuild()
```

Hooks meanwhile latch onto existing (or new) requirements, either before or after they run

You can add a requirement by itself, a hook for a new or existing requirement, or a combination of both.
Some examples:
- MySQL plugin
  - SQLRequirement: runs a query on database
- Web Search
  - SearchRequirement: performs a HTTP request the URL
  - @before hook: validates the URL against a blacklist/whitelist before running request
- Anonymize Paths
  - @after hook: privacy-focused plugin that converts expanded paths to fake ones (/home/user-name -> home/jdoe) in results

---

## 🎭 Examples

These were obtained with [Kimi K2](https://openrouter.ai/moonshotai/kimi-k2) on OpenRouter.

*click to expand:*

<details>
<summary><b>Do any of the files in ~/Sync look dangerous?</b></summary>

```
─── User ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Reply:
 > Do any of the files in ~/Sync look dangerous?

⠇ Waiting... (Ctrl+C to stop)

─── Assistant ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
❝  I'll check the contents of your ~/Sync directory to identify any potentially dangerous files. Let me start by reading the directory structure and then examine the files within.
[ Requirements (1) ]
  [ Read (1) ]
    ❝  First, let me read the ~/Sync directory to see what files are present
    🗁  ~/Sync  (/home/francisco/Sync)

─── User ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
[ Results (1) ]
  [ Read ]
    ❝  First, let me read the ~/Sync directory to see what files are present
    🗁  ~/Sync  (/home/francisco/Sync)
    ┌─── Metadata ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │ 🗁 /home/francisco/Sync | owner_name=francisco | group_name=francisco | path=/home/francisco/Sync | size=4096 | modified_time=Wed ... │
    │ ├─🗁 d1                                                                                                                               │
    │ ├─🗎 dev.sh                                                                                                                           │
    │ ├─🗎 f1                                                                                                                               │
    │ ├─🗎 hello.py                                                                                                                         │
    │ ├─🗎 j1.json                                                                                                                          │
    │ ├─🗎 run.sh.bak                                                                                                                       │
    │ └─🗎 stuff.txt                                                                                                                        │
    └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
    ?  Allow sending metadata? [y/N]: y
  
?  >  

⠏ Waiting... (Ctrl+C to stop)

─── Assistant ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
❝  I can see several files in your ~/Sync directory. Let me examine the contents of the potentially executable files (shell scripts and Python files) to check if they contain any dangerous commands.
[ Requirements (3) ]
  [ Read (3) ]
    ❝  Checking the dev.sh shell script for potentially dangerous commands
    🗎  ~/Sync/dev.sh  (/home/francisco/Sync/dev.sh)
    ❝  Checking the hello.py Python script for potentially dangerous code
    🗎  ~/Sync/hello.py  (/home/francisco/Sync/hello.py)
    ❝  Checking the run.sh.bak backup shell script for potentially dangerous commands
    🗎  ~/Sync/run.sh.bak  (/home/francisco/Sync/run.sh.bak)

```
</details>

---

## 🧩 Plugins

Solveig has an extensible plugin system that automatically discovers and loads plugins on startup.

**Plugin Types:**
1. **Hook plugins**: Use `@before()` or `@after()` decorators to validate or process existing requirements (file/command operations)
2. **Requirement plugins**: Create new operation types that the LLM can request - things like database queries, API calls, directory trees, or specialized file operations
3. **Plugin tests**: Add comprehensive test suites in `tests/plugins/test_my_plugin.py`

**Adding a hook plugin:**
1. Create a file in `solveig/plugins/hooks/my_plugin.py` 
2. Use decorators: `@before(requirements=(CommandRequirement,))`, `@after()`, both, or neither
3. Add tests in `tests/plugins/test_my_plugin.py` following the existing patterns
4. Plugins auto-load when Solveig starts - no configuration needed!

**Adding a requirement plugin:**
1. Create a new requirement class in `solveig/schema/requirements/my_requirement.py`
2. Extend the base `Requirement` class and implement `_actually_solve()` method
3. Add the new requirement type to `solveig/schema/requirements/__init__.py`
4. Create corresponding result class in `solveig/schema/results/my_result.py`  
5. Update the LLM system prompt examples to show the new capability
6. Add comprehensive tests for both success and failure cases

Check out `solveig/plugins/hooks/shellcheck.py` and `tests/plugins/test_shellcheck.py` for complete hook examples.
The existing requirement types in `solveig/schema/requirements/` show patterns for implementing new operations.


### Examples:

*click to expand:*

<details>
<summary><b>Block dangerous commands with custom patterns</b></summary>

```python
from solveig.plugins.hooks import before
from solveig.plugins.exceptions import SecurityError
from solveig.schema.requirements import CommandRequirement

@before(requirements=(CommandRequirement,))
def block_dangerous_commands(config, interface, requirement):
    """Block commands that could be dangerous to system security."""
    dangerous_patterns = [
        "sudo chmod 777",
        "wget http://",  # Block HTTP downloads
        "curl http://",
        "dd if=",        # Block disk operations
    ]
    
    for pattern in dangerous_patterns:
        if pattern in requirement.command:
            raise SecurityError(f"Blocked dangerous command pattern: {pattern}")
```
</details>

<details>
<summary><b>Anonymize all paths before sending to LLM</b></summary>

```python
import re
from pathlib import PurePath
from solveig.plugins.hooks import after
from solveig.exceptions import ProcessingError
from solveig.schema.requirements import ReadRequirement, WriteRequirement

@after(requirements=(ReadRequirement, WriteRequirement))
def anonymize_paths(config, interface, requirement, result):
    """Anonymize file paths in results before sending to LLM."""
    try:
        original_path = str(result.metadata.path)
    except:
        return
    anonymous_path = re.sub(r"/home/\w+", "/home/jdoe", original_path)
    anonymous_path = re.sub(r"^([A-Z]:\\Users\\)[^\\]+", r"\1JohnDoe", anonymous_path, flags=re.IGNORECASE)
    result.metadata.path = PurePath(anonymous_path)
```
</details>

---

## 🤝 Contributing

We use modern Python tooling to maintain code quality and consistency:

### Development Tools

All code is automatically checked on `main` and `develop` branches:
1. **Formatting**: `black .` - Ensures consistent code style
2. **Linting**: `ruff check .` - Catches potential bugs and code quality issues  
3. **Type checking**: `mypy solveig/ scripts/ --ignore-missing-imports` - Validates type hints
4. **Testing**: `pytest` - Runs full test suite with coverage reporting

### Testing Philosophy

Solveig follows **strict testing guidelines** to ensure reliability and safety:

#### Test Coverage Requirements
- **Success and failure paths**: Every feature must test both successful execution and error conditions
- **Mock only when necessary**: Mock only low-level I/O behavior with potential side effects
- **No untested code paths**: All business logic, error handling, and user interactions must be tested

#### Testing Architecture

**Test Safety Philosophy**: Unit tests must achieve high coverage while being completely safe to run. Our mocking approach ensures tests never touch real files, run real commands, or require user interaction.

**Core Mocking Infrastructure**:
- **MockClient
- **MockFilesystem**: Elaborate wrapper around `@patch()` calls that simulates complete file operations
- **MockInterface**: Wrapper around `@patch()` calls for user input/output without actual terminal interaction  
- **Plugin isolation**: Tests call `filter_hooks()` with specific configs to ensure plugin state isolation
- **Automatic mocking**: `conftest.py` automatically applies mocks via `@pytest.fixture(autouse=True)`

**Unit Tests (`tests/unit/`)**:
- Mock all I/O and side-effect operations (file system, user interface, external commands)
- Tests like `TestReadRequirement.test_successful_reads_with_mock_fs()` prove mock isolation by creating files at paths like `/test/readable.txt` that don't exist on the real filesystem
- Config tests use `cli_args` to bypass reading sys.argv and pass mock values without complex patching

**Integration Tests (`tests/integration/`)**:
- Allow real file I/O operations using temporary directories  
- Mock only user interactions and LLM responses to avoid interactive prompts
- Test complete conversation flows with `MockLLMClient` (thin wrapper around `@patch()`)

**The apparent complexity serves a critical purpose**: achieving 87%+ coverage while guaranteeing tests cannot damage your system or require manual intervention.

**Mock Filesystem Safety Proof**: Tests like `TestReadRequirement.test_successful_reads_with_mock_fs()` prove our mock filesystem works by creating files at paths like `/test/readable.txt` that don't exist on the real filesystem, then successfully reading them through the requirement system. The fact that these tests pass demonstrates that our mock filesystem is intercepting all file operations, ensuring no real files are touched during unit testing.

#### Running Tests

```bash
# Install with testing dependencies:
pip install -e .[dev]

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only  
python -m pytest tests/integration/ -v

# Specific test class
python -m pytest tests/unit/test_main.py::TestInitializeConversation -v

# Run all checks locally (same as CI) 
black . && ruff check . && mypy solveig/ scripts/ --ignore-missing-imports && pytest ./tests/ --cov=solveig --cov=scripts --cov-report=term-missing -vv

# Running mock client (works with config)
python -m tests.mocks.run_with_mock_client
```

#### Test Organization
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── mocks/          # Mock implementations
└── plugins/        # Plugin-specific tests
```

---

## 📈 Roadmap

**Next Steps:**
- Enhanced command validation with Semgrep static analysis  
- Second-opinion LLM validation for generated commands
- Improve test coverage
- API integration for Claude/Gemini
