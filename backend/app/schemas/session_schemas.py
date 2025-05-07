from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, List, Dict, Literal, Optional
from datetime import datetime

# довідники
AnalysisMethod  = Literal["META", "STRUCT", "SEMANTIC"]
StructAlgorithm = Literal["BY_TYPE", "CLUSTER", "CRITERIA"]

# ---------- Запити ----------
class SessionCreate(BaseModel):
    directory: str = Field(..., example="/abs/path")
    recursive: bool = Field(True, description="Scan sub‑directories too")

class AnalysisRequest(BaseModel):
    method: AnalysisMethod = Field(..., example="STRUCT")

class PlanRequest(BaseModel):
    algorithm: StructAlgorithm = Field(..., example="BY_TYPE")

class ApplyRequest(BaseModel):
    dry_run: bool = Field(False, description="Preview only without real changes")

# ---------- Відповіді ----------
class SessionShort(BaseModel):
    id: UUID
    directory: str
    status: str
    created_at: datetime

class SessionDetail(SessionShort):
    recursive: bool
    files_total: int
    analysis_method: Optional[AnalysisMethod]
    struct_algorithm: Optional[StructAlgorithm]
    actions_total: int

class AnalysisSummary(BaseModel):
    files_analyzed: int
    description_examples: List[str]

class PlanSummary(BaseModel):
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
