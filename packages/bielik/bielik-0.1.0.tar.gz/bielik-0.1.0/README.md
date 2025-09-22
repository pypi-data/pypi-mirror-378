# 🦅 bielik

[![PyPI](https://img.shields.io/pypi/v/bielik.svg)](https://pypi.org/project/bielik/)
[![Python](https://img.shields.io/pypi/pyversions/bielik.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/tomsapletta/bielik/python-app.yml?branch=main)](https://github.com/tomsapletta/bielik/actions)

Author: **Tom Sapletta**  
License: **Apache-2.0**

---

## 📌 Features

- **CLI** `bielik` — interactive chat shell with Ollama (REST → fallback `ollama` lib).  
- **Web server** (FastAPI on port 8888):  
  - `POST /chat` — send chat messages  
  - `WS /ws` — websocket chat  

---

## ⚙️ Installation

```bash
pip install bielik
```

Optional dependency (official Ollama lib):

```bash
pip install "bielik[ollama]"
```

---

## 🚀 Usage

### CLI

```bash
bielik
```

Wpisz wiadomości, zakończ `:exit`.

### Web API

```bash
uvicorn bielik.server:app --port 8888
```

* POST `/chat`:

```json
{"messages": [{"role":"user","content":"Hello!"}]}
```

* WebSocket `/ws`

---

## 🔧 Environment Variables

* `OLLAMA_HOST` — default: `http://localhost:11434`
* `BIELIK_MODEL` — default: `bielik`

---

## 📝 Development

```bash
git clone https://github.com/tomsapletta/bielik.git
cd bielik
python -m venv .venv
source .venv/bin/activate
pip install -e .[ollama]
```


# 📂 Struktura

```
bielik/
├── bielik/
│   ├── __init__.py
│   ├── cli.py
│   └── server.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_server.py
├── pyproject.toml
├── setup.cfg
├── MANIFEST.in
├── LICENSE
├── README.md
├── Makefile
└── .github/workflows/python-publish.yml
```



## 📜 License

[Apache License 2.0](LICENSE)


