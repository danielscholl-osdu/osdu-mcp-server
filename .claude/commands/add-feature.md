READ specs/$ARGUMENT

Before Starting:
- gh: create a issue with the a short descriptive title.
- GIT: checkout a branch and switch to it.

IMPLEMENT TOOL
> Provide task updates to the issue if appropriate.

On Completion:
- GIT: commit with a descriptive message.
- GIT: push the branch to the remote repository.
- gh: create a PR and link the issue.


You are an experienced Software Engineer tasked with implementing a feature.

First, let's review the feature arguments provided:

<feature_arguments>
{{feature_ARGUMENTS}}
</feature_arguments>

Begin by analyzing the feature and deciding if a spec exists.
- If spec found READ spec.
- If spec not found analyze feature and if vague ask for clarification. 

**GUIDANCE**

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

**TODO List**
☐ Create github issue for feature implementation
☐ Create feature branch from main
☐ Implement feature
☐ Commit changes
☐ Push feature branch to github
