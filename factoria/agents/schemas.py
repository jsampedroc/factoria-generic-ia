from pydantic import BaseModel, Field
from typing import List, Optional

class PythonServiceSchema(BaseModel):
    class_name: str = Field(..., description="Nombre de la clase en CamelCase")
    description: str = Field(..., description="Descripción breve de lo que hace el servicio")
    extra_imports: List[str] = Field(default_factory=list, description="Lista de librerías necesarias")
    business_logic: str = Field(..., description="El cuerpo de la función principal. Solo lógica, sin definiciones de clase.")
    requirements: List[str] = Field(default_factory=list, description="Librerías de pip necesarias (ej: pandas, requests)")