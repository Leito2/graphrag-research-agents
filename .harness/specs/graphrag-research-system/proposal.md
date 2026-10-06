# Proposal: GraphRAG Multi-Agent Research System

## Problem
Financial-crime questions are relational (shared devices, cards, IPs), global (which rings are active) and
multi-source (graph, policies, web, receipts). Vector RAG and single agents fail on multi-hop and global questions
and self-confirm. See PLAN.md §1.

## Scope
Knowledge graph (transactional from P1 + documents + temporal facts), GraphRAG (local, global, hybrid, Cypher),
multi-agent LangGraph system with a deterministic Leader and fact-auditing loop, MCP tools, sandboxed code,
vision audit, durable execution, human approval, evaluation against known ground truth.

## Out of scope
Production deployment, real customer data, model fine-tuning, real-time blocking actions.

## Risks
Free-tier quotas, noisy extraction with small models, prompt injection through web content, 8 GB RAM (PLAN §14).
