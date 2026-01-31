from crewai import Task

def build_backend_generation_task(backend_builder):
    return Task(
        description=(
            "Genera el código Java Spring Boot completo. "
            "REGLA DE ORO: Crea TODOS los archivos necesarios para que el proyecto compile, "
            "incluyendo entidades, repositorios, controladores y EVENTOS. "
            "Si una clase importa algo, ese algo DEBE ser creado. "
            "Usa 'file_writer' para guardar los archivos empezando por 'pom.xml' "
            "y siguiendo con 'src/main/java/...'."
        ),
        agent=backend_builder,
        expected_output="Proyecto Java completo y listo para ser compilado por Maven.",
    )
