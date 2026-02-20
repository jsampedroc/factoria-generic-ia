from pathlib import Path
from crewai import Task

def build_single_file_task(agent, file_path, relevant_domain, architecture):
    file_name = Path(file_path).stem
    ext = Path(file_path).suffix
    path_lower = file_path.lower()
   
   # ... (dentro de build_single_file_task) ...

    is_test = "test" in path_lower
    is_vo = "domain/valueobject" in path_lower
    is_model = "domain/model" in path_lower
    is_dto = "application/dto" in path_lower
    is_main = "mainapplication" in path_lower

    attributes = relevant_domain.get('attributes', [])

    extra_instructions = ""
    
    if is_main:
        extra_instructions = """
        ### INSTRUCCIONES PARA CLASE MAIN ###
        - Genera SOLO el contenido estático de la clase principal de Spring Boot.
        - DEBES DEVOLVER ÚNICAMENTE el código que va entre las llaves de la clase.
        - El contenido debe ser: 
          @SpringBootApplication
          public static void main(String[] args) {
              SpringApplication.run(MainApplication.class, args);
          }
        - NO añadas ninguna otra anotación, importación o código.
        """
    elif is_test:
        extra_instructions = """
        ### INSTRUCCIONES DE TEST UNITARIO ###
        1. Usa JUnit 5 (@ExtendWith(MockitoExtension.class)) y Mockito (@Mock, @InjectMocks).
        2. Genera SOLAMENTE el CONTENIDO de los métodos de prueba.
        3. **PROHIBICIÓN TOTAL**: No escribas NINGUNA declaración de clase, interfaz, o constructor (`public class...`, `@Data`, `@Builder`, `@NoArgsConstructor`, `ClassName() { ... }`).
        4. Empieza directamente con la anotación `@Test`.
        """
    elif is_vo or is_model or is_dto:
        extra_instructions = f"""
        ### INSTRUCCIONES DE POJO/MODEL/DTO/VALUE OBJECT ###
        1. ATRIBUTOS A GENERAR: {attributes}
        2. Genera SOLAMENTE los campos privados, getters y setters.
        3. NO uses anotaciones de Spring (@Component, @Service, etc.).
        4. **PROHIBIDO**: NO generes SETTERS públicos. Los Value Objects deben ser inmutables.
        5. Si es un Value Object, incluye métodos estáticos de fábrica como `public static {file_name} fromString(String value)`.
        6. Genera Getter, equals(), hashCode(), y métodos de fábrica estáticos (`fromString`, `generate`).
        """
    elif "controllers" in path_lower:
            extra_instructions = """
            ### INSTRUCCIONES DE CONTROLLER ###
            - Genera SOLAMENTE los métodos Spring (@GetMapping, @PostMapping, etc.) y sus cuerpos.
            - PROHIBIDO: No incluyas campos @Autowired ni la declaración de la clase.
            - PROHIBIDO: NO escribas la firma completa del método (NO incluyas 'public ResponseEntity<ChildDTO> createChild(...) {').
            - Usa el servicio inyectado como si ya existiera (ej: `paymentService.createPayment(...)`).
            - Genera SOLAMENTE el CUERPO de los métodos HTTP (@GetMapping, @PostMapping, etc.).
            - Usa los DTOs y Value Objects (ej: ChildDTO, ChildId) para las firmas de los parámetros que recibes o devuelves.
             """
    elif "repository" in path_lower:  #ultimo se puede eliminar bloque
            extra_instructions = """
            ### INSTRUCCIONES PARA REPOSITORIO JPA ###
            - Estás generando una INTERFAZ de Spring Data JPA.
            - Genera SOLO las firmas de los métodos personalizados (ej: List<Entity> findByStatus(String status);).
            - Si necesitas una consulta compleja, usa @Query.
            - PROHIBIDO: No escribas el cuerpo del método (no uses { ... }).
            - PROHIBIDO: No escribas la declaración de la clase ni @Repository.
            """
    else:
        # Lógica de Servicios, Controllers, Repositories (Implementaciones)
        extra_instructions = """
        ### INSTRUCCIONES DE MIEMBROS DE CLASE ###
        1. Escribe los CAMPOS PRIVADOS para dependencias usando inyección por constructor (ej: 'private final ChildRepositoryPort repository;').
        2. Escribe el CONSTRUCTOR de la clase para inicializar esos campos.
        3. Escribe los MÉTODOS COMPLETOS (Firma + Cuerpo). Ejemplo: 
           public Child save(Child child) { 
               return repository.save(child); 
           }
        
        ### PROHIBICIONES ESTRICTAS ###
        - NO escribas la cabecera de la clase 'public class {file_name} {'.
        - NO escribas 'package' ni 'imports' (el template se encarga).
        - NO uses anotaciones de clase como @Service, @RestController o @Slf4j.
        
        ### EXCEPCIÓN PARA REPOSITORIOS (PORT/JPA) ###
        - Si el archivo es una Interface (RepositoryPort), genera SOLO las firmas de los métodos: 'Child save(Child child);'.
        """

    prompt = f"""
### ROLE ###
Senior Java Expert. Escribiendo para: {file_name} ({file_path})

{extra_instructions}

### ¡¡PROHIBICIÓN CRÍTICA!! ###
- EMPIEZA DIRECTAMENTE con los atributos o métodos.
- NO ESCRIBAS la cabecera de la clase ("public class..."), "package", ni "import" estándar.

### CONTEXTO ###
{relevant_domain.get('entity')}

### FORMATO DE SALIDA (JSON ESTRICTO) ###
{{
  "imports": ["com.daycaremanagement.domain.valueobject.*"],
  "content": "// Escribe aquí solo los campos o métodos solicitados"
}}
"""
    return Task(description=prompt, agent=agent, expected_output="JSON con el fragmento de código solicitado.")