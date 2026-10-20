# AI and System Design

Two [Claude Code](https://claude.com/claude-code) skills:

- **system-design**: designing and reviewing scalable backend systems (databases, caching, queues, load balancing, CAP, estimation).
- **ai-engineering**: designing and reviewing production LLM systems and agents (tool calling, agent loops, RAG, MCP, evals, guardrails, cost and latency).

Each skill is a small wiki. `SKILL.md` is a routing table, and Claude reads only the reference pages a question needs, so context stays small.

## Install

Personal (every project):

```bash
git clone https://github.com/TomDamri1/AI-and-System-Design.git
cp -R AI-and-System-Design/system-design AI-and-System-Design/ai-engineering ~/.claude/skills/
```

Or per project: copy the folders into `<repo>/.claude/skills/`.

Then start a new Claude Code session. Use `/system-design` or `/ai-engineering`, or just ask a design question.

## Sources

Every reference page ends with its sources. The system-design pages are adapted from [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (CC BY 4.0). The ai-engineering pages are distilled from vendor documentation and engineering posts (Anthropic, OpenAI, modelcontextprotocol.io and others), cited per page.

## License

MIT for this repo's own text. Adapted material keeps its original license.
