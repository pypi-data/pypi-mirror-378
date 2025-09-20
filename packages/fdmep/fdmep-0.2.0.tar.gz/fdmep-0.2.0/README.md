# fdmep — CLI para scaffolding de extensões pyRevit

[![PyPI version](https://img.shields.io/pypi/v/fdmep.svg)](https://pypi.org/project/fdmep/)
![Python versions](https://img.shields.io/pypi/pyversions/fdmep.svg)
![License](https://img.shields.io/badge/license-MIT-informational)

## Sobre o Projeto

**fdmep** é uma aplicação **CLI** para facilitar inicializações de extensões **pyRevit**.

### 1) Como usar

Instale via pip:

```bash
pip install fdmep
```

Inicialize um projeto:

```bash
fdmep install
```

> Requisitos: Python 3.9+, permissões de escrita no diretório atual. (pyRevit não é necessário para rodar o scaffolding, apenas para usar a extensão criada.)

---

# Sobre este Tutorial: Criando uma CLI Python publicável (ex.: `fdmep`)

Este guia mostra o passo a passo para criar uma aplicação **CLI** instalável via `pip` e que expõe um comando de terminal (por ex., `fdmep` com subcomando `install`). O fluxo usa **setuptools** e **pyproject.toml** com o layout moderno `src/`.

---

## 1) Estrutura mínima do projeto

```
fdmep/
├─ src/
│  └─ fdmep/
│     ├─ __init__.py
│     ├─ cli.py
│     └─ scaffolder.py      # sua lógica (criar pastas/arquivos etc.)
├─ pyproject.toml
├─ README.md
├─ LICENSE
└─ .gitignore
```

> Dica: o nome do pacote (`fdmep`) deve ser igual ao nome da pasta dentro de `src/`.

---

## 2) `pyproject.toml` (configuração do pacote)

Crie o arquivo `pyproject.toml` na raiz com o conteúdo abaixo:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fdmep"
version = "0.1.0"
description = "CLI para inicialização rápida de extensões pyRevit"
readme = "README.md"
authors = [{ name = "Seu Nome", email = "seuemail@example.com" }]
license = { text = "MIT" }
requires-python = ">=3.9"
dependencies = [
  "colorama>=0.4.6"
]

[project.urls]
Homepage = "https://github.com/seuuser/fdmep"
Issues = "https://github.com/seuuser/fdmep/issues"

# cria o executável de terminal `fdmep`
[project.scripts]
fdmep = "fdmep.cli:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

-   `project.scripts` → mapeia `fdmep` para a função `main` no módulo `fdmep.cli`.
-   `package-dir` e `packages.find` → dizem ao setuptools para procurar o pacote dentro de `src/`.

---

## 3) Código da CLI

### 3.1 `src/fdmep/__init__.py`

```python
__version__ = "0.1.0"
```

### 3.2 `src/fdmep/scaffolder.py` (sua lógica de negócio)

```python
# -*- coding: utf-8 -*-
import os

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except Exception:
    class _NoColor:
        def __getattr__(self, _): return ''
    Fore = Style = _NoColor()

def info(m): print(f"{Fore.CYAN}ℹ {m}{Style.RESET_ALL}")
def ok(m):   print(f"{Fore.GREEN}✔ {m}{Style.RESET_ALL}")
def warn(m): print(f"{Fore.YELLOW}▲ {m}{Style.RESET_ALL}")
def err(m):  print(f"{Fore.RED}✖ {m}{Style.RESET_ALL}")

def _ensure_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        ok(f"Criada pasta: {path}")
    else:
        info(f"Pasta já existe: {path}")

def run_create():
    \"\"\"Fluxo simples de demonstração para validar a CLI.\"\"\"
    info("Iniciando scaffolding da extensão pyRevit (demo).")
    _ensure_dir("MyExtension.extension")
    os.chdir("MyExtension.extension")
    _ensure_dir("MyPanel.panel")
    os.chdir("MyPanel.panel")
    _ensure_dir("MyCommand.pushbutton")
    ok("Extensão criada/atualizada! (demo)")
```

### 3.3 `src/fdmep/cli.py` (ponto de entrada da CLI)

```python
# -*- coding: utf-8 -*-
import argparse
from importlib.metadata import version, PackageNotFoundError

from fdmep.scaffolder import run_create
from fdmep import __version__

def main():
    parser = argparse.ArgumentParser(
        prog="fdmep",
        description="CLI para inicializar extensões pyRevit rapidamente."
    )
    parser.add_argument("--version", action="store_true", help="Mostra a versão e sai.")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("create", help="Executa o scaffolding/instalação da extensão.")

    args = parser.parse_args()

    if args.version:
        try:
            print(version("fdmep"))
        except PackageNotFoundError:
            print(__version__)
        return

    if args.command == "create":
        run_create()
        return

    parser.print_help()
```

---

## 4) Desenvolvimento local

### 4.1 Instalar em modo _editable_

No diretório raiz do projeto (onde está o `pyproject.toml`):

```bash
# Windows (com Python Launcher)
py -3.11 -m pip install -e .

# ou Linux/macOS
python -m pip install -e .
```

Agora você já tem o comando disponível no PATH:

```bash
fdmep --version
fdmep install
```

### 4.2 Rodar sem o wrapper (útil para debug)

```bash
py -3.11 -m fdmep.cli --version
py -3.11 -m fdmep.cli install
```

---

## 5) Empacotar e publicar

### 5.1 Gerar os artefatos

```bash
python -m pip install build
python -m build
# sairão arquivos em dist/*.whl e dist/*.tar.gz
```

### 5.2 Publicar (PyPI)

```bash
python -m pip install twine
twine upload dist/*
# será solicitado usuário/senha do PyPI
```

> Alternativa moderna com **uv**:
>
> ```bash
> uv build
> uv publish
> ```

---

## 6) TL;DR

1. Estrutura com layout `src/`
2. `pyproject.toml` usando setuptools e `project.scripts`
3. `cli.py` com `main()` + `scaffolder.py` com `run_create()`
4. `pip install -e .` para testar localmente
5. `python -m build` e `twine upload dist/*` para publicar

Pronto! Sua CLI estará instalável via `pip install fdmep` e executável como `fdmep create`. 🚀
