# 📊 Proyecto 8: Calculadora de Métricas de Complejidad con Enfoque Funcional

**Universidad de Colima - Ingeniería en Computación Inteligente**  
**Materia**: Programación Funcional  
**Profesor**: Gonzalez Zepeda Sebastian  
**Semestre**: Agosto 2025 - Enero 2026

## Implementado actualmente

- [`src/analizador.py`](src/analizador.py) analiza el AST de un archivo Python. Identifica funciones síncronas y asíncronas y devuelve una tupla de instancias inmutables de `FunctionMetrics`.
- La complejidad ciclomática parte de 1. El analizador suma por `if`, `while`, `for`, `async for`, `except`, operadores booleanos y casos de `match`.
- Las líneas físicas se cuentan desde la definición de la función hasta su última línea, ambas incluidas. La profundidad mide el anidamiento de las estructuras de control que reconoce el analizador.
- [`src/validacion.py`](src/validacion.py) compara la complejidad ciclomática con Radon usando el nombre y la línea de definición.
- [`src/metricas.py`](src/metricas.py) calcula complejidad cognitiva, Halstead y altura del AST.
- [`src/cfg.py`](src/cfg.py) construye un grafo inmutable por función con secuencias, ramas, bucles y salidas explícitas.
- [`src/reportes.py`](src/reportes.py) combina las métricas y el CFG en texto, JSON y HTML. El JSON incluye nodos y aristas. El HTML muestra el resumen y las aristas de cada función.
- [`main.py`](main.py) recibe un archivo Python UTF-8. Las pruebas están en [`tests/`](tests/).

## Instalación y uso

Desde la raíz del repositorio, con Python 3.10 o posterior:

```bash
python -m pip install -r requirements.txt pytest
python main.py ruta/al/archivo.py
python main.py ruta/al/archivo.py --json > informe.json
python main.py ruta/al/archivo.py --html > informe.html
python -m pytest -v
```

## Reglas de las métricas

- **Cognitiva.** Una decisión suma 1 más el nivel de anidamiento según las estructuras reconocidas. Un `elif`, un `else` de condicional o bucle, cada nodo booleano y cada `break` o `continue` suman 1. Se usa una regla propia para Python y el cálculo excluye los ámbitos internos.
- **Halstead.** Enumera operadores aritméticos, unarios, booleanos, comparaciones y asignaciones, y cuenta nombres y literales como operandos dentro del cuerpo de la función. Con esos conteos calcula vocabulario, longitud, volumen, dificultad y esfuerzo.
- **Altura del AST.** Una hoja tiene altura 1. Un nodo con hijos tiene altura 1 más la mayor altura de sus hijos. El anidamiento de control se reporta aparte.

## Limitaciones conocidas

- En un `match` con `case 0` y `case _`, el analizador del proyecto suma ambos casos y devuelve 3. Radon 6.0.1 excluye el comodín del incremento y devuelve 2. Si Radon carece de una referencia para una función, el valor y la coincidencia aparecen como `null` en JSON.
- El CFG representa `if/else`, `for`, `async for`, `while`, `else` de bucle, retornos, `raise`, `break` y `continue`. Las expresiones se tratan como parte de su sentencia. Los bloques `try`, `with` y `match` se marcan como opacos, con una arista de continuación que aproxima su flujo.

## Trabajo futuro

- Índice de mantenibilidad con una definición explícita y pruebas de referencia.
- Modelar excepciones, gestores de contexto y `match` dentro del CFG.
- Ampliar las reglas de complejidad cognitiva y el inventario de Halstead.

## Fundamentos académicos

### AST

Un AST (Árbol de Sintaxis Abstracta, o Abstract Syntax Tree en inglés) es una representación en forma de árbol de la estructura de tu código fuente.
En lugar de leer el código como una simple línea de texto, el programa lo transforma en una jerarquía de datos donde cada elemento (una variable, una operación, un bucle) es un nodo.

¿Qué es y para qué sirve?

• Simplificación: Omite detalles innecesarios del código original (como paréntesis, puntos y comas o espacios en blanco) y deja solo la lógica pura.
• Traducción a datos: Convierte el texto del código en un objeto que los programas pueden analizar, modificar o transformar.
• Compiladores e intérpretes: Es el paso intermedio tras leer el texto (analizador léxico/sintáctico) antes de generar código de máquina o código intermedio.
• Herramientas de análisis (SAST / Linters): Permiten a herramientas como ESLint, Babel o analizadores de seguridad revisar el código en busca de errores, malas prácticas o vulnerabilidades.

### Pattern matching

En programación funcional, un match (o pattern matching / coincidencia de patrones) es un mecanismo que permite comparar un valor o estructura de datos contra uno o varios patrones para seleccionar una rama de código y, opcionalmente, descomponer (destructurar) el objeto para extraer sus partes internas.

Características principales

* Comparación estructural: No solo evalúa la igualdad de valores simples (como números o textos), sino que verifica la forma, el tipo o la composición interna de estructuras complejas (como listas, árboles o tipos de datos algebraicos).
* Desestructuración: Permite extraer variables directamente de los datos mientras se evalúa el patrón.
* Evaluación como expresión: A diferencia de una instrucción switch tradicional en lenguajes imperativos, un match suele retornar un valor (es una expresión).
* Patrón comodín (wildcard): Se utiliza un símbolo (como _) para capturar cualquier otro caso que no haya coincidido con los patrones anteriores.

### Radon

Radon es una librería de Python que sirve para analizar el código fuente y calcular métricas de calidad y complejidad. Se utiliza principalmente para detectar bloques de código difíciles de leer o mantener y facilitar la refactorización.

Funciones y métricas principales

Puedes usar Radon desde la línea de comandos o integrarla en flujos de trabajo (como CI/CD o linters) para obtener cuatro tipos de análisis:
* Complejidad ciclomática (cc). Cuenta el número de caminos independientes o puntos de decisión (como bucles for o condicionales if) en una función. Califica el código con letras de la A (muy simple) a la F (muy complejo y propenso a errores).
* Índice de mantenibilidad (mi). Calcula una puntuación del 0 al 100 que indica qué tan fácil es mantener un archivo. Combina la complejidad ciclomática, el volumen de código y las líneas de comentarios.
* Métricas sin procesar (raw). Cuenta datos básicos del archivo, como el total de líneas de código (LOC), líneas lógicas (LLOC) y líneas de comentarios.
* Métricas de Halstead (hal). Evalúa la complejidad basándose en la cantidad de operadores (palabras clave, símbolos) y operandos (variables, valores) para estimar el esfuerzo de desarrollo y posibles errores.

El proyecto usa la complejidad ciclomática de Radon. Las demás métricas de la biblioteca forman parte del contexto académico.

## Referencias

- McCabe, T.J. (1976). *A Complexity Measure*
- Halstead, M.H. (1977). *Elements of Software Science*
- **Radon**: https://radon.readthedocs.io/
- **SonarSource Cognitive Complexity**: https://www.sonarsource.com/

## Licencia

Proyecto académico - Universidad de Colima © 2025
