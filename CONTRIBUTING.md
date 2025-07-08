# Contributing to Gitbolt

Thank you for considering contributing to **Gitbolt**! 🎉
Your help is highly appreciated — whether you're fixing bugs, writing docs, improving performance, or suggesting new ideas.

---

## 🛠️ How to Contribute

### 1. **Clone the Repo**

```bash
git clone https://github.com/Vaastav-Technologies/py-gitbolt.git
cd py-gitbolt
```

### 2. **Set Up Your Environment**

We recommend using a virtual environment:

#### Option 1: Using `venv` + `pip`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . --group dev
```

#### Option 2: Using [`uv`](https://github.com/astral-sh/uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .  --group dev
```

### 3. **Pre-commit Hooks**

(If applicable) Set up pre-commit hooks for your local workflow:

```bash
pre-commit install
```

### 4. **Run Tests**

Make sure everything passes before submitting a PR:

```bash
pytest --doctest-modules
```

### 5. **Open a Pull Request**

* Fork the repository
* Create a new branch
* Make your changes
* Open a PR with a clear title and description

---

## 📋 Code Style

* Use [ruff](https://github.com/astral-sh/ruff) for formatting
* Use [mypy](http://mypy-lang.org/) for static typing
* Follow PEP8 standards

Run formatting + linting locally:

```bash
ruff check . --fix
ruff format .
mypy -p gitbolt
```

---

## 🧪 Testing

We use `pytest` for testing. Please write tests for any new features or bug fixes.
Test files are located under the `tests/` directory.

---

## 💡 Suggestions & Feature Requests

Have an idea or improvement? Feel free to open an [issue](https://github.com/your-username/gitbolt/issues) and describe it. We welcome feedback from everyone.

---

## 🤝 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to keep the community respectful and inclusive.

---

Thanks again for contributing! 🚀
