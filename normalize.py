import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
DOCS = ROOT / "docs"

BACKUP_DIR = ROOT / f"_backup_docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(exist_ok=True)

def backup_file(path: Path):
    if path.exists():
        shutil.copy(path, BACKUP_DIR / path.name)

def prepend_block(path: Path, block: str):
    content = path.read_text(encoding="utf-8")
    if block.strip() in content:
        return
    path.write_text(block + "\n\n" + content, encoding="utf-8")

def append_block(path: Path, block: str):
    content = path.read_text(encoding="utf-8")
    if block.strip() in content:
        return
    path.write_text(content + "\n\n" + block, encoding="utf-8")

# --- BLOQUES CANÓNICOS ---

SOURCE_OF_TRUTH = """
> 🔒 DOCUMENTO CANÓNICO
>
> Este archivo constituye la ÚNICA fuente de verdad técnica del subsistema
> JARVIS Commercial Bot.  
> Cualquier otro documento es derivado, explicativo o comercial.
"""

FASE_C_NOTICE = """
> ⚠️ IMPLEMENTACIÓN DE REFERENCIA (NO NORMATIVA)
>
> El código incluido a continuación es un ejemplo funcional.
> No constituye una decisión arquitectónica inmutable.
> Las decisiones canónicas se documentan fuera del código.
"""

NO_LEARNING_CONTRACT = """
## Contrato de Aprendizaje

Este subsistema **NO posee aprendizaje autónomo**.

- No ajusta pesos
- No modifica reglas
- No altera comportamiento por experiencia

Toda interacción se registra **únicamente con fines de observabilidad
y futura ingesta controlada**.
"""

OBSERVABILITY_CONTRACT = """
## Observabilidad (Principio Transversal)

La observabilidad **no es un módulo**, es una propiedad sistémica.

Todos los dominios del subsistema deben:
- Emitir logs estructurados
- Registrar métricas
- Permitir trazabilidad de decisiones
"""

RISKS_DECLARATION = """
## Riesgos Conocidos Postergados

Los siguientes riesgos han sido identificados y conscientemente postergados:

- Protección contra replay attacks
- Rate limiting avanzado
- Circuit breaker distribuido

Su mitigación está planificada para Fase D+.
"""

MATURITY_TABLE = """
## Estado de Madurez por Módulo

| Módulo        | Estado        |
|--------------|---------------|
| Gateway      | Estable       |
| Session      | Estable       |
| Rules        | Heurístico    |
| LLM Adapter  | Dependiente externo |
| Observability| Parcial       |
"""

DERIVED_NOTICE = """
> ℹ️ DOCUMENTO DERIVADO
>
> Este archivo **NO es fuente de verdad técnica**.
> Su contenido debe interpretarse como complementario.
"""

# --- EJECUCIÓN ---

def main():
    print("🔧 Normalizando documentación JARVIS...")

    # Detectar archivos
    tecnico = next(DOCS.glob("*tecnico*can*"), None)
    comercial = next(DOCS.glob("*comercial*"), None)
    readme = ROOT / "README.md"
    guia = next(ROOT.glob("*GUIA*"), None)

    for f in [tecnico, comercial, readme, guia]:
        if f and f.exists():
            backup_file(f)

    if tecnico:
        prepend_block(tecnico, SOURCE_OF_TRUTH)
        append_block(tecnico, NO_LEARNING_CONTRACT)
        append_block(tecnico, OBSERVABILITY_CONTRACT)
        append_block(tecnico, RISKS_DECLARATION)
        append_block(tecnico, MATURITY_TABLE)

    for f in [comercial, readme]:
        if f and f.exists():
            prepend_block(f, DERIVED_NOTICE)

    if guia:
        prepend_block(guia, FASE_C_NOTICE)

    print("✅ Normalización completada.")
    print(f"📦 Backup generado en: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
