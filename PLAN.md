# 🕸️ P4 — GraphRAG Multi-Agent Research System (Financial-Crime Intelligence)

> **Plan de proyecto** (vive en este repo como `PLAN.md`). **Estado:** ✅ Plan completo (14/14 módulos) · 🟡 Setup M0 hecho. Se implementa después de P3 (fase F7.5 del plan de Learning); varias piezas se benefician de los 16 GB.
> **Absorbe y supera** el proyecto del CV *Hybrid RAG & Multi-Agent Research System* (`Leito2/multi-agent-research-system`, que queda archivado aparte): mismos agentes Research / Fact-Auditing / Synthesis, mismo harness SDD, ahora con **GraphRAG**, ejecución paralela, MCP, memoria durable, humano en el bucle y evaluación rigurosa.
> Stack: LangGraph · Neo4j (Cypher, GDS: Leiden, PageRank; índice vectorial) · neo4j-graphrag · Graphiti (grafo temporal) · GLiNER · Qdrant + ChromaDB · sentence-transformers (`bge-small-en-v1.5`) en ONNX · Tavily · Gemma 4 31B (texto y visión) vía `llm-gateway` (P0) · MCP (servidores de herramientas) · Postgres (checkpointer de LangGraph) · `judgekit` (P2) + Langfuse + MLflow · FastAPI + SSE · Docker Compose
> Gasto: **$0** (free tiers de Google AI Studio, Groq y Tavily, solo con datos sintéticos o públicos; Ollama como respaldo local).

## Módulos del plan
| # | Sección | Estado |
|---|---|---|
| 0 | Herencia del proyecto multiagente del CV | ✅ |
| 1 | Visión, problema y frase del CV | ✅ |
| 2 | Arquitectura macro y flujo de una investigación | ✅ |
| 3 | Datos: grafo de transacciones, corpus documental, web y evidencia visual | ✅ |
| 4 | El grafo de conocimiento: esquema, construcción y GraphRAG | ✅ |
| 5 | El sistema multiagente | ✅ |
| 6 | Herramientas vía MCP, sandbox y seguridad | ✅ |
| 7 | Memoria, contexto y ejecución durable | ✅ |
| 8 | Harness de evaluación | ✅ |
| 9 | Harness Engineering: desarrollo dirigido por especificaciones (SDD) | ✅ |
| 10 | Observabilidad | ✅ |
| 11 | Presupuesto de recursos (8 GB / `⏳ 16GB`) y ejecución | ✅ |
| 12 | Estructura del repo y del README | ✅ |
| 13 | Hitos de implementación y criterios de aceptación | ✅ |
| 14 | Riesgos y pendientes | ✅ |

## Regla del README
README progresivo: **contexto teórico, conceptual y macro primero**; en cada componente, el detalle técnico al final. Incluye cómo funciona, los pasos para ejecutarlo y las alternativas de ejecución o despliegue (local primero).

---

## 0. Herencia del proyecto multiagente del CV

El repo original llegó a la fase *pre-apply* de su SDD: specs, 18 ADRs, contratos de agentes, proveedores (Gemma vía AI Studio, Hugging Face, mock) y observabilidad con MLflow implementados. P4 **contiene todo** eso como componentes reales y lo lleva más lejos.

### 0.1 Qué se conserva
| Elemento original | ADR original | En P4 | Sección |
|---|---|---|---|
| LangGraph `StateGraph` cíclico | ARCH-002 | Se conserva, con fan-out paralelo (`Send`) y subgrafos | §5 |
| Tres agentes: Research, Fact-Auditing, Synthesis | ARCH-003 | Se conservan, más Planner, Graph Analyst, Web Researcher, Vision Auditor, Code Verifier y Critic | §5 |
| Orquestador Leader **determinista** (nunca usa un LLM para transiciones) | HARNESS-001 | Se conserva como regla dura del grafo: las aristas condicionales leen el estado, no llaman al LLM | §5.2 |
| Bucle de auditoría acotado (máx. 3) con bandera de confianza degradada | ITER-014 | Se conserva, con contradicciones tipadas | §5.4 |
| Qdrant (primario) + ChromaDB (dev/tests) tras un protocolo `VectorStore` | ARCH-004 | Se conserva; se suma el índice vectorial de Neo4j para las semillas del grafo | §4 |
| `bge-small-en-v1.5` (384d) con sentence-transformers | EMB-010 | Se conserva, exportado a ONNX para CPU; e5 multilingüe como alternativa medida | §4.5 |
| `RecursiveCharacterTextSplitter` 512/64 | CHUNK-012 | Baseline de chunking; se compara con chunking por estructura | §3.2 |
| Umbral de similitud 0.70 | SIM-013 | Punto de partida; se calibra con el set de evaluación | §8 |
| Compactación de contexto: ventana deslizante (5) + resumen cada 10 turnos | CTX-015 | Se conserva por agente, con presupuesto de contexto medido | §7.2 |
| Tavily con backoff exponencial (3 reintentos) y modo solo-RAG si falla | TAV-016 | Se conserva; además el contenido web se trata como **no confiable** | §6 |
| Gemma 4 como núcleo, multimodal (visión) y con *function calling* | LLM-011 | Vía P0: `smart` y `vision` → Gemma 4 31B en Google AI Studio, con fallback local | §5.5 |
| Abstracción de proveedores (`LLMProvider`, `EmbeddingProvider`, fábrica, `mock`) | ARCH-005 | Se conserva; el `LLMProvider` por defecto habla con P0 | §5.5 |
| Herramienta de ejecución de código para verificación numérica | design.md | Sandbox aislado (contenedor sin red) expuesto por MCP | §6.3 |
| Auditoría multimodal (diagramas, capturas, PDFs) | design.md | Vision Auditor: recibos, capturas de comercios y gráficos vs datos del grafo | §5.3 |
| MLflow local (file-based) con respaldo `metrics.jsonl`, saneamiento (`content_`, `text_`, `doc_` bloqueados) y hashes SHA-256 | MLFLOW-018 | Se conserva igual; Langfuse se suma para trazas | §10 |
| *Fail-closed*: sin LLM no hay respuesta; sin evidencia, "evidencia insuficiente" | requirements.md | Requisitos EARS con test | §9 |
| SDD con harness `.harness/` (Alt-C): EARS, dos compuertas humanas, contratos de resultado, ADRs en JSON, contexto curado < 20%, diffs < 400 líneas | HARNESS-001, ARCH-009 | **Se conserva completo** como método de desarrollo de P4 | §9 |
| TDD con pytest, cobertura ≥ 80%, tipado estricto | ARCH-008 | Se conserva (mypy + ruff + pytest-cov) | §9 |

### 0.2 Qué se mejora
| Límite del original | Mejora en P4 |
|---|---|
| Solo RAG vectorial: falla en preguntas multi-hop y "globales" ("¿qué redes están activas?") | **GraphRAG**: búsqueda local (vecindarios), global (comunidades resumidas) e híbrida |
| Agentes secuenciales | Fan-out paralelo de investigadores con `Send` y reducción en el auditor |
| Herramientas acopladas al código | Servidores **MCP** reutilizables (también por Claude Code u otros clientes) |
| Sin memoria entre sesiones ni reanudación | Checkpointer en Postgres (reanudar, *time travel*), hallazgos escritos al grafo con procedencia |
| Sin humano en el bucle | Interrupciones de LangGraph antes de conclusiones de alto impacto |
| Objetivo ">85% de precisión multi-hop" sin método de medición | Set dorado con **verdad conocida** (las redes de fraude plantadas por el generador de P1), baselines y `judgekit` |
| El contenido web entra directo al prompt | Contenido externo marcado como no confiable, Prompt Guard en P0 y separación de instrucciones y datos |
| Gemma llamada directo, sin control de costos ni cuotas | Todo vía P0: caché, breaker, cuotas del free tier, presupuesto |

---

## 1. Visión, problema y frase del CV

### 1.1 El problema
Un analista de fraude o de prevención de lavado necesita responder preguntas que **ninguna fuente sola** responde:
- "¿Este usuario está conectado (por tarjeta, dispositivo o IP) a cuentas bloqueadas en los últimos 30 días? ¿Por qué camino?" → **grafo**.
- "¿El patrón de la red R-12 coincide con alguna tipología documentada en nuestras políticas?" → **grafo + documentos**.
- "¿Hay reportes públicos recientes de este tipo de esquema?" → **web**.
- "¿El monto del recibo que adjuntó el cliente coincide con la transacción?" → **visión + grafo**.
- "Resume las redes de fraude activas este mes y su impacto." → **pregunta global**: ningún chunk la contiene; hay que agregar sobre comunidades del grafo.

El RAG vectorial recupera fragmentos parecidos a la pregunta, pero no sigue relaciones de varios saltos ni agrega sobre todo el corpus. Un solo agente mezcla fuentes y se autoconfirma. P4 combina **GraphRAG** con un **equipo de agentes con roles separados** que se auditan entre sí, y responde con un **reporte citado** o con "evidencia insuficiente".

### 1.2 Qué construimos
1. **Grafo de conocimiento en Neo4j** con tres capas: transacciones (de P1, determinista), documentos (políticas y tipologías, por extracción) y hechos temporales (Graphiti), unidas por resolución de entidades.
2. **GraphRAG** con búsqueda local, global (comunidades Leiden con resúmenes) e híbrida (vector + grafo + BM25 con RRF), más herramientas Cypher parametrizadas y Text2Cypher validado.
3. **Sistema multiagente en LangGraph** con Leader determinista: Planner → investigadores en paralelo (Graph Analyst, Doc Researcher, Web Researcher, Vision Auditor, Code Verifier) → Fact-Auditor (bucle de contradicciones) → Synthesis → Critic → humano en el bucle.
4. **Herramientas como servidores MCP** y sandbox de código aislado.
5. **Memoria y ejecución durable**: checkpointer en Postgres, compactación de contexto, hallazgos persistidos en el grafo.
6. **Evaluación** con verdad conocida, baselines (RAG vectorial, Microsoft GraphRAG, LightRAG) y `judgekit` + Langfuse.
7. **API + UI con SSE** que muestra el avance de cada agente en vivo.
8. **Harness SDD** completo como método de desarrollo.

### 1.3 Métricas de éxito
| Tipo | Métrica | Meta |
|---|---|---|
| Calidad | Exactitud en preguntas multi-hop con verdad conocida | **> 85%** (la meta del proyecto original, ahora medida) |
| Calidad | Mejora frente al RAG solo vectorial en multi-hop y preguntas globales | Se reporta (pp de diferencia, con IC) |
| Calidad | Precisión de citas (la cita respalda la afirmación) | ≥ 95% |
| Auditoría | Precisión y recall de detección de contradicciones (inyectadas) | Se reporta |
| Abstención | F1 de abstención en preguntas sin respuesta | Se reporta |
| Grafo | Recall de las redes de fraude plantadas (comunidades Leiden vs `ring_id`) | Se reporta (ARI / pureza) |
| Costo | Tokens y llamadas por investigación; $ a precio de referencia | Se reporta |
| Latencia | Tiempo por investigación (p50/p95) y tiempo hasta el primer evento SSE | Se reporta |
| Ingeniería | Cobertura de tests | ≥ 80% |
| Harness | Cobertura EARS en `review.md` | 100% |

### 1.4 Frase del CV (plantilla)
> **GraphRAG Multi-Agent Research System** · LangGraph · Neo4j (GDS) · Graphiti · Qdrant · MCP · Gemma 4 · Tavily · Langfuse
> Financial-crime research agents that fuse a **live transaction knowledge graph**, private policy documents, web intelligence and **visual evidence**: a deterministic LangGraph orchestrator fans out graph, document, web, vision and code-verification agents, a fact-auditor resolves contradictions, and every report is cited or abstains. **{a}% accuracy on multi-hop questions with known ground truth (+{d} pp over vector RAG)**, {c}% citation precision, {r} fraud rings recovered via Leiden communities; built spec-first with EARS requirements and a SDD harness.

### 1.5 Narrativa para entrevista (30 segundos)
"Mi primer sistema multiagente solo hacía RAG vectorial más búsqueda web. Lo rehice con GraphRAG porque las preguntas de fraude son relacionales: quién comparte dispositivo con quién, qué red está activa. Construí el grafo desde los eventos de mi proyecto de fraude en tiempo real, así que tengo la verdad conocida de las redes plantadas y puedo medir la exactitud de verdad. Los agentes investigan en paralelo, un auditor busca contradicciones y nada sale sin citas; si no hay evidencia, el sistema lo dice."

---

## 2. Arquitectura macro y flujo de una investigación

```
            P1 (Postgres v_entity_edges / topic entity-edges)      Corpus: políticas, tipologías,
                         │ carga determinista                       casos (sintéticos + públicos)
                         ▼                                                 │ GLiNER + extract (P0)
 ┌──────────────────────────── Neo4j (grafo de conocimiento) ──────────────▼──────────────┐
 │ capa transaccional · capa documental · hechos temporales (Graphiti) · Findings          │
 │ GDS: Leiden (comunidades) + resúmenes · PageRank · índice vectorial de entidades        │
 └────────────▲────────────────────────────────────────────────────────────────────────────┘
              │ MCP: graph-mcp (Cypher parametrizado, local/global search)
 Qdrant / Chroma ◄── MCP: docs-mcp         Tavily ◄── MCP: web-mcp        sandbox ◄── MCP: code-mcp
              │                                  │                              │
 ┌────────────┴──────────────── LangGraph (Leader determinista) ───────────────┴───────────┐
 │ intake → planner → [Send: graph_analyst | doc_researcher | web_researcher |               │
 │                      vision_auditor | code_verifier]  (en paralelo)                       │
 │        → fact_auditor ──contradicción y iter < 3──► planner (re-investigar)               │
 │        → synthesis (reporte citado o "evidencia insuficiente") → critic (judgekit)        │
 │        → interrupt (humano) si la conclusión es de alto impacto → report                  │
 │ checkpointer: Postgres · compactación de contexto · presupuesto por investigación        │
 └───────────────┬──────────────────────────────────────────────────────────┬──────────────┘
                 │ todas las llamadas a LLM                                  │ SSE
                 ▼                                                          ▼
        llm-gateway (P0): smart · vision · extract · judge          API FastAPI + UI
```

### 2.1 Decisiones de diseño (ADRs resumidos)
- **ADR-1 · El grafo transaccional es determinista.** Las relaciones usuario–tarjeta–dispositivo–IP–comercio vienen de datos estructurados de P1; ningún LLM las inventa. El LLM solo extrae de documentos. Es más barato, más exacto y da verdad conocida para evaluar.
- **ADR-2 · Orquestación determinista (heredado).** Las transiciones del grafo de LangGraph dependen del estado (`needs`, `contradictions`, `iteration`), nunca de una llamada al LLM.
- **ADR-3 · Herramientas Cypher parametrizadas primero, Text2Cypher después.** Las preguntas frecuentes usan consultas fijas y probadas (seguras, rápidas). Text2Cypher solo para preguntas abiertas, con validación de esquema, modo solo-lectura, `LIMIT` obligatorio y timeout.
- **ADR-4 · Herramientas detrás de MCP.** Cada fuente es un servidor MCP independiente y testeable; los agentes las consumen con adaptadores MCP de LangChain. Cambiar o agregar una fuente no toca el grafo de agentes.
- **ADR-5 · El contenido externo es dato, no instrucción.** Todo resultado web o de documentos subidos se envuelve como dato delimitado, pasa por Prompt Guard (P0) y nunca puede disparar herramientas por sí mismo.
- **ADR-6 · Roles aislados con contexto curado (heredado).** Cada agente recibe solo su tarea y la evidencia pertinente, con un presupuesto de contexto (< 20% de la ventana) medido.
- **ADR-7 · Neo4j como base de grafos.** Es el estándar de la industria (Cypher, GDS, índice vectorial, ecosistema GraphRAG). Alternativas medidas o documentadas: Memgraph (streaming nativo), FalkorDB (sobre Redis, liviano).
- **ADR-8 · Todo LLM pasa por P0.** Caché, breakers, cuotas de free tier, guardrails y presupuesto centralizados.
- **ADR-9 · Humano en el bucle para conclusiones de alto impacto.** Recomendar bloquear una cuenta o reportar una red requiere aprobación explícita (interrupt de LangGraph).

### 2.2 Flujo de una investigación
1. `POST /investigations` con la pregunta (y adjuntos opcionales). Se crea un `thread_id` y la investigación corre en segundo plano; el cliente sigue el avance por SSE.
2. **Intake:** normaliza, detecta entidades mencionadas (GLiNER) y las enlaza a nodos del grafo.
3. **Planner:** descompone en sub-preguntas y decide qué fuentes necesita cada una (`needs_graph`, `needs_docs`, `needs_web`, `needs_vision`, `needs_code`). Salida estructurada validada.
4. **Fan-out:** un investigador por sub-pregunta y fuente, en paralelo (`Send`). Cada uno devuelve `Evidence` con procedencia.
5. **Fact-Auditor:** compara evidencias, detecta contradicciones (grafo vs web, recibo vs transacción, política vs hecho) y verifica afirmaciones. Si hay contradicciones y `iteration < 3`, vuelve al Planner con preguntas dirigidas.
6. **Synthesis:** reporte con cada afirmación citada (nodo, documento, URL o imagen), bandera de confianza y contradicciones no resueltas explícitas, o "evidencia insuficiente".
7. **Critic:** `judgekit` verifica afirmación por afirmación. Si falla, la síntesis se rehace una vez.
8. **Interrupt:** si el reporte recomienda una acción de alto impacto, espera aprobación humana.
9. **Report:** se persiste el reporte y los hallazgos (`Finding`) en el grafo, con procedencia.

---

## 3. Datos

### 3.1 Grafo transaccional (desde P1)
- **Carga histórica:** vista `v_entity_edges` de P1 (Postgres) → Neo4j con `MERGE` idempotente por lotes.
- **Carga en vivo (`⏳ 16GB`):** consumidor del topic `entity-edges` de P1.
- **Sin P1 levantado:** snapshot Parquet exportado por P1, o el generador de P1 en modo offline.
- **Verdad conocida:** el generador de P1 planta redes de fraude (`ring_id`, latente). Ese archivo se usa **solo para evaluar** (nunca se carga al grafo que ven los agentes).

### 3.2 Corpus documental
| Fuente | Contenido | Licencia |
|---|---|---|
| Políticas internas (sintéticas) | Reglas de prevención de fraude, umbrales, procedimientos de escalamiento | Propia |
| Tipologías | Descripciones de esquemas (cuentas mula, *card testing*, toma de cuentas, triangulación) basadas en reportes públicos | Verificar licencia de cada fuente pública |
| Notas de casos (sintéticas) | Casos cerrados con conclusiones, que mencionan entidades del grafo | Propia |
| Listas públicas de sanciones (opcional) | Entidades sancionadas como nodos | Verificar licencia (p. ej., uso no comercial) |

Chunking: baseline `RecursiveCharacterTextSplitter` 512/64 (heredado) frente a chunking por estructura; ambos medidos en §8.

### 3.3 Web
Tavily para tipologías y alertas públicas recientes, y para verificar entidades públicas. Con presupuesto de créditos por investigación y caché de resultados (Redis) para no repetir búsquedas.

### 3.4 Evidencia visual (sintética)
Recibos, capturas de páginas de comercios y gráficos **generados** (HTML renderizado a PNG) a partir de transacciones del grafo, con discrepancias plantadas (monto, fecha, comercio) para evaluar al Vision Auditor.

### 3.5 Set de evaluación (~300 preguntas, generado desde la verdad conocida + revisión manual)
| Tipo | % | Qué prueba |
|---|---|---|
| Multi-hop en el grafo (2–4 saltos) | 30% | Caminos y conexiones |
| Globales (comunidades, tendencias) | 15% | Búsqueda global |
| Grafo + documentos | 15% | Fusión de fuentes |
| Con contradicción plantada | 15% | Fact-Auditor |
| Visión (recibo vs transacción) | 10% | Vision Auditor |
| Sin respuesta | 10% | Abstención |
| Numéricas (agregados, proporciones) | 5% | Code Verifier |

---

## 4. El grafo de conocimiento

### 4.1 Esquema
```
(:User)-[:USES_CARD]->(:Card)          (:User)-[:USES_DEVICE]->(:Device)
(:User)-[:CONNECTS_FROM]->(:IpCountry) (:User)-[:PAYS {amount, decision, score, ts}]->(:Merchant)
(:Document)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(:Entity)      (:Typology)-[:DESCRIBED_IN]->(:Document)
(:Community {level, summary})<-[:IN_COMMUNITY]-(:User)          (:Finding {claim, confidence})-[:SUPPORTED_BY]->(evidencia)
```
Restricciones de unicidad por ID, índices de propiedades e **índice vectorial** sobre resúmenes de comunidad y descripciones de entidades.

### 4.2 Construcción
- **Capa transaccional:** carga determinista (ADR-1).
- **Capa documental:** GLiNER (CPU) para entidades + alias `extract` de P0 (salida estructurada) para relaciones; **resolución de entidades** (normalización, *fuzzy matching* y, en la zona gris, confirmación con el LLM).
- **Hechos temporales:** Graphiti para hechos con validez en el tiempo (`valid_at` / `invalid_at`), p. ej., "el comercio M cambió de categoría".
- **Comunidades:** GDS Leiden sobre el grafo de usuarios proyectado (conexiones por recursos compartidos); un resumen por comunidad generado por el LLM y guardado en el nodo (estilo Microsoft GraphRAG).

### 4.3 Modos de recuperación
| Modo | Cómo | Para qué preguntas |
|---|---|---|
| **Local** | Semillas por índice vectorial o por entidad enlazada → expansión de k saltos → caminos y propiedades | "¿Cómo se conecta X con Y?" |
| **Global** | Map-reduce sobre resúmenes de comunidades | "¿Qué redes están activas?" |
| **Híbrida** | Vector (Qdrant) + grafo + BM25, fusionados con RRF | Preguntas mixtas |
| **Cypher parametrizado** | Herramientas fijas: caminos más cortos, vecinos con decisión BLOCK, comunidades de un usuario, top-PageRank | Preguntas frecuentes del dominio |
| **Text2Cypher** | El LLM escribe Cypher con el esquema; se valida (solo lectura, `LIMIT`, timeout) y se corrige con el error | Preguntas abiertas |

### 4.4 Baselines externos
**Microsoft GraphRAG** y **LightRAG** indexan el mismo corpus documental (subset, por costo de indexación en el free tier) para comparar calidad y costo de construcción frente al pipeline propio.

### 4.5 Embeddings y vector stores
`bge-small-en-v1.5` en ONNX (CPU) por defecto, e5 multilingüe como alternativa. Qdrant (primario) y ChromaDB (tests y modo sin Docker) detrás del protocolo `VectorStore` heredado.

---

## 5. El sistema multiagente

### 5.1 Estado (`ResearchState`)
`question`, `thread_id`, `plan: list[SubQuestion]`, `evidence: list[Evidence]` (reducer de concatenación), `contradictions: list[Contradiction]`, `iteration`, `max_iterations=3`, `report`, `confidence`, `status`, `budget` (tokens y créditos web restantes), `needs_human`.

### 5.2 Roles
| Agente | Responsabilidad | Herramientas |
|---|---|---|
| **Leader** (determinista, sin LLM) | Ejecuta el grafo, aplica límites de iteración, presupuesto y compuertas | — |
| **Planner** | Descompone la pregunta y decide fuentes por sub-pregunta | Esquema del grafo, catálogo de herramientas |
| **Graph Analyst** | Búsqueda local, global, Cypher | `graph-mcp` |
| **Doc Researcher** | RAG sobre políticas, tipologías y casos | `docs-mcp` |
| **Web Researcher** | Búsqueda y extracción web, con contenido no confiable | `web-mcp` |
| **Vision Auditor** | Compara imágenes (recibos, capturas) con datos del grafo | alias `vision` de P0 |
| **Code Verifier** | Verificación numérica en sandbox | `code-mcp` |
| **Fact-Auditor** | Detecta contradicciones y afirmaciones sin respaldo; decide re-investigar | — |
| **Synthesis** | Reporte citado, banderas de confianza, "evidencia insuficiente" | — |
| **Critic** | Verificación afirmación por afirmación con `judgekit` | `judgekit` |

### 5.3 Vision Auditor
Recibe la imagen y los datos de la transacción enlazada; extrae los campos (monto, fecha, comercio) con el modelo de visión y los compara con el grafo. Las discrepancias son `Contradiction` con tipo `visual_vs_graph`.

### 5.4 Bucle de auditoría
Contradicciones tipadas (`graph_vs_web`, `doc_vs_graph`, `visual_vs_graph`, `numeric`) con severidad. Si quedan contradicciones de severidad alta y `iteration < 3`, el Planner recibe preguntas dirigidas para resolverlas. Al agotar las iteraciones, Synthesis reporta el conflicto con ambas fuentes citadas y confianza degradada (heredado).

### 5.5 Modelos (todos vía P0)
| Uso | Alias de P0 | Modelo principal | Respaldo |
|---|---|---|---|
| Planner, investigadores, síntesis | `smart` | Gemma 4 31B (AI Studio, free tier) | Groq Llama 3.3 70B → Ollama Qwen3 1.7B |
| Visión | `vision` | Gemma 4 31B (multimodal) | `mock` (la visión local no entra en 4 GB de VRAM junto al resto) |
| Extracción para el grafo | `extract` | Gemma 4 26B A4B (MoE) | Groq → Ollama |
| Crítica y evaluación | `judge` / `judge_golden` | Gemma 3 4B local / Gemma 4 31B | `mock` |

---

## 6. Herramientas vía MCP, sandbox y seguridad

### 6.1 Servidores MCP
| Servidor | Herramientas |
|---|---|
| `graph-mcp` | `shortest_path(a, b, max_hops)`, `neighbors(entity, rel, decision)`, `community_of(user)`, `community_summaries(top_k)`, `local_search(q)`, `global_search(q)`, `text2cypher(q)` |
| `docs-mcp` | `search_docs(q, top_k, filters)`, `get_chunk(id)` |
| `web-mcp` | `web_search(q, max_results)`, `extract(url)` (Tavily; backoff, caché, presupuesto de créditos) |
| `code-mcp` | `run_python(code, timeout)` en el sandbox |

Los servidores corren con transporte HTTP en el Compose y por `stdio` en tests; se prueban por separado del grafo de agentes.

### 6.2 Seguridad del contenido externo
Delimitado como dato, Prompt Guard en P0 (modo `monitor` → `enforce` tras medir), el Web Researcher no puede llamar a herramientas distintas de búsqueda y extracción, y las URLs seguidas se registran.

### 6.3 Sandbox de código
Contenedor dedicado sin red, usuario sin privilegios, sistema de archivos de solo lectura salvo `/tmp`, límites de CPU, memoria y tiempo, y solo librerías permitidas (pandas, numpy). Alternativas documentadas: microVMs (Firecracker) o servicios de sandbox gestionados.

### 6.4 Cypher seguro
Rol de Neo4j de solo lectura para los agentes, validación sintáctica, rechazo de cláusulas de escritura, `LIMIT` obligatorio y timeout de transacción.

---

## 7. Memoria, contexto y ejecución durable
### 7.1 Ejecución durable
Checkpointer de LangGraph en Postgres: cada paso se guarda; una investigación interrumpida (o esperando aprobación humana) se reanuda con su `thread_id`; *time travel* para depurar desde un paso anterior.
### 7.2 Contexto
Heredado: ventana deslizante de 5 turnos + resumen cada 10. Además, cada agente tiene un **presupuesto de contexto** y la evidencia se resume antes de pasar al auditor. Se mide el % de llenado por agente (meta < 20%, heredada del harness).
### 7.3 Memoria de largo plazo
Los hallazgos aprobados se escriben al grafo como `Finding` con procedencia, y una investigación futura los puede citar (con su fecha).

---

## 8. Harness de evaluación
| Nivel | Métricas |
|---|---|
| Respuesta | Exactitud contra la verdad conocida (exact match / F1 de tokens / juez), por tipo de pregunta |
| Citas | Precisión y cobertura de citas; `unsupported_claim_rate` |
| Auditoría | Precisión y recall de contradicciones plantadas, por tipo |
| Abstención | Precisión, recall y F1 |
| Grafo | Pureza y ARI de las comunidades frente a `ring_id`; exactitud de Text2Cypher (consulta válida y resultado correcto) |
| Sistema | Latencia por investigación, llamadas, tokens, créditos web, $ a precio de referencia, iteraciones de auditoría |

**Configuraciones comparadas:** (B0) RAG vectorial de un solo agente (el original del CV), (B1) multiagente con RAG vectorial, (B2) GraphRAG local, (B3) GraphRAG global, (B4) híbrido completo, (B5) B4 + web + visión + código, más Microsoft GraphRAG y LightRAG en el subset documental.

**Herramientas:** `judgekit` (P2) con panel de jueces, Langfuse (datasets, experiments, scores), MLflow (heredado, saneado). Compuertas en la CI con `mock`: exactitud de las herramientas Cypher, contratos MCP y forma del reporte (citas, abstención).

---

## 9. Harness Engineering: desarrollo dirigido por especificaciones (SDD)
Heredado completo del proyecto original y aplicado al desarrollo de P4 con Claude Code como implementador:
```
init → proposal → spec (EARS) → [COMPUERTA HUMANA] → design → [COMPUERTA HUMANA] → tasks → apply → verify → archive
```
- `.harness/tasks.json`: máquina de estados por feature.
- `.harness/agents/`: contratos de rol (`leader`, `spec-author`, `implementer`, `reviewer`) con entradas, salidas y restricciones.
- `.harness/skills/sdd-workflow/SKILL.md`: protocolo de fases y dependencias de artefactos.
- `.harness/memory/decisions.json`: ADRs; `supervision-guide.md`: runbook del supervisor humano.
- `.harness/specs/<feature>/`: `proposal.md`, `requirements.md` (EARS), `design.md`, `tasks.md` (tareas atómicas, diff < 400 líneas), `review.md` (cada requisito EARS → test).
- Contrato de resultado por fase: `status`, `executive_summary`, `artifact`, `next_recommended_action`, `risk`.
- Telemetría del harness: cobertura EARS, cobertura de tests, tamaño de diff y llenado de contexto (tabla de umbrales heredada).

---

## 10. Observabilidad
Langfuse: una traza por investigación con un span por nodo y por herramienta, scores de `judgekit`. MLflow: corridas de evaluación (file-based, `metrics.jsonl` de respaldo, saneamiento de `content_`/`text_`/`doc_`, hashes SHA-256). Prometheus: investigaciones activas, duración por nodo, iteraciones de auditoría, llamadas a herramientas, errores MCP, créditos web. Trazas OTel propagadas a P0.

---

## 11. Presupuesto de recursos y ejecución
| Servicio | RAM aprox. | Perfil |
|---|---|---|
| Neo4j (heap 512 MB + page cache 512 MB) | ~1.3 GB | `core` |
| Qdrant | ~300 MB | `core` |
| Postgres (checkpointer) | ~200 MB | `core` |
| Redis + `llm-gateway` | ~700 MB | `core` |
| API + agentes + servidores MCP | ~700 MB | `core` |
| Sandbox | ~200 MB | `core` |
| **Total** | **≈ 3.4 GB** 🟢 (sin P1 levantado) | |
| `⏳ 16GB` | P1 en vivo (`entity-edges`), Langfuse self-hosted, Microsoft GraphRAG completo | `full` |

Ollama corre nativo en Windows solo como respaldo. Ejecución: `make doctor` → `make up` → `make load-graph` → `make ask Q="..."` → UI en `localhost:8090`. Alternativas: Neo4j AuraDB Free para la demo pública (verificar límites), Codespaces.

---

## 12. Estructura del repo y del README
```
graphrag-research-agents/
├── README.md · PLAN.md · AGENTS.md · LICENSE · Makefile · docker-compose.yml · pyproject.toml (workspace uv)
├── .harness/ (tasks.json, agents/, skills/, memory/, specs/)
├── packages/researchcore/      # contratos (ResearchState, Evidence, Contradiction, Citation), esquema del grafo
├── services/
│   ├── agents/                 # grafo de LangGraph, roles, Leader
│   ├── mcp/ (graph, docs, web, code)
│   ├── ingest/                 # carga desde P1, extracción, Graphiti, comunidades
│   └── api/                    # FastAPI + SSE + UI
├── sandbox/ · infra/ (neo4j/, postgres/) · eval/ (dataset/, configs/, gates.yaml)
├── tests/ (unit/, contract/, integration/) — cada requisito EARS con su test
└── docs/ (adr/, results/, images/)
```
**Esqueleto del README (en inglés):** Part I (problem; concepts: knowledge graphs, GraphRAG local/global, multi-agent roles, contradiction auditing, MCP, durable execution, SDD), Part II (components), Part III (the graph: schema, construction, communities), Part IV (the agents), Part V (proof: baselines, results, judge validation), Part VI (run it), Part VII (reflection: what changed from the original system, limitations, future work).

---

## 13. Hitos de implementación y criterios de aceptación
**Definición de terminado:** CI en verde · cabe en 8 GB · README del hito · $0 · artefactos SDD del hito (spec EARS + review) · tag.

| Hito | Objetivo | Criterios de aceptación | Tamaño |
|---|---|---|---|
| **M0 · Bootstrap** ✅ | Repo, harness `.harness/`, contratos, Compose, CI, README esqueleto | `make doctor` pasa; CI en verde; spec EARS inicial | S |
| **M1 · Datos** | Esquema, carga desde P1 (o snapshot), corpus documental, imágenes sintéticas, set de evaluación v0 con verdad conocida | Grafo cargado e idempotente; set de 300 preguntas revisado | M |
| **M2 · Baseline B0** | RAG vectorial de un agente (el original) vía P0; harness de evaluación | Tabla B0; `judgekit` integrado | M |
| **M3 · Grafo + GraphRAG** | Herramientas Cypher, GDS Leiden + resúmenes, búsquedas local y global | B2 y B3 medidos; pureza/ARI de comunidades | L |
| **M4 · Capa documental** | GLiNER + `extract`, resolución de entidades, Graphiti, híbrida RRF | B4 medido; precisión de la extracción en una muestra etiquetada | L |
| **M5 · Multiagente** | Planner, fan-out con `Send`, Fact-Auditor con bucle, Synthesis, Critic, Leader, checkpointer, compactación | Investigación de punta a punta reanudable; contradicciones plantadas detectadas | L |
| **M6 · Web, visión y código** | `web-mcp` (Tavily), Vision Auditor, sandbox | B5 medido; recall de discrepancias visuales | M |
| **M7 · MCP, HITL, API y UI** | Servidores MCP, interrupts, FastAPI + SSE, UI | Una investigación se aprueba o rechaza desde la UI; los MCP pasan sus contratos | M |
| **M8 · Evaluación completa** | Todas las configuraciones + Microsoft GraphRAG y LightRAG; Langfuse experiments; compuertas en la CI | Tabla de resultados final; frase del CV con números | M |
| **M9 · Pulido y publicación** | Observabilidad, README completo, `review.md` con 100% EARS, `v1.0` | Una persona ajena lo corre desde el README | M |
| M10 · `⏳ 16GB` | Grafo en vivo desde P1, Langfuse self-hosted | Resultados `v1.1` | M |

**MVP para el CV:** M0 → M5 + M8 parcial (B0 vs B4/B5 con verdad conocida).
**Orden de recorte:** baselines externos → Graphiti → Text2Cypher → visión (se conservan grafo, multiagente y auditoría).

---

## 14. Riesgos y pendientes
| ID | Riesgo | Mitigación |
|---|---|---|
| R1 | Cuotas del free tier (Gemma 4 en AI Studio, Tavily) limitan la evaluación completa | P0 respeta las cuotas y cae a Groq/Ollama; caché de resultados web; evaluación por lotes en varios días |
| R2 | Indexar con Microsoft GraphRAG consume muchos tokens | Solo sobre el subset documental; se reporta el costo de construcción como resultado |
| R3 | La extracción de relaciones con modelos chicos es ruidosa | ADR-1 (la capa transaccional no depende del LLM); muestra etiquetada para medir precisión |
| R4 | Text2Cypher genera consultas incorrectas o peligrosas | Herramientas parametrizadas primero; validación y rol de solo lectura |
| R5 | Prompt injection vía contenido web | ADR-5, Prompt Guard en P0, herramientas restringidas por rol |
| R6 | Neo4j + el resto no caben en 8 GB junto a P1 | P1 no corre a la vez (snapshot); live en `⏳ 16GB` |
| R7 | Dependencias: P0 (aliases `smart`, `vision`, `extract`), P1 (`entity-edges`) y P2 (`judgekit`) | Contratos versionados; `mock` en P0; snapshot sintético si P1 no está listo |
| R8 | Scope creep (es el proyecto más ambicioso) | MVP M0–M5 + M8 parcial; orden de recorte |

**Verificar al implementar:** versión y licencia de Neo4j Community y del plugin GDS en Docker, API vigente de `neo4j-graphrag`, Graphiti y LightRAG, adaptadores MCP de LangChain, límites del free tier de Tavily y de Google AI Studio para Gemma 4 (texto y visión), licencias de las fuentes públicas de tipologías y sanciones, condiciones de Neo4j AuraDB Free.
