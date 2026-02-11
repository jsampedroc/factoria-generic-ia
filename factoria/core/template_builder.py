import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateBuilder:
    def __init__(self):
        # Localizamos la carpeta de templates relativa a este archivo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_path = os.path.join(base_dir, "templates")
        
        self.env = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_path: str, data: dict) -> str:
        """
        Renderiza una plantilla (ej: 'python/fastapi_service.j2') 
        con los datos proporcionados.
        """
        template = self.env.get_template(template_path)
        return template.render(**data)