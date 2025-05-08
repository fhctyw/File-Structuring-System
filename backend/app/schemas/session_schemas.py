from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, List, Dict, Literal, Optional

# довідники
AnalysisMethod  = Literal["META", "STRUCT", "SEMANTIC"]
StructAlgorithm = Literal["CLUSTER", "CRITERIA"]

# ---------- Запити ----------
class SessionCreate(BaseModel):
    directory: str = Field(..., example="/abs/path")
    recursive: bool = Field(True, description="Scan sub‑directories too")

class ProcessRequest(BaseModel):
    method: str      # "META" / "STRUCT" / "CONTENT"  (id з MethodRegistry)
    algorithm: str   # "CRITERIA" / "CLUSTER" …      (id з AlgorithmRegistry)

class ApplyRequest(BaseModel):
    dry_run: bool = Field(False, description="Preview only without real changes")

# ---------- Відповіді ----------
class SessionShort(BaseModel):
    id: UUID
    directory: str
    status: str

class SessionDetail(SessionShort):
    recursive: bool
    files_total: int
    analysis_method: Optional[AnalysisMethod]
    struct_algorithm: Optional[StructAlgorithm]
    actions_total: int

class ProcessSummary(BaseModel):
    files_analyzed: int
    actions_created: int
    breakdown: Dict[str, int]

class PreviewTree(BaseModel):
    tree: Dict[str, Any]  # { "folder": {subfolders…}, "file": "MOVE->…" }

class ApplyResult(BaseModel):
    applied: int
    failed: int
    errors: List[str] = []

class ProgressReport(BaseModel):
    percent: int = Field(0, ge=0, le=100)
    status: str

class MethodSchema(BaseModel):  # бажано описати окрему схему
    id: str
    description: str
    returns: List[Dict[str, Any]]
    layer: str | None = None
    domain: str | None = None
    action: str | None = None
    impl_class: str | None = None
    enabled: bool | None = True