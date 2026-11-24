# 📊 Proyecto 8: Calculadora de Métricas de Complejidad con Enfoque Funcional

**Universidad de Colima - Ingeniería en Computación Inteligente**  
**Materia**: Programación Funcional  
**Profesor**: Gonzalez Zepeda Sebastian  
**Semestre**: Agosto 2026 - Enero 2027

Analiza código Python por función sin ejecutarlo. El programa muestra sus métricas y dibuja su grafo de flujo de control (CFG).

## Arquitectura

- [`src/analizador.py`](src/analizador.py) identifica funciones síncronas y asíncronas en el AST y calcula sus métricas básicas.
- [`src/validacion.py`](src/validacion.py) obtiene la complejidad de Radon y la cruza por nombre y línea de definición.
- [`src/metricas.py`](src/metricas.py) calcula complejidad cognitiva, Halstead y altura del AST.
- [`src/cfg.py`](src/cfg.py) construye el grafo lógico con nodos y aristas inmutables.
- [`src/visualizacion.py`](src/visualizacion.py) convierte el grafo a SVG sin dependencias gráficas.
- [`src/reportes.py`](src/reportes.py) reúne las métricas y el CFG en un informe común. [`main.py`](main.py) gestiona la entrada y selecciona el formato.

## Instalación y ejecución

Desde la raíz del repositorio, con Python 3.10 o posterior:

```bash
python -m pip install -r requirements.txt pytest
python main.py ejemplo.py
python main.py ejemplo.py --json > informe.json
python main.py ejemplo.py --html > informe.html
python -m pytest -v
```

El archivo debe tener extensión `.py`. Se lee como UTF-8 por defecto y admite la declaración de codificación de Python. La CLI termina con código 0 en caso de éxito, 1 si falla la lectura o el análisis y 2 si el uso es incorrecto.

El texto muestra cada función y el número de nodos y aristas. El JSON incluye las métricas, los nodos y las aristas en campos estructurados. El HTML muestra el mismo resumen y un SVG desplegable por función. Se puede abrir directamente en un navegador, incluso sin conexión.

## Métricas

- **Ciclomática.** Parte de 1 y suma por `if`, `for`, `async for`, `while`, `except`, operadores booleanos (un incremento por enlace `and` u `or`) y casos de `match`. Analiza el cuerpo de cada función y excluye la cabecera y los ámbitos internos. Radon se presenta como referencia independiente.
- **Líneas y anidamiento de control.** Las líneas físicas abarcan desde el `def` o `async def` hasta la última línea de la función, inclusive. El anidamiento mide la profundidad de las estructuras de control que reconoce el analizador.
- **Altura del AST.** Una hoja aporta 1. Un nodo con hijos aporta 1 más la mayor altura de sus hijos.
- **Cognitiva.** Regla propia del proyecto. `if`, bucles, `except`, `match` y expresiones condicionales suman 1 más su nivel de anidamiento. Cada `elif`, `else` de condicional o bucle, nodo booleano, `break` y `continue` suman 1. Los ámbitos internos quedan fuera del cálculo de la función externa.
- **Halstead.** El subconjunto de operadores incluye operaciones binarias, unarias, booleanas, comparaciones y asignaciones. Los operandos son nombres y literales del cuerpo. Las apariciones se cuentan en `N1` y `N2`. Los distintos se cuentan en `n1` y `n2`, por clase de operador, identificador o par tipo-valor del literal. El vocabulario es `n1 + n2`, la longitud es `N1 + N2`, el volumen es `longitud × log₂(vocabulario)`, la dificultad es `(n1/2) × (N2/n2)` y el esfuerzo es `dificultad × volumen`. Para un vocabulario vacío, el volumen es cero. Si no hay operandos, la dificultad es cero.

## CFG y visualización

El grafo conecta la entrada con las sentencias y la salida. Un condicional tiene aristas verdadera y falsa. Un bucle enlaza su cabecera con el cuerpo y con su continuación. Los retornos y `raise` van a la salida. `break` y `continue` usan los destinos del bucle correspondiente.

En el SVG, cada sentencia se identifica por su tipo y línea. Los terminales se distinguen en azul y las decisiones en amarillo. Las flechas etiquetadas muestran el destino del flujo. Los carriles laterales ayudan a distinguir los saltos y los bucles.

## Ejemplo y pruebas

Guarda en `ejemplo.py`:

```python
def doble_si_positivo(x):
    if x > 0:
        return x * 2
    return 0
```

El programa muestra complejidad ciclomática propia y de Radon de 2, complejidad cognitiva de 1, 4 líneas, anidamiento de 1 y un CFG con 5 nodos y 5 aristas. La suite comprueba el parser, las métricas, Radon, el grafo, el SVG, los formatos de reporte y los códigos de salida de la CLI.

## Limitaciones conocidas

- Con `case 0` y `case _`, la complejidad propia es 3 y Radon 6.0.1 devuelve 2. Radon también incrementa por el `else` de bucle y puede contar decisiones dentro de una lambda. Las reglas propias cuentan el bucle sin ese incremento y excluyen el cuerpo de la lambda. Si falta una referencia de Radon, su valor y la coincidencia aparecen como `null` en JSON.
- Los bloques `try`, `with` y `match` son opacos en el CFG. La arista de continuación aproxima su flujo y las expresiones quedan dentro de su sentencia. El SVG puede requerir desplazamiento horizontal para grafos grandes.
- Los inventarios de cognitiva y Halstead son convenciones del proyecto. Los resultados pueden diferir de los de otras herramientas.

## Trabajo futuro

- Modelar excepciones, gestores de contexto y `match` dentro del CFG.
- Evaluar el índice de mantenibilidad como métrica de archivo, con su propia referencia y sus unidades documentadas.

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

## Referencias académicas

### ACM Digital Library

- J. L. Elshoff and M. Marcotty, “On the use of the cyclomatic number to measure program complexity,” *ACM SIGPLAN Notices*, vol. 13, no. 12, pp. 29–40, 1978.

- G. K. Conrado, A. K. Goharshady, K. Kochekov, Y. C. Tsai, and A. K. Zaher, “Exploiting the Sparseness of Control-Flow and Call Graphs for Efficient and On-Demand Algebraic Program Analysis,” *Proceedings of the ACM on Programming Languages*, vol. 7, OOPSLA2, 2023.

### IEEE Xplore

- T. J. McCabe, “A Complexity Measure,” *IEEE Transactions on Software Engineering*, vol. SE-2, no. 4, pp. 308–320, 1976.

- G. A. Campbell, “Cognitive Complexity — An Overview and Evaluation,” in *2018 IEEE/ACM International Conference on Technical Debt (TechDebt)*, 2018.

- “Applying Halstead Software Science on Different Programming Languages for Analyzing Software Complexity,” in *2020 4th International Conference on Trends in Electronics and Informatics (ICOEI)*, 2020.

## Video representativo

- https://vt.tiktok.com/ZSsFd6way/

## Referencias técnicas

- Radon documentation: https://radon.readthedocs.io/
- SonarSource Cognitive Complexity: https://www.sonarsource.com/

## Integrantes y contribuciones

- Eduardo Antolín Herrera Solórzano:
  - Validación de complejidad ciclomática con Radon.
  - Pruebas de comparación entre el analizador propio y Radon.
  - Integración y pruebas del sistema.

- Luis Giovanni Pineda:
  - Analizador principal basado en AST.
  - Cálculo de complejidad ciclomática y métricas básicas.

- Miguel Ángel Palomino Aguilar:
  - Documentación y fundamentos teóricos del proyecto.

## Licencia

Proyecto académico - Universidad de Colima © 2025
