# Picard MCP on NixOS

## Scope

Source: `PaulFaguet/mcp-picard` (MIT), a stdio MCP for the public `picard.fr` frozen-product catalogue. It provides search, details, category browsing, promotions, nutrition comparison, a best-effort store finder, and an in-memory planning cart.

It does **not** authenticate to Picard checkout. Its cart is local process memory. The catalogue is French; do not infer Luxembourg store availability.

## Install pattern

Keep the checkout under Hermes-owned state and isolate dependencies:

```bash
mkdir -p ~/.hermes/mcp
git clone --depth 1 https://github.com/PaulFaguet/mcp-picard.git ~/.hermes/mcp/mcp-picard
cd ~/.hermes/mcp/mcp-picard
uv venv .venv
uv pip install --python .venv/bin/python 'mcp>=1.0.0' 'curl_cffi>=0.7.0'
```

The project’s editable package metadata did not specify a Hatch wheel package selection. Installing its two runtime dependencies and launching the checked-out `src.server` module avoids relying on packaging metadata.

## NixOS wrapper

`curl_cffi` wheels may need the Nix C++ runtime outside an interactive shell. Resolve the current runtime path dynamically rather than hard-coding a Nix-store hash:

```bash
GCC_LIB=$(nix eval --raw nixpkgs#stdenv.cc.cc.lib.outPath)
```

Create a wrapper which sets `LD_LIBRARY_PATH="$GCC_LIB/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"`, changes into the repository, then executes `.venv/bin/python -m src.server`.

Register it:

```bash
printf 'Y\n' | hermes mcp add picard --command /bin/bash --args /absolute/path/to/run-hermes.sh
hermes mcp test picard
```

A new Hermes session is required before newly registered MCP tools appear.

## Live verification

Use an stdio MCP client or the future session’s Picard tool to call `search_products` once. On 2026-07-16, search for `legumes` returned a live product result, confirming the server could reach Picard’s catalogue after tool discovery.
