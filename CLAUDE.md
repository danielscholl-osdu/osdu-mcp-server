# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OSDU MCP Server is a Model Context Protocol server that provides AI assistants with access to OSDU platform capabilities. The project adapts patterns from the OSDU CLI while building an independent implementation optimized for MCP.

## Development Commands

- Testing framework setup (pytest)
- github `gh` command

## Key Documentation

@CONTRIBUTING.md
@docs/adr/README.md
@docs/project-architect.md


## Guidance

1. Branch Naming:
   - Use: agent/<issue-number>-<short-description>
   - Example: agent/42-fix-login-bug

2. Commit Message Format (Release Please):
   - Use Conventional Commits style for Release Please automation
   - Format: <type>[optional scope]: <description>
   - Types that trigger releases:
     - feat: - New feature (minor version bump)
     - fix: - Bug fix (patch version bump)
     - feat!: or fix!: - Breaking change (major version bump)
   - Types for maintenance (no version bump):
     - chore: - Maintenance tasks, dependency updates
     - docs: - Documentation changes
     - style: - Code formatting, no logic changes
     - refactor: - Code refactoring without new features
     - test: - Adding or updating tests

3. Merge Request (MR) Template:
   - Description: Brief summary of the changes and why they were made
   - Related Issues: List related issues (e.g., Closes #42, Relates to #15)
   - Type of Change: Bug fix, New feature, Breaking change, or Documentation update
   - Checklist: Code builds and passes tests, Documentation updated, Conventional commit format used, Reviewer assigned
   - Additional Notes: Any extra context, screenshots, or deployment considerations