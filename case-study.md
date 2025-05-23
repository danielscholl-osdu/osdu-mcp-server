# Case Study: Building Quality Code with AI Agents

*Author: Daniel Scholl • Date: 23 May 2025*

---

## Introduction

The objective of this case study is to demonstrate how structured software engineering practices and systematic AI-driven workflows can significantly improve code quality, consistency, and productivity. By illustrating real-world implementations, documented through comprehensive agent logs and project artifacts, we explore how AI agents move beyond simple automation and become disciplined orchestrators within a robust engineering framework.

This case study covers critical practices, detailing concrete examples and patterns observed in an active development environment. Each section provides insights into the strategic choices made, their practical implementation, and their impact on project outcomes.

---

## 1. Agent Design: Workflow Engineering, Not Just Prompting

**Pattern:** AI agent effectiveness is maximized when driven by clearly defined, structured workflows rather than relying solely on dynamic prompts. Each development cycle consistently follows a deterministic, traceable lifecycle:

```
Issue → Branch → Context → Code → Test → Docs → Merge Request (MR) → Session Log
```

Our project meticulously outlines and enforces this lifecycle through detailed CONTRIBUTING guidelines, automated tooling, and explicit naming conventions. This rigor transforms the agent from a passive script executor into a disciplined orchestrator, actively managing the entire software development lifecycle.

### Strategic Implementation

* **Structured and Repeatable Actions:** Every agent task is explicitly scripted within Agent Developer Workflows (ADW). These workflows standardize essential practices—branch naming, commit message formatting, merge request creation—ensuring repeatability and reducing human error.

* **Explicit Cognitive Loop:** Agents consistently execute a clear cognitive cycle:

  * **Reason:** Load and interpret architectural decision records (ADRs), specifications, and relevant historical context.
  * **Act:** Generate code, conduct tests, update documentation.
  * **Reflect:** Assess outcomes and explicitly log findings.
  * **Retry:** Systematically attempt solutions to failures or test issues.
  * **Escalate:** Clearly surface persistent issues for human intervention or merge request reviews.

* **Observable Artifacts:** Each step in the workflow produces tangible, documented artifacts—issues, branches, session logs, ADRs, and merge requests—creating a robust audit trail. These artifacts facilitate seamless collaboration, provide transparency, and maintain historical continuity.

### Lessons Learned and Insights

* **Foundation Implementation:** Clearly defined workflows provided transparency and accelerated the delivery of foundational features. Issue #4, executed through branch `agent/4-foundation-implementation`, showcased how structured engineering practices reduce iteration times and improve quality.

* **Entitlements Phase:** Systematic adherence to structured workflows in branch `agent/19-minimal-entitlements` highlighted the importance of consistent process enforcement, ensuring successful outcomes and predictable timelines.

### Impact and Benefits

Embedding structured workflows deeply into agent-driven processes consistently yields:

* **Enhanced Consistency:** Standardized practices significantly reduce variability and errors, enhancing overall quality and predictability.
* **Scalable Extensibility:** Structured workflows facilitate the seamless integration of additional tools and features, ensuring maintainability as complexity grows.
* **Optimized Collaboration:** Transparent, documented workflows foster improved accountability and efficient collaboration between AI agents and human developers.

---

## 2. Memory *is* Architecture

**Pattern:** Long-term memory lives in *files the agent can load*, not in oversized prompts. Session logs capture transient context for future runs, while ADRs encode durable decisions.

In agent-driven development, memory is not just a convenience—it is a core architectural pillar. Our approach treats memory as a set of persistent, structured artifacts that the agent can reliably load, reason over, and update. This avoids oversized prompts and ephemeral chat history while enabling intentional, durable decision-making.

### Strategic Implementation

* **Session Logs as Short-Term Memory:** Every agent session produces a log that captures what was done, why, and what was learned. These logs serve as a running history, allowing the agent to pick up where it left off, avoid repeating mistakes, and maintain continuity. For example, the evolution from single write protection to the dual permission model (`OSDU_MCP_ENABLE_WRITE_MODE` and `OSDU_MCP_ENABLE_DELETE_MODE`) is documented in session logs, ensuring future sessions inherit these safety patterns automatically.

* **ADRs as Long-Term, Durable Memory:** Architectural Decision Records (ADRs) encode project design choices like authentication, naming, or error handling. Kept concise and scoped, they’re optimized for selective loading—enabling the agent to stay within context limits without losing architectural grounding.

* **Modular Context Loading:** Agents dynamically load only the most relevant context—typically a combination of recent session logs, scoped ADRs, and any relevant specifications or checklists. This focused strategy minimizes hallucination and context bloat.

* **File-Based Recovery:** In case of failure (e.g., crash, timeout, or hallucination), the agent restores continuity by reloading the last known memory state from disk—not volatile memory.

* **Automation and Continuity:** Session logs are linked directly to issues and MRs, creating a traceable narrative thread that the agent can follow between sessions without needing re-prompting.

### Lessons Learned and Insights

* **Too Much Context is a Liability:** Early experiments with verbose prompts led to drift and confusion. File-based scoping improved clarity and outcome reliability.

* **Memory Enables Autonomy:** Once key decisions were externalized into ADRs and logs, agents could independently execute long-running features across multiple sessions without constant intervention.

* **Debuggability Matters:** Durable memory artifacts allowed us to reconstruct any decision chain or failure path quickly by asking: “What did the agent know at this point?”

* **Design Before Docs:** Emphasizing ADRs early meant foundational decisions were made up front—making downstream development clearer and more intentional.

### Impact and Benefits

Treating memory as a first-class architectural component yielded:

* **Improved Accuracy:** Scoped context reduced hallucinations and improved reasoning.
* **Faster Iterations:** Agents resumed tasks without rework or manual re-priming.
* **Sustainable Scale:** Context growth became manageable as memory expanded linearly.
* **Auditable Decision History:** Structured memory improved transparency, trust, and code reviews.

## 3. Planning Isn’t Optional

**Pattern:** Each phase starts with a specification or checklist, the agent writes failing tests, then iterates until green. Reflection is logged as “Lessons Learned / Next Steps.”

In an agent-driven development environment, the bottleneck has shifted. The marginal cost of generating and rewriting code is near zero—what matters most is the clarity and completeness of the planning process. The agent’s effectiveness is directly tied to the precision of the instructions it receives. As a result, planning becomes the core engineering task.

### Strategic Implementation

* **Specification-First Workflow:** Every task begins with a clear specification or checklist that outlines the goal, constraints, and success criteria. This gives the agent a bounded problem space and ensures that outputs are tied to a known target.

* **Test-Driven Execution:** Before any implementation begins, the agent is directed to write failing tests derived from the specification. Following our behavior-driven testing philosophy (ADR-010), tests focus on observable outcomes rather than implementation details. This practice ensures that development is grounded in verifiable behavior, not just code generation.

* **Plan-Execute-Reflect Cycle:** Each session ends with a structured reflection log that captures lessons learned, what succeeded, and what adjustments are needed. These entries guide the planning phase of the next cycle, reinforcing a closed feedback loop.

* **Checklist Discipline:** Repeatable planning artifacts (e.g., onboarding checklists, feature definitions) are templated and version-controlled. These planning primitives make it easier to spin up new tasks with consistent quality and scope.

### Lessons Learned and Insights

* **Garbage In, Garbage Out:** Weak or ambiguous plans consistently led to poor agent performance. Strengthening specifications had an immediate impact on output quality and reduced iteration count.

* **Specification as Leverage:** Well-formed specs allowed the agent to operate independently, even across complex features. One example was the `feature/async-deletion`, which proceeded through multiple stages with minimal human adjustment due to a tightly-scoped initial spec.

* **Planning is the Human’s Superpower:** The engineer’s role is evolving toward architectural vision, problem decomposition, and constraint definition. The agent can execute—but only when the roadmap is clear.

* **Feedback Improves Planning:** Logging “Lessons Learned / Next Steps” created a body of institutional knowledge. Over time, this archive improved the quality and clarity of future planning artifacts.

### Impact and Benefits

Elevating planning to a first-class engineering activity delivered measurable results:

* **Higher Code Quality:** Better plans led to better test coverage and fewer regressions.
* **Accelerated Delivery:** Strong upfront planning reduced time spent on rework and debugging.
* **Reduced Human Supervision:** Precise specs enabled autonomous execution across phases.
* **Cumulative Learning:** Planning artifacts and reflections compounded into a reusable strategy library.

## 4. Real-World Agents Need Real-World Tools

**Pattern:** The agent shells out to **Git**, **gh**, and even **curl** during health-check debugging; common workflows are captured in documentation and ADRs for reuse.

The agent’s true potential is unlocked when paired with the right tools. Bash and Unix shell utilities aren’t just developer conveniences—they are essential instruments that let agents execute powerful, scalable operations with precision. By leaning on real-world tooling, the agent transcends pure code generation to become an orchestrator of repeatable, traceable engineering work.

### Strategic Implementation

* **Delegation to Shell Utilities:** Instead of recreating standard tooling behavior in Python, the agent uses shell commands—`grep`, `sed`, `curl`, `git`, `gh`, and others—to manipulate files, automate version control, and query remote services. This delegation enhances speed and reliability.

* **Workflow Documentation:** Reusable patterns and workflows are captured in CONTRIBUTING.md and CLAUDE.md. This allows the agent to invoke complex operations by following documented patterns, supporting safe, tested reuse across multiple workflows.

* **Composable Refactoring Workflows:** The agent chains multiple commands together to execute sophisticated operations—such as file renaming, dependency rewiring, and doc regeneration—while maintaining git integrity and traceability.

* **Observability and Rollback:** All shell-based operations are wrapped with git status checks and commit hooks. This ensures changes are observable, reversible, and verifiable through automated tests.

### Lessons Learned and Insights

* **Don’t Rebuild What Exists:** Leveraging mature shell tools drastically reduced complexity and bug surface area. Simple tasks stayed simple.

* **Shell Enables Speed at Scale:** A tool renaming refactor involving 14 tools across 3 services was completed in minutes via shell scripts—what would have taken hours by hand.

* **Command Templates Compound Value:** As the number of templated commands grew, the agent’s velocity improved. Refactor tasks became simpler to define and reuse.

* **Human-Level Tool Access:** Letting agents operate with tools like `git` and `gh` meant they could perform high-context developer tasks—like opening MRs, inspecting history, or rebasing—without human intervention.

### Impact and Benefits

Empowering agents with real-world tooling resulted in:

* **Accelerated Refactors:** Multi-file, cross-service changes executed safely and quickly.
* **Improved Traceability:** Shell outputs were logged, versioned, and easily auditable.
* **Higher Automation Ceiling:** Tasks like health-check debugging or release prep became agent-driven.
* **Reusable Automation:** Templated command libraries became a core resource for scalable development.

## 5. ReAct & CoT Are System Patterns, Not Magic Tricks

**Pattern:** The runtime enforces *Reason → Act → Reflect* by pairing failing tests with auto-retry loops, then appending a reflective section to each session log.

In the OSDU MCP Server project, ReAct (Reason → Act → Reflect) and Chain-of-Thought (CoT) are not clever tricks confined to prompt design—they are foundational system patterns embedded in the engineering workflow. These patterns structure every agent interaction into a disciplined cycle of reasoning, execution, and reflection.

### Strategic Implementation

* **Enforced Cognitive Loops:** Every agent session begins by loading specs, ADRs, and logs to reason about the task. It then acts—writing or editing code, executing tests—and ends with structured reflection logged in session files. This loop is explicit, repeatable, and auditable.

* **Auto-Retry Mechanism:** When tests fail, the agent enters a retry loop: analyzing failure, applying a fix, and retesting. This continues until success or a stopping condition is met. Each iteration documents intent, changes, and test outcomes.

* **Safe Experimentation:** Engineering conventions enforce isolation through branches, structured commits, and session logging. Failed attempts can be discarded without loss, while preserving learnings in logs.

* **Durable Reflection:** Every session log ends with a reflective section—“Lessons Learned / Next Steps”—capturing insights that guide subsequent planning and reduce repeated mistakes.

### Lessons Learned and Insights

* **From Prompting to Process:** Making reasoning and reflection explicit turned what could have been a fragile prompt into a resilient process.

* **Failure is a Feature:** When a flow doesn’t work, the agent learns from it, documents the outcome, and restarts cleanly. This is more powerful than avoiding failure—it normalizes it as part of disciplined iteration.

* **Debugging as a Use Case:** In one example, the agent spent multiple sessions troubleshooting an issue, isolating behaviors, and documenting attempts before discarding the failed path and restarting. The result was cleaner implementation informed by prior knowledge.

* **Process Fidelity Improves Outcomes:** Enforcing Reason → Act → Reflect ensures consistent agent behavior, even across complex or ambiguous tasks. When a human revisits a task, the log provides clarity on what was tried, why it failed, and what comes next.

### Impact and Benefits

* **Resilient Development Loops:** Tasks evolve through intentional, test-anchored retries—not guesswork or overwrite cycles.
* **Transparent Iteration:** Each retry is documented, making agent reasoning visible and debuggable.
* **Safe Failure Recovery:** Complex failures are logged and isolated, enabling clean restarts with accumulated insight.
* **Process Over Prompting:** By embedding ReAct and CoT into runtime logic and logs, the system remains robust and maintainable as scale and complexity increase.

## 6. Don’t Confuse Autonomy with Chaos

**Pattern:** Every destructive capability is off by default and gated behind environment flags; sensitive errors are redacted unless explicitly enabled.

Autonomy in agent-driven systems doesn’t mean unchecked freedom—it means empowered execution within clearly defined safety boundaries. Especially when agents interact with live, production-grade systems like OSDU, autonomy must be paired with robust guardrails to prevent unintended or destructive outcomes.

### Strategic Implementation

* **Environment-Based Safeguards:** All destructive capabilities (e.g., deleting partitions, editing entitlements) are gated behind environment flags following a dual permission model (ADR-020): `OSDU_MCP_ENABLE_WRITE_MODE` for create/update operations and `OSDU_MCP_ENABLE_DELETE_MODE` for destructive operations. Read-only behavior is the default, and unsafe actions are explicitly opt-in.

* **Safe Defaults and Observable Failures:** Attempts to perform restricted actions trigger clear, actionable errors (e.g., “Write operations disabled. Set OSDU\_MCP\_PARTITION\_ALLOW\_WRITE=true to enable.”) rather than silent failures or cryptic exceptions. These events are logged and surfaced for audit.

* **Controlled Integration Testing:** Integration tests that involve real backend systems are only enabled in environments configured for destructive actions. Unit tests mock external services, while integration tests are tightly scoped and environment-gated.

* **Granular Capability Flags:** Environment variables are scoped narrowly to the specific tools or services being protected, ensuring precision and minimizing accidental escalation of agent privileges.

### Lessons Learned and Insights

* **Guardrails Build Confidence:** With write protections in place by default, both developers and agents could iterate more freely, knowing that mistakes would be blocked before becoming harmful.

* **Testing Discipline Reduces Risk:** Separating unit and integration test strategies helped maintain fast feedback while keeping backend risks contained.

* **Safe Experimentation Patterns:** The Partition Service pattern—where destructive operations are denied unless explicitly allowed—proved a reusable model for other services.

* **Actionable Observability is Essential:** Clear, descriptive error messages turned failed writes into teachable moments for agents, prompting them to revise plans or escalate appropriately.

### Impact and Benefits

* **Fail-Safe Defaults:** Systems were resilient by default, requiring no manual overrides to prevent damage.
* **Confidence in Live Environments:** Agents were able to interact with real backends without risk to data integrity.
* **Tighter Feedback Loops:** Developers received immediate, descriptive errors when protections were triggered.
* **Extensible Safety Model:** The same flag-based pattern was reused across services, making safety policies easy to scale.

## 7. The Real Value Is in Orchestration

**Pattern:** Shared patterns (service-client, naming conventions) let dozens of tools behave consistently. Documented workflows in CONTRIBUTING.md and ADRs turn those patterns into repeatable practices for the agent.

The logs and results from this project consistently show that while the agent excels at execution, the real power—and engineering challenge—comes from orchestration. Coordinating specs, tools, naming patterns, and workflows into a unified system is what enables speed, safety, and repeatability at scale.

### Strategic Implementation

* **Standardized Tooling Patterns:** Shared architectural conventions—like consistent service-client patterns, naming rules (ADR-019), and label strategies—give structure to the codebase. These enable the agent to understand, predict, and manipulate the system reliably.

* **Workflow Documentation and Patterns:** Documented patterns in CONTRIBUTING.md, CLAUDE.md, and ADRs act as reusable workflows for common tasks. These patterns embody architectural best practices and eliminate variability in how refactors, tests, and migrations are performed.

* **Orchestration Over Execution:** The system favors coordinated activity over isolated code generation. Workflows tie together spec writing, test scaffolding, code updates, and documentation in a sequence that delivers outcomes, not just files.

* **Process Capture Through Logs:** Each session captures not just what was done, but how. This growing library of session logs and ADRs becomes the documentation of orchestration itself—showing how agent cycles evolve over time.

* **Label-Driven Task Distribution:** The comprehensive label strategy enables intelligent task routing. Issues are automatically categorized and assigned to the appropriate agent (human, Claude Code, or GitHub Copilot) based on label combinations, creating a self-organizing development pipeline.

### Lessons Learned and Insights

* **Execution Is Easy, Coordination Is Hard:** Code generation is fast. Aligning that code with architecture, documentation, and tests requires intentional orchestration.

* **Consistency Compounds:** Shared conventions across tools and services dramatically reduce friction. The more structure we introduced, the faster the agent moved.

* **Engineer as Conductor:** The modern engineer isn't just a code author—they’re a process manager, guiding the agent, tuning workflows, and building reusable systems that scale.

* **Process Is a Product:** Our workflows became as important as the services we shipped. Well-orchestrated processes made high-quality delivery consistent and fast.

### Impact and Benefits

* **Accelerated Project Velocity:** Repeatable workflows enabled parallel agent sessions without confusion or conflict.
* **Sustained Code Quality:** Shared patterns meant every tool or service adhered to architectural standards automatically.
* **Increased Reuse and Scalability:** Tools, tests, and refactors were defined once and used everywhere.
* **Continuous Improvement:** With orchestration captured in logs and templates, process improvements were easy to identify and apply.

## 8. Multi-AI Orchestration: Specialized Agents for Specialized Tasks

**Pattern:** Different AI agents excel at different tasks. Claude Code handles architecture and complex reasoning, while GitHub Copilot executes well-defined implementation tasks.

The evolution from single-agent to multi-agent orchestration represents a significant maturation in AI-driven development. By recognizing that different AI systems have distinct strengths, the project leverages each agent for what it does best.

### Strategic Implementation

* **Claude Code for Architecture:** Complex architectural decisions, ADR creation, multi-file refactoring, and system design remain with Claude Code. Its deep reasoning capabilities and ability to maintain context across large codebases make it ideal for high-level engineering tasks.

* **GitHub Copilot for Implementation:** Well-scoped, pattern-based tasks are delegated to GitHub Copilot through labeled issues. Tasks like adding test coverage, implementing new tools following existing patterns, or fixing lint errors are perfect for Copilot's execution strengths.

* **Label-Based Task Routing:** The sophisticated label strategy (documented in `docs/label-strategy.md`) includes a "copilot" label that triggers automated assignment. This creates a seamless handoff mechanism between human engineers, Claude Code, and GitHub Copilot.

* **Shared Context and Standards:** Both AI agents reference the same documentation (CLAUDE.md, copilot-instructions.md) and follow identical quality standards, ensuring consistency regardless of which agent performs the work.

### Lessons Learned and Insights

* **Specialization Improves Quality:** Claude Code's architectural work combined with Copilot's focused implementation creates better outcomes than either agent working alone.

* **Automated Handoff Reduces Friction:** The GitHub Action that auto-assigns Copilot-labeled issues eliminates manual coordination overhead.

* **Common Standards Are Critical:** Shared documentation and testing requirements ensure all agents produce compatible, high-quality code.

* **Human Orchestration Remains Key:** Engineers still define tasks, review outputs, and ensure agents are working on appropriate problems.

### Impact and Benefits

Multi-agent orchestration delivers:

* **Parallel Development:** Multiple agents can work on different aspects simultaneously
* **Optimized Resource Usage:** Each agent focuses on tasks matching its strengths
* **Improved Velocity:** Specialized task routing reduces iteration time
* **Consistent Quality:** Shared standards ensure uniform code quality

---

## Putting It All Together: From Principles to Practice

Agentic coding tools like Claude Code are intentionally flexible and unopinionated, empowering engineers to shape their own workflows. Anthropic’s best practices—context curation, tool integration, iterative planning, and workflow customization—are foundational. But the real value emerges when these principles are operationalized in a disciplined, production-grade engineering system.

### How We Applied Agentic Coding Principles in OSDU MCP Server

1. **Context is King—But Make it File-Based and Durable**
   Anthropic recommends using project-level context files (like `CLAUDE.md`). We took this further: every session log, ADR, and spec is a persistent, structured artifact. The agent loads only what’s needed, keeping prompts lean and memory durable.

2. **Workflow Discipline—From Flexible to Prescriptive**
   While Claude Code is unopinionated, we engineered a deterministic lifecycle: `Issue → Branch → Context → Code → Test → Docs → MR → Session Log`. This is enforced by both project conventions and automation, ensuring every change is traceable and auditable.

3. **Tooling as a Force Multiplier**
   Anthropic highlights the power of shell and custom tools. In our system, bash, `gh`, and documented workflow patterns are first-class citizens. The agent orchestrates complex refactors, test runs, and documentation updates by following established patterns, all versioned and reusable.

4. **Iterative Planning and Reflection**
   We operationalize “plan before code” by requiring specs and failing tests before implementation. Every session ends with a reflective log, capturing lessons learned and next steps—fueling continuous improvement.

5. **Safety and Autonomy with Guardrails**
   Anthropic’s “safe yolo mode” is mirrored in our environment flag gating and destructive-action safeguards. The agent can move fast, but never at the expense of production safety or architectural discipline.

6. **Orchestration and Human-in-the-Loop**
   The engineer’s role shifts from code author to orchestrator—managing, sequencing, and nudging the agent for rapid, high-quality results. Our logs and process artifacts encode this experience, making it reusable and scalable.

