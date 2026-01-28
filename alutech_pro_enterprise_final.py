import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai import Agent

# 1. CONFIGURACIÓN DE ENTORNO
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"
os.environ["OPENAI_MODEL_NAME"] = "deepseek-chat"

file_tool = FileWriterTool()

# --- FUNCIÓN DE RECUPERACIÓN INTELIGENTE ---
def obtener_tareas_pendientes(todas_las_tareas):
    """
    Verifica si ya existen los artefactos base para no repetir el gasto de tokens.
    """
    print("\n🔍 Analizando estado de la factoría para optimizar saldo...")
    hay_backend = os.path.exists("./output/backend/pom.xml")
    hay_frontend = os.path.exists("./output/frontend/angular.json")
    
    if hay_backend and hay_frontend:
        print("✅ Estructura base detectada. Saltando a fases de Marketing, Validación y Entrega.")
        # Filtramos para ejecutar solo las tareas de marketing y la entrega final
        return [t for t in todas_las_tareas if "landing" in t.description or "VALIDACIÓN" in t.description]
    
    print("🆕 Proyecto nuevo o incompleto. Iniciando flujo de producción total.")
    return todas_las_tareas

# 2. EQUIPO DE ÉLITE COMPLETO (11 AGENTES)
po = Agent(role='Product Owner Industrial', goal='Superar a Cortizo/Exlabesa en flexibilidad.', backstory='Visionario SaaS experto en modelos de suscripción industrial.', verbose=True)
documentalista = Agent(role='Documentalista Técnico', goal='Digitalizar reglas de despiece de perfiles.', backstory='Experto en catálogos técnicos de aluminio (Cortizo/Exlabesa).', verbose=True)
analista = Agent(role='Ingeniero de Sistemas', goal='Diseñar motor de cálculo y algoritmos de optimización.', backstory='Matemático experto en Nesting 1D para perfiles de 6.5m.', verbose=True)
ux_ui = Agent(role='UX/UI Designer', goal='Crear un configurador visual y táctil para taller.', backstory='Especialista en interfaces industriales modernas.', verbose=True)
architect = Agent(role='Software Architect', goal='Diseñar arquitectura multi-tenant escalable.', backstory='Guru de Java 21 y Spring Boot 3.', verbose=True)
ciso = Agent(role='Security Engineer', goal='Protección de datos y cifrado.', backstory='Experto en ciberseguridad industrial.', verbose=True)
backend_arch = Agent(role='Senior Backend Architect', goal='Desarrollar API ejecutable con Maven.', backstory='Especialista en Spring Boot. Generas OBLIGATORIAMENTE pom.xml y estructura Maven.', tools=[file_tool], verbose=True)
frontend_arch = Agent(role='Senior Angular Architect', goal='Desarrollar SPA ejecutable con Angular CLI.', backstory='Maestro de Angular 17. Generas OBLIGATORIAMENTE angular.json y package.json.', tools=[file_tool], verbose=True)
qa_automation = Agent(role='QA Engineer', goal='Validar precisión milimétrica de cálculos.', backstory='Tester obsesivo con los decimales.', verbose=True)
marketing_copy = Agent(role='Growth Hacker Industrial', goal='Estrategia de ventas y copy de alta conversión.', backstory='Experto en marketing B2B industrial.', tools=[file_tool], verbose=True)
devops_writer = Agent(role='DevOps & Automation', goal='Orquestación total y scripts de arranque automático.', backstory='Guru de Docker. Aseguras que el proyecto compile y arranque con un clic.', tools=[file_tool], verbose=True)

# 3. FLUJO DE TAREAS INTEGRADO
t1_negocio = Task(description='Definir requerimientos: Gestión multimarca y presupuestos dinámicos.', agent=po, expected_output='Especificación funcional.')
t2_doc_tecnica = Task(description='Digitalizar reglas de series COR-70 y 4500: descuentos y herrajes.', agent=documentalista, expected_output='Matriz técnica de reglas.')
t3_algoritmo = Task(description='Diseñar la lógica matemática de despiece y optimización de corte.', agent=analista, expected_output='Algoritmos de optimización.', context=[t2_doc_tecnica])
t4_diseno = Task(description='Diseñar el configurador visual táctil para taller.', agent=ux_ui, expected_output='Guía de estilo y prototipo.', context=[t3_algoritmo])

# Tarea T5 Modificada: Foco en Inventario y Multi-tenant
t5_arch = Task(
    description='''Diseñar esquema DB multi-tenant que incluya:
    - Gestión de stock de barras y retales.
    - Tablas de series (perfiles y accesorios).
    - Relación de proyectos por taller (tenant).''',
    agent=architect,
    expected_output='Esquema SQL detallado y diseño de entidades.'
)

# Tarea T6 Modificada: Persistencia automática y Endpoints de Stock
t6_back = Task(
    description='''Programar en ./output/backend/. 
    IMPORTANTE: Configurar JPA para crear las tablas automáticamente al conectar con Postgres.
    Incluir endpoints para consultar stock de aluminio disponible.''',
    agent=backend_arch,
    expected_output='Código Java con persistencia automática de datos.',
    context=[t5_arch]
)

t7_front = Task(
    description='''Programar en ./output/frontend/. REQUISITO: angular.json, package.json y componentes. 
    Debe soportar 'npm install' y build dentro de un contenedor Docker.''',
    agent=frontend_arch, expected_output='Proyecto Angular CLI completo.', context=[t4_diseno, t5_arch]
)

t8_marketing = Task(
    description='Crear landing page y estrategia "Libertad Multimarca" en ./output/marketing/landing.md.',
    agent=marketing_copy, expected_output='Material de ventas profesional.', context=[t1_negocio]
)

t9_entrega = Task(
    description='''VALIDACIÓN Y AUTOMATIZACIÓN FINAL:
    1. Generar Dockerfiles (Multi-stage) para Backend y Frontend.
    2. Crear docker-compose.yml vinculando App, DB y Red interna.
    3. Generar archivo .env centralizado.
    4. Crear script 'start.sh' (Linux/Mac) y 'start.bat' (Win) que ejecute 'docker-compose up --build'.
    5. Escribir MANUAL DE TALLER en README.md con instrucciones de arranque.''',
    agent=devops_writer,
    expected_output='Entorno 100% automatizado y listo para producción.',
    context=[t6_back, t7_front]
)

# 4. LANZAMIENTO DINÁMICO
todas_las_tareas = [t1_negocio, t2_doc_tecnica, t3_algoritmo, t4_diseno, t5_arch, t6_back, t7_front, t8_marketing, t9_entrega]
tareas_finales = obtener_tareas_pendientes(todas_las_tareas)

factory = Crew(
    agents=[po, documentalista, analista, ux_ui, architect, ciso, backend_arch, frontend_arch, qa_automation, marketing_copy, devops_writer],
    tasks=tareas_finales,
    process=Process.sequential
)

print(f"🚀 INICIANDO PRODUCCIÓN: Trabajando en {len(tareas_finales)} tareas...")
factory.kickoff()