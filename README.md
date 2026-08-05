# HROS

HERMES Research Operating System.

GitHub repository: [o-yutaka/HORS](https://github.com/o-yutaka/HORS)

## Repository Structure

```
HROS/
├── bible/          # Architecture constitution and foundational documents
├── adr/            # Architecture Decision Records
├── rfc/            # Request for Comments
├── prompts/        # Prompt templates and libraries
├── core/           # Core system components
├── kernel/         # Kernel layer
├── capability/     # Capability definitions and implementations
│   ├── competition-intelligence/ # Official evidence collection and synthesis
│   └── competition_operator/     # URL → hypothesis → arena → frozen submission
├── service/        # Service layer
├── infrastructure/ # Infrastructure components
├── workspace/      # Workspace management
├── experiments/    # Experimental work
└── logs/           # Logs and audit trails
```

## Competition execution boundary

BLACK controls decisions and replanning. HROS provides reusable research and competition capabilities. Kaggle Official Notebook is the heavy execution and submission environment. GitHub is the source of truth; Cloudflare may be used only for lightweight run metadata, APIs, and report delivery.
