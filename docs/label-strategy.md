# GitHub Label Strategy

This document defines the labeling strategy for the OSDU MCP Server project, ensuring consistent categorization of issues and pull requests.

## Label Categories

### 1. Type Labels (What kind of work)
- **bug** - Something isn't working
- **enhancement** - New feature or request
- **documentation** - Improvements or additions to documentation
- **refactor** - Requires code refactoring
- **cleanup** - Cleanup tasks requiring minimal effort
- **question** - Further information is requested
- **testing** - Test coverage, test fixes, or new tests
- **security** - Security vulnerabilities or improvements
- **performance** - Performance optimizations

### 2. Priority Labels (How urgent)
- **high-priority** - High priority issues
- **medium-priority** - Medium priority issues
- **low-priority** - Low priority issues

### 3. Component Labels (What area)
- **configuration** - Related to project configuration
- **dependencies** - Pull requests that update a dependency file
- **github_actions** - Pull requests that update GitHub Actions code
- **code-quality** - Code quality improvements (linting, typing, etc.)
- **ADR** - Architecture Decision Record needed or updated

### 4. Status Labels (Current state)
- **help wanted** - Extra attention is needed
- **good first issue** - Good for newcomers
- **wontfix** - This will not be worked on
- **needs-triage** - New issues requiring review and categorization
- **blocked** - Issues blocked by dependencies or other work
- **breaking-change** - Changes that break backward compatibility

### 5. AI Agent Labels (Automation)
- **copilot** - Suitable for GitHub Copilot to implement
- **claude** - Issue created by Claude Code assistant

## AI Agent Guidelines

When creating issues, AI agents should apply labels based on:

1. **Always include one Type label** - Every issue should have exactly one type label
2. **Add Priority when clear** - If the issue mentions urgency or importance
3. **Include relevant Component labels** - Can have multiple if the issue spans areas
4. **Status labels are optional** - Apply only when explicitly relevant
5. **Add AI agent label** - Claude should add `claude` label, suitable tasks get `copilot` label

## When to Apply the Copilot Label

Apply the **copilot** label to issues that are:

### Suitable for Copilot:
- Adding new tools following existing patterns
- Improving test coverage for existing code
- Fixing type errors or lint issues
- Updating documentation
- Small, well-defined features
- Implementing validation for edge cases
- Improving error messages
- Adding missing type hints

### NOT Suitable for Copilot:
- Major architectural changes
- Security-critical modifications  
- Complex cross-service refactoring
- Ambiguous or exploratory tasks
- Initial service client implementations
- Changes requiring ADR updates
- Breaking API changes

## Label Selection Examples

### Example 1: Bug in Authentication
```
Labels: bug, configuration, high-priority
```

### Example 2: Add Documentation for Tools
```
Labels: documentation, low-priority
```

### Example 3: Refactor Authentication Code
```
Labels: refactor, configuration, medium-priority
```

### Example 4: Update Dependencies
```
Labels: dependencies, cleanup, low-priority
```

### Example 5: New Feature Request
```
Labels: enhancement, medium-priority
```

### Example 6: Fix Security Vulnerability in Auth
```
Labels: security, bug, high-priority, configuration
```

### Example 7: Improve Query Performance
```
Labels: performance, enhancement
```

### Example 8: Add Tests for Validation Logic
```
Labels: testing, medium-priority
```

### Example 9: Breaking API Change
```
Labels: enhancement, breaking-change, high-priority, ADR
```

### Example 10: Add Missing Type Hints
```
Labels: code-quality, copilot, low-priority
```

### Example 11: Improve Test Coverage for Auth Module
```
Labels: testing, copilot, medium-priority, configuration
```

## Label Colors

- **Type labels**: Red/Orange tones (#d73a4a, #a2eeef, #0075ca)
- **Priority labels**: Purple tones (#7057ff, #b3a2ff, #d4c5f9)
- **Component labels**: Green tones (#0e8a16, #5cb85c, #c5f015)
- **Service labels**: Blue tones (#1d76db, #0052cc, #006b75)
- **Status labels**: Yellow/Gray tones (#fbca04, #e4e669, #d93f0b)

## Automation

Labels can be automatically managed using:
- `.github/labels.yml` - Label definitions
- GitHub Actions for label sync
- Issue templates with default labels

### Automatic Copilot Assignment

Issues labeled with **copilot** are automatically assigned to the GitHub Copilot user via the `.github/workflows/copilot-assign.yml` workflow. The workflow:
- Triggers when the 'copilot' label is added to an issue
- Automatically assigns the issue to @Copilot
- Posts a comment confirming the assignment status
- Provides guidance on Copilot implementation patterns