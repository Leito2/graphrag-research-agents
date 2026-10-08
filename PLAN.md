# 🕸️ P4 — GraphRAG Study Research Agents (Obsidian Second Brain)

> **Plan de proyecto, v2** (vive en este repo como `PLAN.md`). **Estado:** ✅ Plan completo (14/14 módulos) · 🟡 Setup M0 hecho. Se implementa después de P3 (fase F7.5 del plan de Learning), tras el curso C8 de GraphRAG.
> **v2 (2026-10-06):** el dominio pasa de investigación de fraude a **investigación de estudio sobre tu vault de Obsidian** (todas las notas en una misma carpeta), y **Tavily se reemplaza** por un stack de búsqueda propio y más robusto (SearXNG self-hosted + Crawl4AI + arXiv/OpenAlex + PyPI/GitHub). Ya no depende de P1.
> **Absorbe y supera** el proyecto del CV *Hybrid RAG & Multi-Agent Research System* (`Leito2/multi-agent-research-system`, archivado aparte): mismos agentes Research / Fact-Auditing / Synthesis y mismo harness SDD, ahora con **GraphRAG sobre tus propias notas**, ejecución paralela, MCP, memoria durable, humano en el bucle y evaluación con verdad conocida.
> Stack: LangGraph · Neo4j (Cypher, GDS: Leiden, PageRank; índice vectorial) · neo4j-graphrag · Graphiti (hechos temporales) · GLiNER · Qdrant + ChromaDB · `bge-small-en-v1.5` / e5 multilingüe (ONNX) · **SearXNG** · **Crawl4AI** · arXiv API · OpenAlex · PyPI JSON API · GitHub API · Exa (opcional) · Gemma 4 31B (texto y visión) vía `llm-gateway` (P0) · MCP · Postgres (checkpointer) · `judgekit` (P2) + Langfuse + MLflow · watchdog · FastAPI + SSE · Docker Compose
> Gasto: **$0** (SearXNG y Crawl4AI son self-hosted; arXiv, PyPI y GitHub gratis; OpenAlex con su cuota diaria gratuita; Gemma 4 por el free tier de Google AI Studio vía P0 con consentimiento; Ollama como respaldo local).

## Módulos del plan
| # | Sección | Estado |
|---|---|---|
| 0 | Herencia del proyecto multiagente del CV | ✅ |
| 1 | Visión, problema y frase del CV | ✅ v2 |
| 2 | Arquitectura macro y flujo de una investigación | ✅ v2 |
| 3 | El vault como fuente: lectura, actualización en vivo y escritura segura | ✅ v2 |
| 4 | El grafo de conocimiento y GraphRAG | ✅ v2 |
| 5 | El sistema multiagente y los modos de investigación | ✅ v2 |
| 6 | Búsqueda externa: por qué no Tavily y el stack que lo reemplaza | ✅ v2 |
| 7 | Herramientas vía MCP, sandbox, seguridad y privacidad | ✅ v2 |
| 8 | Memoria, contexto y ejecución durable | ✅ |
| 9 | Harness de evaluación con verdad conocida | ✅ v2 |
| 10 | Harness Engineering: desarrollo dirigido por especificaciones (SDD) | ✅ |
| 11 | Observabilidad, recursos y ejecución | ✅ v2 |
| 12 | Estructura del repo y del README | ✅ v2 |
| 13 | Hitos de implementación y criterios de aceptación | ✅ v2 |
| 14 | Riesgos y pendientes | ✅ v2 |

## Regla del README
README progresivo: **contexto teórico, conceptual y macro primero**; en cada componente, el detalle técnico al final. Incluye cómo funciona, los pasos para ejecutarlo y las alternativas de ejecución o despliegue (local primero).

---

## 0. Herencia del proyecto multiagente del CV

El repo original llegó a la fase *pre-apply* de su SDD: specs, 18 ADRs, contratos de agentes, proveedores (Gemma vía AI Studio, Hugging Face, mock) y observabilidad con MLflow implementados. P4 **contiene todo** eso como componentes reales y lo lleva más lejos.

### 0.1 Qué se conserva
| Elemento original | ADR original | En P4 | Sección |
|---|---|---|---|
| LangGraph `StateGraph` cíclico | ARCH-002 | Se conserva, con fan-out paralelo (`Send`) y subgrafos | §5 |
| Tres agentes: Research, Fact-Auditing, Synthesis | ARCH-003 | Se conservan, más Planner, Vault Analyst, Web Researcher, Scholar, Vision Auditor, Code Verifier y Critic | §5 |
| Orquestador Leader **determinista** | HARNESS-001 | Regla dura: las aristas condicionales leen el estado, nunca llaman al LLM | §5.2 |
| Fusión de conocimiento **privado** (documentos propios) con **web en vivo** | proposal.md | Privado = **tu vault de Obsidian**; web = SearXNG + Crawl4AI + fuentes académicas | §3, §6 |
| Bucle de auditoría acotado (máx. 3) con bandera de confianza degradada | ITER-014 | Se conserva, con contradicciones tipadas (nota vs web, nota vs nota, diagrama vs texto, numérica) | §5.4 |
| Qdrant (primario) + ChromaDB (dev/tests) tras un protocolo `VectorStore` | ARCH-004 | Se conserva; se suma el índice vectorial de Neo4j | §4 |
| `bge-small-en-v1.5` con sentence-transformers | EMB-010 | En ONNX para CPU; e5 multilingüe para las notas en español (el vault mezcla idiomas) | §4.5 |
| `RecursiveCharacterTextSplitter` 512/64 | CHUNK-012 | Baseline; se compara con chunking por encabezados de Markdown | §3.2 |
| Umbral de similitud 0.70 | SIM-013 | Punto de partida; se calibra con el set de evaluación | §9 |
| Compactación de contexto: ventana 5 + resumen cada 10 turnos | CTX-015 | Por agente, con presupuesto medido | §8 |
| Búsqueda web con backoff (3 reintentos) y modo solo-RAG si falla | TAV-016 | Se conserva el **patrón**; **Tavily se reemplaza** (§6) | §6 |
| Gemma 4 multimodal (visión) y *function calling* | LLM-011 | Vía P0: `smart` y `vision` → Gemma 4 31B (AI Studio) con fallback local | §5.5 |
| Abstracción de proveedores (`LLMProvider`, `EmbeddingProvider`, fábrica, `mock`) | ARCH-005 | Se conserva; el `LLMProvider` por defecto habla con P0 | §5.5 |
| Ejecución de código para verificación numérica | design.md | Sandbox aislado que además **ejecuta los snippets de tus notas** para ver si siguen funcionando | §7.3 |
| Auditoría multimodal (diagramas, capturas) | design.md | Vision Auditor sobre las imágenes del vault | §5.3 |
| MLflow file-based con `metrics.jsonl`, saneamiento (`content_`, `text_`, `doc_`) y hashes SHA-256 | MLFLOW-018 | Se conserva; Langfuse se suma para trazas | §11 |
| *Fail-closed* y "evidencia insuficiente" | requirements.md | Requisitos EARS con test | §10 |
| Harness SDD (`.harness/`, EARS, compuertas humanas, contratos, ADRs JSON, contexto < 20%, diffs < 400 líneas) | HARNESS-001, ARCH-009 | **Completo**, como método de desarrollo | §10 |
| TDD con pytest, cobertura ≥ 80%, tipado | ARCH-008 | Se conserva | §10 |

### 0.2 Qué se mejora
| Límite del original | Mejora en P4 |
|---|---|
| Solo RAG vectorial: falla en preguntas multi-hop y globales | **GraphRAG** sobre el grafo que **ya existe** en tu vault (wikilinks, carpetas, tags) + conceptos extraídos |
| Tavily: resultados pobres en la práctica | Stack propio multi-proveedor con fusión, reranking y fuentes primarias (§6) |
| Corpus genérico de "documentos corporativos" | Tus ~1.000 notas reales, actualizadas en vivo cuando las editas |
| Agentes secuenciales | Fan-out paralelo con `Send` |
| Herramientas acopladas al código | Servidores **MCP** reutilizables (también desde Claude Code u Obsidian) |
| Sin memoria ni reanudación | Checkpointer en Postgres; hallazgos persistidos como notas y en el grafo |
| Sin humano en el bucle | Aprobación antes de escribir en el vault |
| Meta ">85% multi-hop" sin método | Verdad conocida: wikilinks ocultos, preguntas con nota fuente conocida, hechos desactualizados plantados (§9) |

---

## 1. Visión, problema y frase del CV

### 1.1 El problema
Un vault de estudio grande (aquí: **~991 notas en 17 áreas, ~4.700 wikilinks, ~4.900 bloques de código Python**) se vuelve difícil de aprovechar:
- "¿Qué sé de GraphRAG, en qué notas está y cómo se conecta con lo que vi de RAG y de grafos?" → **multi-hop sobre wikilinks**.
- "¿Cuáles son los temas centrales de mi vault y cuáles están flojos?" → **pregunta global**: ningún chunk la responde; hay que agregar sobre comunidades.
- "¿Qué notas están **desactualizadas**?" (p. ej., TorchServe se archivó en 2025; Bytewax dejó de publicar versiones) → **notas vs mundo**.
- "¿Mis notas se contradicen entre sí?" → **nota vs nota**.
- "¿Este snippet de mi nota sigue funcionando con las versiones actuales?" → **ejecución verificada**.
- "Investiga el estado del arte de X en 2026 y conéctalo con lo que ya estudié" → **web + papers + vault**.
- "Dame un plan de estudio para Y, ordenado por prerrequisitos y empezando por lo que me falta" → **grafo + gaps**.

El RAG vectorial encuentra fragmentos parecidos pero no sigue enlaces, no agrega sobre todo el vault y no sabe qué cambió en el mundo. P4 combina **GraphRAG** sobre tu vault con un **equipo de agentes** que consulta la web y fuentes académicas, se audita y **escribe el resultado como notas nuevas de Obsidian**, enlazadas con las que ya tienes.

### 1.2 Qué construimos
1. **Lector del vault** que entiende Obsidian (frontmatter, wikilinks con ruta, alias y encabezado, embeds, tags, bloques de código) y se **actualiza en vivo** cuando editas una nota.
2. **Grafo de conocimiento en Neo4j**: capa estructural determinista (notas, carpetas, wikilinks, tags), capa conceptual extraída (conceptos, tecnologías, papers) y hechos temporales (versiones, deprecaciones).
3. **GraphRAG**: búsqueda local (vecindarios y caminos), global (comunidades Leiden con resúmenes) e híbrida (vector + grafo + BM25).
4. **Sistema multiagente en LangGraph** con Leader determinista y cinco modos: `ask`, `deep-research`, `staleness-audit`, `gap-map` y `study-plan`.
5. **Stack de búsqueda propio** que reemplaza a Tavily: SearXNG, Crawl4AI, arXiv, OpenAlex, PyPI y GitHub, con fusión y reranking.
6. **Escritura segura**: notas nuevas en **una carpeta propia del vault**, nunca se modifican tus notas; las sugerencias de edición se proponen, no se aplican.
7. **Evaluación con verdad conocida**, `judgekit` + Langfuse, y harness SDD completo.

### 1.3 Métricas de éxito
| Tipo | Métrica | Meta |
|---|---|---|
| Calidad | Exactitud en preguntas multi-hop con nota fuente conocida | **> 85%** (la meta del original, ahora medida) |
| Calidad | Mejora frente al RAG solo vectorial (multi-hop y globales) | Se reporta (pp, con IC) |
| Citas | Precisión de citas (la nota o URL citada respalda la afirmación) | ≥ 95% |
| Grafo | Recall@10 de wikilinks ocultos (predicción de enlaces) | Se reporta |
| Desactualización | Precisión y recall sobre hechos desactualizados plantados + casos reales conocidos | Se reporta |
| Contradicciones | P/R de contradicciones nota vs nota plantadas | Se reporta |
| Búsqueda externa | nDCG@5 del stack propio vs solo SearXNG vs Exa (opcional), juzgado | Se reporta |
| Frescura del índice | Tiempo desde que guardas una nota hasta que es recuperable | < 10 s |
| Costo y latencia | Tiempo, llamadas y tokens por investigación | Se reporta |
| Ingeniería | Cobertura de tests / cobertura EARS en `review.md` | ≥ 80% / 100% |

### 1.4 Frase del CV (plantilla)
> **GraphRAG Study Research Agents** · LangGraph · Neo4j (GDS) · Graphiti · Qdrant · MCP · SearXNG · Crawl4AI · Gemma 4 · Langfuse
> Multi-agent research system over a **~1,000-note Obsidian knowledge base**: a live knowledge graph built from wikilinks plus extracted concepts, GraphRAG local/global search, and parallel vault, web, scholarly, vision and code-verification agents with a fact-auditor; writes cited, linked research notes back to the vault. **{a}% multi-hop accuracy (+{d} pp over vector RAG)**, {c}% citation precision, **{s} outdated notes detected** ({p}% precision), {r}% recall on held-out links; replaced a commercial search API with a self-hosted, reranked search stack; built spec-first with EARS and an SDD harness.

### 1.5 Narrativa para entrevista (30 segundos)
"Mi primer sistema multiagente fusionaba documentos privados con búsqueda web, pero solo con RAG vectorial y Tavily, que rendía mal. Lo rehice sobre mi propio vault de Obsidian de mil notas: los wikilinks ya son un grafo, así que construí GraphRAG encima y lo uso para preguntas multi-hop y globales. Los agentes investigan en paralelo en mis notas, la web, papers y PyPI/GitHub; un auditor detecta contradicciones y notas desactualizadas, y el resultado vuelve al vault como notas enlazadas. Lo medí con verdad conocida: oculté enlaces y planté hechos viejos para ver si el sistema los encontraba."

---

## 2. Arquitectura macro y flujo de una investigación

```
  Vault de Obsidian (una carpeta, solo lectura)          Carpeta de salida del vault (lectura/escritura)
  SW-ML-AI Engineering/  ──watchdog──┐                   99 - Research Agent/  ◄──────────────┐
                                     ▼                                                       │
  ┌──────────── ingest: parser Obsidian → chunks → embeddings → grafo (incremental por hash) ──┼───┐
  │ capa estructural (notas, carpetas, wikilinks, tags) · capa conceptual (GLiNER + extract)    │   │
  │ hechos temporales (Graphiti) · comunidades Leiden + resúmenes · enlaces no resueltos       │   │
  └──────────────┬───────────────────────────────────────────────────────┬───────────────────┘   │
          Neo4j  ▼                                          Qdrant/Chroma ▼                         │
  MCP: vault-mcp · graph-mcp     web-mcp (SearXNG, Crawl4AI, PyPI, GitHub)   scholar-mcp (arXiv, OpenAlex)   code-mcp (sandbox)
                 │                                │                                │                    │
  ┌──────────────┴──────────────── LangGraph (Leader determinista) ───────────────┴────────────────────┴──┐
  │ intake → planner → [Send: vault_analyst | web_researcher | scholar | vision_auditor | code_verifier]    │
  │        → fact_auditor ──contradicción/obsolescencia alta y iter < 3──► planner                         │
  │        → synthesis (nota citada o "evidencia insuficiente") → critic (judgekit)                        │
  │        → interrupt: aprobación humana → writer (solo en la carpeta de salida) ─────────────────────────┘
  │ checkpointer Postgres · compactación de contexto · presupuesto por investigación                       │
  └───────────────┬──────────────────────────────────────────────────────────────────┬────────────────────┘
                  ▼ todas las llamadas a LLM                                          ▼ SSE
         llm-gateway (P0): smart · vision · extract · judge                 API FastAPI + UI
```

### 2.1 Decisiones de diseño (ADRs resumidos)
- **ADR-1 · La capa estructural del grafo es determinista.** Notas, carpetas, wikilinks y tags salen del parser, sin LLM. Es exacta, barata, y da verdad conocida para evaluar (los enlaces que tú escribiste).
- **ADR-2 · Orquestación determinista (heredado).** Las transiciones dependen del estado, nunca de una llamada al LLM.
- **ADR-3 · El vault es de solo lectura; P4 escribe solo en su carpeta.** El contenedor monta el vault en modo `ro` y la carpeta de salida en `rw`. Las sugerencias de cambio a tus notas van dentro de la nota de investigación, como lista revisable; nunca se aplican solas.
- **ADR-4 · Herramientas Cypher parametrizadas primero, Text2Cypher después**, validado, solo lectura, con `LIMIT` y timeout.
- **ADR-5 · Herramientas detrás de MCP.** El `vault-mcp` también sirve para que Claude Code u otros clientes consulten tu vault.
- **ADR-6 · El contenido externo es dato, no instrucción.** Delimitado, filtrado por Prompt Guard (P0) y sin capacidad de disparar herramientas.
- **ADR-7 · Búsqueda externa propia y multi-proveedor en vez de Tavily** (§6).
- **ADR-8 · Todo LLM pasa por P0** (caché, breakers, cuotas, guardrails, presupuesto).
- **ADR-9 · Privacidad por consentimiento explícito.** Los fragmentos del vault solo salen hacia el free tier de Google AI Studio si `VAULT_CLOUD_CONSENT=true` (**activado por el usuario el 2026-10-06**: es el valor por defecto del repo); con `false`, P4 usa solo modelos locales. Siempre se excluyen las carpetas y tags privados, y Presidio redacta PII antes de enviar.
- **ADR-10 · Neo4j como base de grafos** (Cypher, GDS, índice vectorial, ecosistema GraphRAG). Alternativas documentadas: Memgraph, FalkorDB.
- **ADR-11 · Aprobación humana antes de escribir** (interrupt de LangGraph) con vista previa de la nota.

### 2.2 Flujo de una investigación
1. `POST /investigations` con la pregunta y el modo. Se crea un `thread_id`; el avance se sigue por SSE.
2. **Intake:** detecta conceptos y notas mencionadas (GLiNER + resolución contra títulos y alias del vault).
3. **Planner:** sub-preguntas y fuentes por sub-pregunta (`vault`, `web`, `scholar`, `vision`, `code`). Salida estructurada validada.
4. **Fan-out en paralelo** (`Send`): cada investigador devuelve `Evidence` con procedencia (nota y encabezado, URL, DOI, versión de PyPI, ejecución del sandbox).
5. **Fact-Auditor:** contradicciones (nota vs nota, nota vs web, diagrama vs texto, numéricas) y **obsolescencia** (la nota afirma X; la fuente primaria actual dice Y). Si hay hallazgos de severidad alta y `iteration < 3`, vuelve al Planner.
6. **Synthesis:** nota de investigación con cada afirmación citada (`[[nota#encabezado]]` o URL), confianza, contradicciones y obsolescencias explícitas, o "evidencia insuficiente".
7. **Critic:** `judgekit` verifica afirmación por afirmación; si falla, la síntesis se rehace una vez.
8. **Interrupt:** vista previa en la UI; al aprobar, el Writer guarda la nota en la carpeta de salida y registra los `Finding` en el grafo.

---

## 3. El vault como fuente

### 3.1 Lectura (parser de Obsidian)
| Elemento | Cómo se interpreta |
|---|---|
| Frontmatter YAML | Propiedades de la nota (tags, aliases, fechas, tipo) |
| `[[Nota]]`, `[[Nota\|alias]]`, `[[Nota#Encabezado]]`, `[[carpeta/sub/Nota]]` | Relación `LINKS_TO` con alias y encabezado; resolución como Obsidian (ruta exacta, si no por nombre de archivo, sin distinguir mayúsculas) |
| `![[imagen.png]]`, `![[Nota]]` | `EMBEDS` (imágenes para el Vision Auditor; transclusiones) |
| `#tag`, `#tag/subtag` | `TAGGED` (se ignoran dentro de bloques de código y encabezados `#`) |
| Encabezados | Secciones (`HAS_SECTION`) y anclas para las citas |
| Bloques de código con lenguaje | Material para el Code Verifier |
| Enlaces no resueltos | Nodos `MissingNote`: **temas que referenciaste y nunca escribiste** (gaps) |

**Una sola carpeta:** `VAULT_PATH` apunta a la carpeta que contiene todo (por defecto `Learning/SW-ML-AI Engineering`), recorrida de forma recursiva. Se excluyen `.obsidian/`, la carpeta de salida de P4 (para no indexar sus propias notas como fuente primaria, salvo que se pida) y lo listado en `VAULT_EXCLUDE` (carpetas o tags privados).

### 3.2 Chunking
Por encabezados de Markdown (respeta la estructura de las notas, que siguen el *Deep Format* del vault), con el título y la ruta de encabezados como prefijo. Baseline heredado: `RecursiveCharacterTextSplitter` 512/64. Ambos se comparan en §9.

### 3.3 Actualización en vivo
`watchdog` vigila la carpeta; cada cambio se re-procesa por **hash de contenido** (solo lo que cambió): se actualizan chunks, embeddings, enlaces y, si cambia la estructura, las comunidades afectadas (recalculo periódico). Renombrar una nota actualiza sus enlaces entrantes. Se mide la frescura (§1.3), igual que en P3.

### 3.4 Escritura (carpeta de salida)
`RESEARCH_OUTPUT_DIR` (por defecto `99 - Research Agent/` dentro del vault). Cada nota generada:
- **Frontmatter:** `type` (ask, deep-research, staleness-audit, gap-map, study-plan), `question`, `created`, `confidence`, `sources`, `model`, `thread_id`.
- **Cuerpo:** resumen; hallazgos con citas `[[nota#encabezado]]` y URLs; *callouts* de Obsidian (`> [!warning] Desactualizado`, `> [!question] Evidencia insuficiente`); contradicciones; gaps (enlaces no resueltos, temas ausentes); **ediciones sugeridas** a notas existentes (como lista, sin aplicarlas); plan de estudio cuando corresponde.
- Al quedar enlazada con wikilinks, aparece en la vista de grafo de Obsidian junto a tus notas.

### 3.5 Medición inicial sobre el vault real (M0, 2026-10-06)
El parser de M0 se corrió sobre `Learning/SW-ML-AI Engineering`:

| Métrica | Valor |
|---|---|
| Notas | 991 |
| Wikilinks (sin embeds) | 4.482 |
| → resueltos a una nota | 2.307 (51%) |
| → resueltos a una **carpeta de curso** (enlace a la carpeta, no a una nota) | 496 (11%) |
| → **sin resolver** | 1.679 (37,5%), 920 destinos distintos |
| Bloques de código | ~9.400 |

Hallazgos que ajustaron el diseño: (1) muchos enlaces son **relativos** (`../Curso/Nota.md`) y otros apuntan a **carpetas**, así que el resolver soporta ambos; (2) algunas rutas superan los 260 caracteres de Windows (lector con prefijo de ruta extendida); (3) los enlaces sin resolver son en su mayoría **atajos o rutas viejas** (`09/29 - CI-CD for ML`, `Docker Profesional`, rutas a cursos movidos). Ese es el primer producto útil de P4 antes de cualquier LLM: un **reporte de enlaces rotos con sugerencias de destino** (por similitud de nombre y numeración), que alimenta el modo `gap-map`.

---

## 4. El grafo de conocimiento y GraphRAG

### 4.1 Esquema
```
(:Note {path, title, mtime, hash, lang})-[:LINKS_TO {alias, heading}]->(:Note | :MissingNote)
(:Note)-[:IN_FOLDER]->(:Folder)-[:IN_FOLDER]->(:Folder)            área → curso → nota
(:Note)-[:TAGGED]->(:Tag)          (:Note)-[:HAS_SECTION]->(:Section)-[:HAS_CHUNK]->(:Chunk)
(:Note)-[:EMBEDS]->(:Attachment)   (:Chunk)-[:MENTIONS]->(:Concept)
(:Concept)-[:PREREQUISITE_OF | RELATED_TO | ALTERNATIVE_TO]->(:Concept)        extraídos
(:Concept)-[:HAS_FACT {valid_at, invalid_at}]->(:Fact)                         Graphiti (versiones, deprecaciones)
(:Community {level, summary})<-[:IN_COMMUNITY]-(:Note)
(:Finding {claim, kind, confidence})-[:SUPPORTED_BY]->(:Chunk | :Source)       (:Source {url, kind})
```

### 4.2 Construcción
- **Estructural:** determinista desde el parser (ADR-1).
- **Conceptual:** GLiNER (CPU) para conceptos y tecnologías + alias `extract` de P0 para relaciones (`PREREQUISITE_OF`, `ALTERNATIVE_TO`); resolución de entidades (normalización, *fuzzy matching*, confirmación con el LLM en la zona gris) contra los títulos y alias del vault.
- **Temporal:** Graphiti registra hechos con validez (`TorchServe → archivado desde 2025-08`) a partir de PyPI, GitHub y la web; la obsolescencia se detecta comparando lo que dice la nota con los hechos vigentes.
- **Comunidades:** GDS Leiden sobre el grafo de notas (wikilinks + conceptos compartidos); un resumen por comunidad. Se comparan con tus carpetas: cuándo coinciden y cuándo el grafo revela temas transversales.

### 4.3 Modos de recuperación
| Modo | Cómo | Para qué |
|---|---|---|
| **Local** | Semillas (vector o entidad enlazada) → expansión de k saltos por `LINKS_TO` y `MENTIONS` | "¿Cómo se conecta X con Y en mis notas?" |
| **Global** | Map-reduce sobre resúmenes de comunidades | "¿Cuáles son mis temas centrales y débiles?" |
| **Híbrida** | Vector (Qdrant) + grafo + BM25, fusión RRF | Preguntas mixtas |
| **Cypher parametrizado** | Backlinks, caminos más cortos entre notas, notas huérfanas, enlaces no resueltos, notas centrales (PageRank), prerrequisitos | Herramientas frecuentes del dominio |
| **Text2Cypher** | Validado, solo lectura, `LIMIT`, timeout | Preguntas abiertas sobre la estructura |

### 4.4 Baselines externos
**Microsoft GraphRAG** y **LightRAG** indexan un área del vault (p. ej., `06 - Large Language Models`) para comparar calidad y costo de construcción contra el pipeline propio, que aprovecha los wikilinks en vez de extraerlo todo con un LLM.

### 4.5 Embeddings y vector stores
El vault mezcla inglés (cursos nuevos) y español (cursos anteriores): e5 multilingüe en ONNX por defecto y `bge-small-en-v1.5` (heredado) como comparación. Qdrant (primario) y ChromaDB (tests y modo sin Docker) tras el protocolo `VectorStore` heredado.

---

## 5. El sistema multiagente y los modos de investigación

### 5.1 Modos
| Modo | Qué produce | Agentes principales |
|---|---|---|
| `ask` | Respuesta citada a una pregunta concreta | Vault Analyst (+ web si hace falta) |
| `deep-research` | Nota de investigación sobre un tema: estado del arte, conexión con tus notas, gaps | Todos |
| `staleness-audit` | Reporte de notas desactualizadas de una carpeta o curso, con evidencia y ediciones sugeridas | Vault Analyst, Web Researcher (PyPI/GitHub/docs), Code Verifier |
| `gap-map` | Mapa global: comunidades, temas débiles, notas huérfanas, enlaces no resueltos | Vault Analyst (búsqueda global) |
| `study-plan` | Ruta de estudio ordenada por prerrequisitos, marcando lo ya cubierto | Vault Analyst, Scholar |

### 5.2 Roles
| Agente | Responsabilidad | Herramientas |
|---|---|---|
| **Leader** (sin LLM) | Ejecuta el grafo; límites de iteración, presupuesto y compuertas | — |
| **Planner** | Sub-preguntas y fuentes | Esquema del grafo, catálogo de herramientas |
| **Vault Analyst** | Búsqueda local, global, híbrida y Cypher sobre tu vault | `vault-mcp`, `graph-mcp` |
| **Web Researcher** | Búsqueda y extracción web; versiones y estado de proyectos | `web-mcp` |
| **Scholar** | Papers y citas | `scholar-mcp` |
| **Vision Auditor** | Interpreta diagramas e imágenes del vault y los contrasta con el texto | alias `vision` de P0 |
| **Code Verifier** | Verificación numérica y ejecución de snippets de tus notas | `code-mcp` |
| **Fact-Auditor** | Contradicciones, obsolescencia y afirmaciones sin respaldo | — |
| **Synthesis** | Nota de investigación citada o "evidencia insuficiente" | — |
| **Critic** | Verificación afirmación por afirmación | `judgekit` |
| **Writer** (sin LLM) | Escribe la nota aprobada en la carpeta de salida | Sistema de archivos (solo esa carpeta) |

### 5.3 Vision Auditor
El vault tiene pocas imágenes hoy (~22), así que su papel es acotado: describir diagramas para que sean recuperables (RAG multimodal) y detectar diagramas que contradicen el texto. Se evalúa con un set pequeño, incluidos casos plantados.

### 5.4 Bucle de auditoría
Hallazgos tipados (`note_vs_web`, `note_vs_note`, `visual_vs_text`, `numeric`, `outdated`) con severidad. Con severidad alta y `iteration < 3`, el Planner recibe preguntas dirigidas. Al agotar iteraciones, la nota reporta el conflicto con ambas fuentes y confianza degradada (heredado).

### 5.5 Modelos (todos vía P0)
| Uso | Alias | Principal | Respaldo |
|---|---|---|---|
| Planner, investigadores, síntesis | `smart` | Gemma 4 31B (AI Studio; consentimiento activado) | Groq Llama 3.3 70B → Ollama Qwen3 1.7B |
| Visión | `vision` | Gemma 4 31B (multimodal) | `mock` |
| Extracción para el grafo | `extract` | Gemma 4 26B A4B | Groq → Ollama |
| Crítica y evaluación | `judge` / `judge_golden` | Gemma 3 4B local / Gemma 4 31B | `mock` |

Con `VAULT_CLOUD_CONSENT=false`, todas las llamadas que llevan texto del vault usan solo Ollama (calidad menor, documentada como trade-off).

---

## 6. Búsqueda externa: por qué no Tavily y el stack que lo reemplaza

### 6.1 Decisión
Tavily se **descarta**: en tus pruebas los resultados fueron pobres, depende de un proveedor externo con créditos, y además cambió de dueño en 2026. Se reemplaza por un stack **propio, multi-proveedor y self-hosted**, donde cada pieza es la mejor en su tarea y todo queda detrás de un solo servidor `web-mcp`:

| Pieza | Rol | Por qué | Costo |
|---|---|---|---|
| **SearXNG** (self-hosted, Docker) | Metabuscador: consulta varios motores a la vez (DuckDuckGo, Brave, Bing, Mojeek, Wikipedia, GitHub, Stack Overflow, arXiv) y devuelve JSON | Sin cuotas, sin API key, privado; si un motor falla o bloquea, los demás siguen | $0 |
| **Crawl4AI** (open source, Apache 2.0) | Descarga y convierte páginas a Markdown limpio para LLMs, incluido contenido renderizado con JavaScript | Mucho mejor extracción que los snippets de una API de búsqueda; corre local | $0 |
| `trafilatura` | Extractor liviano sin navegador para páginas simples | Más rápido y con menos RAM que levantar Chromium | $0 |
| **arXiv API** | Papers por tema | Fuente primaria académica | $0 |
| **OpenAlex** | Metadatos académicos, citas, autores; búsqueda por DOI | Índice abierto de cientos de millones de trabajos (requiere API key gratuita con cuota diaria desde 2026) | $0 dentro de la cuota |
| **PyPI JSON API** y **GitHub API** | Última versión, fecha de release, si el repo está archivado | **La señal más fiable para detectar notas desactualizadas** | $0 |
| **Exa** (opcional) | Búsqueda neuronal como proveedor extra | Solo si se quiere comparar; apagado por defecto | Free tier / pago |

### 6.2 Cómo se vuelve robusto
1. **Fan-out y fusión:** la consulta va a SearXNG (varios motores), a arXiv/OpenAlex si es académica y a PyPI/GitHub si menciona una tecnología; los resultados se fusionan con RRF.
2. **Deduplicación** por URL canónica y por similitud de contenido.
3. **Calidad de fuente:** prioridad a documentación oficial, repos, papers y registros de paquetes; lista de exclusión para granjas de contenido.
4. **Reranking local** con un cross-encoder pequeño (ONNX, CPU) sobre el contenido extraído, no solo sobre el snippet.
5. **Resiliencia:** reintentos con backoff (patrón heredado de ADR-TAV-016), timeout por proveedor, breaker simple por motor, caché en Redis (TTL) y **modo solo-vault** si todo falla.
6. **Seguridad:** el contenido descargado es dato no confiable (ADR-6) y pasa por Prompt Guard en P0.
7. **Medición:** benchmark de proveedores (§9) con relevancia juzgada, para mostrar con datos que el stack propio supera a usar un solo buscador.

---

## 7. Herramientas vía MCP, sandbox, seguridad y privacidad

### 7.1 Servidores MCP
| Servidor | Herramientas |
|---|---|
| `vault-mcp` | `search_notes(q, mode)`, `get_note(path, heading)`, `backlinks(path)`, `unresolved_links(folder)`, `orphans(folder)`, `notes_by_tag(tag)` |
| `graph-mcp` | `shortest_path(a, b)`, `community_of(note)`, `community_summaries(top_k)`, `local_search(q)`, `global_search(q)`, `prerequisites(concept)`, `text2cypher(q)` |
| `web-mcp` | `web_search(q)`, `fetch(url)`, `package_info(name)`, `repo_status(owner/repo)` |
| `scholar-mcp` | `search_papers(q)`, `paper(doi_or_arxiv_id)` |
| `code-mcp` | `run_python(code, timeout)`, `run_note_snippet(path, block_index)` |

### 7.2 Seguridad
Vault montado en solo lectura (ADR-3), Writer limitado a la carpeta de salida (validación de rutas contra *path traversal*), contenido externo delimitado, Cypher validado y con rol de solo lectura.

### 7.3 Sandbox de código
Contenedor sin red, usuario sin privilegios, sistema de archivos de solo lectura salvo `/tmp`, límites de CPU, memoria y tiempo; imagen con las librerías más usadas en tus notas (versiones fijadas y declaradas en el reporte). Un snippet que falla por API cambiada es **evidencia de obsolescencia**; uno que falla por depender de un servicio externo se marca como "no verificable".

### 7.4 Privacidad
ADR-9: consentimiento explícito para enviar fragmentos del vault a un free tier, exclusiones por carpeta o tag, redacción con Presidio y logs sin contenido (saneamiento heredado de MLflow).

---

## 8. Memoria, contexto y ejecución durable
- **Ejecución durable:** checkpointer de LangGraph en Postgres; una investigación interrumpida o esperando aprobación se reanuda con su `thread_id`; *time travel* para depurar.
- **Contexto:** ventana deslizante de 5 turnos + resumen cada 10 (heredado), presupuesto de contexto por agente y medición del llenado (meta < 20%).
- **Memoria de largo plazo:** las notas aprobadas quedan en el vault y como `Finding` en el grafo; investigaciones futuras las citan con su fecha.

---

## 9. Harness de evaluación con verdad conocida
La evaluación corre sobre una **copia congelada** del vault (snapshot), nunca sobre el vault en vivo.

| Set | Cómo se construye | Qué mide |
|---|---|---|
| **Enlaces ocultos** | Se quita el 10% de los wikilinks de la copia | Recall@10 de recuperar la nota enlazada (predicción de enlaces) |
| **Preguntas con fuente conocida** (~300) | Generadas desde notas y pares de notas enlazadas (1, 2 y 3 saltos), por área e idioma; revisión manual de una muestra | Exactitud y precisión de citas, por tipo |
| **Globales** | Preguntas sobre temas, áreas y cobertura | Calidad juzgada contra un resumen de referencia escrito a mano |
| **Obsolescencia** | Hechos viejos **plantados** en la copia (versiones, fechas, proyectos archivados) + casos reales conocidos (TorchServe, Bytewax) | P/R de detección |
| **Contradicciones** | Afirmaciones opuestas plantadas en pares de notas | P/R `note_vs_note` |
| **Sin respuesta** | Temas ausentes del vault y no verificables | F1 de abstención |
| **Búsqueda externa** | Consultas técnicas con relevancia juzgada | nDCG@5: SearXNG solo vs stack completo vs Exa (opcional) |
| **Snippets** | Muestra de bloques de código del vault | % ejecutables, % rotos por cambios de API |

**Configuraciones comparadas:** (B0) RAG vectorial de un agente (el original del CV), (B1) multiagente vectorial, (B2) GraphRAG local, (B3) global, (B4) híbrido, (B5) B4 + web, académico, visión y código; más Microsoft GraphRAG y LightRAG en un área.
**Herramientas:** `judgekit` (P2) con panel de jueces, Langfuse (datasets, experiments, scores), MLflow saneado. Compuertas en la CI con `mock`: parser (wikilinks, tags, frontmatter), herramientas Cypher, contratos MCP, forma de la nota (citas, frontmatter válido) y que el Writer nunca escriba fuera de su carpeta.

---

## 10. Harness Engineering: desarrollo dirigido por especificaciones (SDD)
Heredado completo y aplicado al desarrollo de P4 con Claude Code como implementador:
```
init → proposal → spec (EARS) → [COMPUERTA HUMANA] → design → [COMPUERTA HUMANA] → tasks → apply → verify → archive
```
`.harness/tasks.json` (máquina de estados), `agents/` (leader, spec-author, implementer, reviewer), `skills/sdd-workflow/`, `memory/decisions.json` (ADRs) y `supervision-guide.md`, `specs/<feature>/` (`proposal`, `requirements` EARS, `design`, `tasks` con diffs < 400 líneas, `review` con cada requisito → test), contratos de resultado por fase y telemetría del harness (cobertura EARS y de tests, tamaño de diff, llenado de contexto).

---

## 11. Observabilidad, recursos y ejecución
**Observabilidad:** Langfuse (una traza por investigación, spans por nodo y herramienta, scores de `judgekit`), MLflow (evaluaciones, saneado), Prometheus (investigaciones activas, duración por nodo, iteraciones, llamadas por herramienta, errores MCP, frescura del índice), trazas OTel propagadas a P0.

| Servicio | RAM aprox. | Perfil |
|---|---|---|
| Neo4j (heap 512 MB + page cache 512 MB) | ~1.3 GB | `core` |
| Qdrant | ~300 MB | `core` |
| Postgres (checkpointer) | ~200 MB | `core` |
| Redis + `llm-gateway` | ~700 MB | `core` |
| SearXNG | ~150 MB | `core` |
| Agentes + ingest + MCP + API | ~800 MB | `core` |
| Crawl4AI (Chromium, bajo demanda) + sandbox | ~700 MB | `core` |
| **Total** | **≈ 4.1 GB** 🟡 | |
| `⏳ 16GB` | Langfuse self-hosted, Microsoft GraphRAG sobre todo el vault, recalculo de comunidades en vivo | `full` |

Ejecución: `make doctor` → `make up` → `make index` (primera indexación del vault) → `make ask Q="..."` o la UI en `localhost:8090` → la nota aparece en `99 - Research Agent/` y la ves en Obsidian.

---

## 12. Estructura del repo y del README
```
graphrag-research-agents/
├── README.md · PLAN.md · AGENTS.md · LICENSE · Makefile · docker-compose.yml · pyproject.toml (workspace uv)
├── .harness/ (tasks.json, agents/, skills/, memory/, specs/)
├── packages/
│   ├── researchcore/          # núcleo hexagonal (ADR-012): vault/, graph/, research/ + ports.py, sin I/O
│   └── researchadapters/      # adaptadores de los puertos: fs_vault, neo4j_graph (luego Qdrant, búsqueda, LLM)
├── services/                   # adaptadores de entrada y raíces de composición
│   ├── ingest/                 # watcher, chunking, embeddings, grafo, conceptos, comunidades
│   ├── agents/                 # grafo de LangGraph, roles, modos, Writer
│   ├── mcp/ (vault, graph, web, scholar, code)
│   └── api/                    # FastAPI + SSE + UI
├── sandbox/ · infra/ (neo4j/, searxng/) · eval/ (snapshot/, sets/, gates.yaml)
├── tests/ (unit/, contract/, integration/) — cada requisito EARS con su test
└── docs/ (adr/, results/, images/)
```
**Esqueleto del README (en inglés):** Part I (problem; concepts: knowledge graphs, a vault as a graph, GraphRAG local/global, multi-agent roles, auditing, MCP, durable execution, SDD), Part II (components), Part III (the graph), Part IV (the agents and modes), Part V (proof: known-ground-truth evaluation, search-stack benchmark, baselines), Part VI (run it on your own vault), Part VII (reflection: what changed from the original system, why not Tavily, limitations).

---

## 13. Hitos de implementación y criterios de aceptación
**Definición de terminado:** CI en verde · cabe en 8 GB · README del hito · $0 · artefactos SDD (spec EARS + review) · tag.

| Hito | Objetivo | Criterios de aceptación | Tamaño |
|---|---|---|---|
| **M0 · Bootstrap** ✅ | Repo, harness, contratos, Leader, esquema, **parser de Obsidian**, Compose (Neo4j, Qdrant, SearXNG…), CI | `make doctor` pasa; CI en verde; el parser maneja wikilinks con ruta, alias, encabezado, embeds y tags | S |
| **M1 · Indexación del vault** | Parser completo, chunking, embeddings, capa estructural en Neo4j, watcher incremental, snapshot de evaluación + sets v0 | Vault completo indexado; frescura medida; enlaces no resueltos y huérfanas listados | M |
| **M2 · Baseline B0** | RAG vectorial de un agente (el original) vía P0 + harness de evaluación | Tabla B0; `judgekit` integrado | M |
| **M3 · GraphRAG** | Herramientas Cypher, Leiden + resúmenes, búsquedas local y global, `gap-map` | B2 y B3 medidos; recall de enlaces ocultos | L |
| **M4 · Capa conceptual y temporal** | GLiNER + `extract`, resolución de entidades, Graphiti, híbrida RRF | B4 medido; precisión de extracción en muestra etiquetada | L |
| **M5 · Multiagente + escritura** | Planner, fan-out, Fact-Auditor, Synthesis, Critic, Leader, checkpointer, Writer con aprobación | Una investigación `deep-research` termina en una nota aprobada en la carpeta de salida; contradicciones plantadas detectadas | L |
| **M6 · Stack de búsqueda + académico** | SearXNG + Crawl4AI + PyPI/GitHub + arXiv/OpenAlex, fusión, rerank, caché; `staleness-audit` | Benchmark de búsqueda; P/R de obsolescencia (plantada + TorchServe/Bytewax) | M |
| **M7 · Visión, código, MCP, API y UI** | Vision Auditor, sandbox con snippets, servidores MCP, SSE y UI con vista previa | MCP pasan contratos; % de snippets ejecutables reportado | M |
| **M8 · Evaluación completa** | B0–B5 + Microsoft GraphRAG y LightRAG; Langfuse experiments; compuertas en la CI | Tabla final; frase del CV con números | M |
| **M9 · Pulido y publicación** | README completo, `review.md` 100% EARS, `v1.0`, guía "úsalo con tu propio vault" | Una persona ajena lo corre con su vault | M |
| M10 · `⏳ 16GB` | Langfuse self-hosted, Microsoft GraphRAG sobre todo el vault | Resultados `v1.1` | M |

**MVP para el CV:** M0 → M5 + M6 parcial (obsolescencia con PyPI/GitHub) + M8 parcial (B0 vs B4/B5).
**Orden de recorte:** baselines externos → Graphiti → visión → Text2Cypher (se conservan grafo, multiagente, auditoría, escritura y búsqueda propia).

---

## 14. Riesgos y pendientes
| ID | Riesgo | Mitigación |
|---|---|---|
| R1 | Motores de SearXNG que bloquean o limitan (CAPTCHA, rate limits) | Varios motores a la vez, intervalos entre consultas, caché, fuentes primarias (PyPI, GitHub, arXiv) que no dependen de buscadores; Exa como proveedor opcional |
| R2 | Crawl4AI con Chromium consume RAM | Bajo demanda y con límite de concurrencia; `trafilatura` primero para páginas simples |
| R3 | Privacidad: fragmentos del vault hacia un free tier | ADR-9 (consentimiento, exclusiones, Presidio); modo solo-local disponible |
| R4 | Escritura accidental sobre tus notas | Montaje `ro`, validación de rutas del Writer, test de compuerta en la CI, aprobación humana |
| R5 | Cuotas de Gemma 4 (AI Studio) y OpenAlex | P0 respeta las cuotas y cae a Groq/Ollama; evaluación por lotes |
| R6 | Extracción conceptual ruidosa con modelos chicos | La capa estructural no depende del LLM (ADR-1); muestra etiquetada |
| R7 | Text2Cypher incorrecto o peligroso | Herramientas parametrizadas primero; validación y rol de solo lectura |
| R8 | Prompt injection vía páginas web | ADR-6, Prompt Guard en P0, herramientas restringidas por rol |
| R9 | Notas que cambian mientras corre una evaluación | La evaluación usa un snapshot congelado |
| R10 | Scope creep | MVP y orden de recorte |

**Verificar al implementar:** versión y licencia de Neo4j Community y del plugin GDS en Docker; API vigente de `neo4j-graphrag`, Graphiti y LightRAG; configuración de SearXNG para salida JSON y motores habilitados; versión de Crawl4AI y su imagen de Docker; condiciones vigentes de OpenAlex (API key y cuota diaria) y de Exa; adaptadores MCP de LangChain; cuotas de Gemma 4 en AI Studio (texto y visión).
