# ADR-005: Pre-Configured Virtual Environment

**Status:** Accepted

**Date:** 2025-12-30

**Deciders:** Development Team

## Context

This is a **learning project** designed to help developers understand AI agent development with DIAL API. The onboarding experience significantly impacts learning outcomes.

Traditional Python projects require users to:
1. Install Python (correct version)
2. Create virtual environment
3. Activate environment
4. Install dependencies
5. Troubleshoot version conflicts

Each step introduces potential friction, especially for:
- Beginners unfamiliar with Python tooling
- Developers on different platforms
- Workshop/training scenarios with time constraints

We needed to decide whether to:
1. Follow standard approach (users create own venv)
2. Include pre-configured environment
3. Use Docker for complete environment
4. Provide multiple installation methods

Key considerations:
- Learning curve vs. best practices
- Setup time vs. repository size
- Platform compatibility
- Maintenance overhead

## Decision

**Include a pre-configured virtual environment** (`dial_simple_agent/`) in the repository with all dependencies pre-installed.

Users simply activate:
```bash
source dial_simple_agent/bin/activate
```

No `pip install`, no dependency resolution, no version conflicts.

## Consequences

### Positive

- **Zero-Setup Dependencies**: Users skip entire installation phase
- **Consistent Environment**: Everyone uses identical package versions
- **Faster Onboarding**: From clone to running agent in < 1 minute
- **Workshop-Friendly**: Ideal for training sessions with limited time
- **Reduced Support**: Fewer "it doesn't work" issues from dep conflicts
- **Beginner-Friendly**: No need to understand pip, venv, requirements.txt
- **Version Control**: Exact package versions preserved

### Negative

- **Repository Size**: +50MB (venv included in git)
- **Platform-Specific**: macOS/Linux binaries don't work on Windows
- **Security Concerns**: Shipping binaries raises trust issues
- **Maintenance Burden**: Must update venv when dependencies change
- **Not Best Practice**: Production projects shouldn't commit venvs
- **Git Noise**: Venv changes pollute commit history
- **Python Version Lock**: Tied to specific Python interpreter (3.13)

### Neutral

- **Learning Trade-off**: Faster start but skips important tooling knowledge
- **Disk Space**: Users need 50MB extra disk space

## Alternatives Considered

### Alternative 1: Standard Requirements.txt

**Approach:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Pros:**
- Industry standard practice
- Small repository
- Platform-agnostic
- Teaches proper Python workflow
- No security concerns

**Cons:**
- 5+ minutes setup time
- Potential version conflicts
- Requires working Python/pip
- Network dependency
- Complex troubleshooting

**Reason for rejection:** Learning project optimizes for getting started quickly. Users can learn proper venv creation in production projects.

### Alternative 2: Docker Container

**Approach:**
```dockerfile
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
CMD ["python", "-m", "task.app"]
```

**Pros:**
- Complete environment isolation
- Platform-agnostic
- Production-like setup
- Easy distribution

**Cons:**
- Docker learning curve
- Slower development (rebuild on changes)
- Harder to debug
- Overkill for small project
- Poor IDE integration

**Reason for rejection:** Docker adds complexity without proportional benefit for learning project.

### Alternative 3: Poetry/Pipenv

**Approach:**
```bash
poetry install
poetry shell
```

**Pros:**
- Modern dependency management
- Deterministic builds
- Lock file for reproducibility
- Cleaner than pip

**Cons:**
- Requires learning new tool
- Additional installation step
- Slower than included venv
- Overkill for 2 dependencies

**Reason for rejection:** Project has minimal dependencies (requests, pydantic). Advanced tooling not justified.

### Alternative 4: Conda Environment

**Approach:**
```bash
conda env create -f environment.yml
conda activate dial-agent
```

**Pros:**
- Popular in data science
- Cross-platform
- Handles non-Python deps

**Cons:**
- Large install (3GB+)
- Slower than pip
- Not universally installed
- Overkill for this project

**Reason for rejection:** Most developers don't have conda. Doesn't align with standard Python practices.

### Alternative 5: Multiple Installation Methods

**Approach:**
Provide all options:
- Quick: Included venv
- Standard: requirements.txt
- Production: Docker

**Pros:**
- Accommodates all users
- Shows different approaches
- Flexibility

**Cons:**
- Confusing documentation
- Three setups to maintain
- Users pick wrong option
- Testing complexity

**Reason for rejection:** Decision paralysis. Better to optimize for one primary workflow.

## Implementation Details

### Virtual Environment Creation

Original setup (done once):
```bash
python3.13 -m venv dial_simple_agent
source dial_simple_agent/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Result committed to git.

### Dependency Snapshot

```bash
$ pip list
Package      Version
------------ -------
certifi      2025.11.12
charset-normalizer 3.4.4
idna         3.11
pydantic     2.12.5
pydantic-core 2.41.5
requests     2.32.5
urllib3      2.6.2
typing-extensions 4.15.0
```

### Repository Structure

```
dial_simple_agent/
├── bin/
│   ├── activate        # Activation script
│   ├── python          # Python executable symlink
│   └── pip             # Pip executable symlink
├── include/
│   └── python3.13/     # Header files
├── lib/
│   └── python3.13/
│       └── site-packages/  # Installed packages
└── pyvenv.cfg          # Venv configuration
```

### Size Breakdown

```
du -sh dial_simple_agent/
52M    dial_simple_agent/
```

Acceptable for learning project repository.

### .gitignore Considerations

**Normal projects:**
```gitignore
venv/
.venv/
*.pyc
__pycache__/
```

**This project:**
```gitignore
# NOT ignoring dial_simple_agent/ venv
__pycache__/
*.pyc
```

Explicitly including venv is the exception.

## Platform Compatibility

### macOS/Linux
✅ **Works**: Binaries compatible

```bash
source dial_simple_agent/bin/activate
```

### Windows
❌ **Doesn't Work**: Different binary format

**Workaround:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Documented in [Setup Guide](../setup.md#alternative-create-new-virtual-environment).

## Security Considerations

### Trust Model
- Repository under EPAM control
- Pre-installed packages from PyPI
- Users should review before running

### Verification
Users can verify packages:
```bash
source dial_simple_agent/bin/activate
pip list --format=json | python -m json.tool
```

### Recommendation
For production or sensitive environments, create fresh venv:
```bash
python -m venv secure_venv
source secure_venv/bin/activate
pip install -r requirements.txt
```

## Educational Impact

### What Users Learn
✅ How to activate virtual environments
✅ DIAL API integration patterns
✅ Tool calling implementations
✅ Agentic design patterns

### What Users Skip
❌ Creating virtual environments
❌ Resolving dependency conflicts
❌ Understanding pip/PyPI

**Trade-off Accepted**: Focus on agent development, not Python tooling.

## Maintenance Strategy

### When to Update Venv
- Dependency version changes
- Python version upgrades
- Security patches in packages

### Update Process
```bash
# Activate environment
source dial_simple_agent/bin/activate

# Update packages
pip install --upgrade pydantic requests

# Freeze new versions
pip freeze > requirements.txt

# Commit updated venv
git add dial_simple_agent/
git commit -m "Update dependencies"
```

### CI/CD Considerations
- GitHub Actions can test with included venv
- Faster CI runs (no pip install step)
- Consistent test environment

## Related Decisions

- **ADR-004**: Dataclasses (minimal dependencies justify simple setup)

## Future Considerations

- **Multi-Platform Support**: Could provide Windows venv separately
- **Dependency Growth**: If deps exceed 10+, reconsider approach
- **Production Use**: For real deployment, switch to standard venv creation
- **Alternative Distribution**: Could use PyPI package instead

## Documentation Requirements

Must clearly communicate:
1. ✅ This is a learning project exception
2. ✅ Production projects use standard venv creation
3. ✅ Windows users need manual setup
4. ✅ Security verification steps available

See [Setup Guide](../setup.md) for user-facing documentation.

## References

- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [PEP 405 - Python Virtual Environments](https://peps.python.org/pep-0405/)
- [Python Packaging Best Practices](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
- [setup.md](../setup.md) - User setup instructions

---

**Last Updated**: 2025-12-30 | **Status**: Accepted | **Impact**: Low (project-specific)

## Decision Review Criteria

Reconsider this decision if:
- Repository exceeds 100MB
- Windows users comprise >30% of audience
- Project moves to production use
- Dependencies grow beyond 5 packages
- Security concerns raised
