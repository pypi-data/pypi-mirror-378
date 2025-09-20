from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from typing import Iterable, List

from .base import Symbol, SymbolExtractor

# Node code we run via `node -e`. It uses ts-morph to parse a single file and
# prints a JSON array of symbol dicts to stdout.
_TS_MORPH_SCRIPT = r"""
const fs = require('fs');
let tsMorph;
try {
  tsMorph = require('ts-morph');
} catch (e) {
  console.error('ts-morph not found: ' + e.message);
  process.exit(12);
}
const { Project } = tsMorph;

function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error('No file path provided to ts-morph bridge.');
    process.exit(2);
  }
  const content = fs.readFileSync(filePath, 'utf8');
  const project = new Project({
    useInMemoryFileSystem: false,
    compilerOptions: { allowJs: true, target: 99, jsx: 2 } // ESNext, React JSX
  });
  const sf = project.createSourceFile(filePath, content, { overwrite: true });

  const syms = [];

  // Top-level functions
  for (const fn of sf.getFunctions()) {
    syms.push({
      name: fn.getName() || '<anonymous>',
      kind: 'function',
      line: fn.getStartLineNumber(),
      col: 0,
      signature: (fn.getText().split('{')[0] || '').trim()
    });
  }

  // Classes + methods
  for (const cls of sf.getClasses()) {
    const clsName = cls.getName() || '<anonymous>';
    syms.push({
      name: clsName,
      kind: 'class',
      line: cls.getStartLineNumber(),
      col: 0,
      signature: undefined
    });
    for (const m of cls.getMethods()) {
      syms.push({
        name: `${clsName}.${m.getName()}`,
        kind: 'method',
        line: m.getStartLineNumber(),
        col: 0,
        signature: (m.getText().split('{')[0] || '').trim()
      });
    }
  }

  // Interfaces
  for (const i of sf.getInterfaces()) {
    syms.push({
      name: i.getName() || '<anonymous>',
      kind: 'interface',
      line: i.getStartLineNumber(),
      col: 0,
      signature: undefined
    });
  }

  // Top-level variables (const/let)
  for (const v of sf.getVariableDeclarations()) {
    // only include top-level declarations
    const isTop = v.getParent().getParent() === sf;
    if (!isTop) continue;
    syms.push({
      name: v.getName(),
      kind: 'variable',
      line: v.getStartLineNumber(),
      col: 0,
      signature: undefined
    });
  }

  console.log(JSON.stringify(syms));
}

try {
  main();
} catch (e) {
  console.error('ts-morph bridge error: ' + e.stack);
  process.exit(1);
}
"""


def _ensure_node_available() -> None:
    if shutil.which("node") is None:
        raise FileNotFoundError(
            "Node.js binary 'node' not found on PATH. Install Node (>=16) to enable the "
            "TypeScript/JavaScript symbol extractor."
        )


def _run_ts_morph(tmp_path: str) -> List[dict]:
    """
    Invoke the inline ts-morph script against the given temp file path and
    return an array of symbol dicts.
    """
    _ensure_node_available()
    try:
        proc = subprocess.run(
            ["node", "-e", _TS_MORPH_SCRIPT, tmp_path],
            check=False,
            text=True,
            capture_output=True,
            timeout=15,
        )
    except FileNotFoundError:
        # Surface a clearer message for callers.
        raise FileNotFoundError("Node.js 'node' executable not found")  # noqa: B904

    if proc.returncode != 0:
        # Common case: ts-morph module not installed.
        if "ts-morph not found" in (proc.stderr or ""):
            raise RuntimeError(
                "The 'ts-morph' package is not available to Node. "
                "Add `npm install --save-dev ts-morph` (or yarn/pnpm equivalent) "
                "in your repo or ensure it’s present in the CI environment."
            )
        raise RuntimeError(
            f"ts-morph analysis failed (exit {proc.returncode}). stderr:\n{proc.stderr}"
        )

    try:
        data = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as err:
        raise RuntimeError("Failed to parse ts-morph output as JSON") from err
    if not isinstance(data, list):
        raise RuntimeError("Unexpected ts-morph output shape (expected list)")
    return data


class TSSymbolExtractor(SymbolExtractor):
    """
    Symbol extractor for JavaScript / TypeScript using ts-morph.

    This class conforms to the SymbolExtractor Protocol; the plugin loader will
    normalize `.name` to the entry-point name at runtime, but we set a default here.
    """

    name = "ts-morph"

    def languages(self) -> Iterable[str]:
        return ("javascript", "typescript", "jsx", "tsx")

    def extract(self, path: str, content: str) -> List[Symbol]:
        # Write the content to a temp file so ts-morph can resolve the file kind by extension.
        suffix = ".ts"
        lower = path.lower()
        if lower.endswith((".tsx", ".jsx", ".mjs", ".cjs", ".js", ".ts")):
            suffix = "." + lower.split(".")[-1]

        with tempfile.NamedTemporaryFile(mode="w+", suffix=suffix, delete=True) as tmp:
            tmp.write(content)
            tmp.flush()

            raw_syms = _run_ts_morph(tmp.name)

        symbols: List[Symbol] = []
        for s in raw_syms:
            # Defensive extraction with defaults
            name = str(s.get("name", ""))
            kind = str(s.get("kind", "symbol"))
            line = int(s.get("line", 0) or 0)
            col = int(s.get("col", 0) or 0)
            signature = s.get("signature")
            symbols.append(
                Symbol(
                    name=name,
                    kind=kind,
                    path=path,
                    line=line,
                    col=col,
                    signature=str(signature) if signature is not None else None,
                    doc=None,
                )
            )
        return symbols
