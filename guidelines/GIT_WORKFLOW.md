# Git Workflow

**Maintainer:** Lars (Technical Manager)

- Project Managers create and assign feature issues from Gantt-Chart
    - Big issues can be split up into sub-issues
- Everybody can create and assign issues for bugs that they find
- Development is performed on individual issue branches (created using GitLab UI or locally)
    - No direct pushing to **main** or **dev**!
    - Commits must be named according to commit message convention based on [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
        - Format: `type(scope): subject` or `type: subject`
        - Type must be one of `feat|fix|docs|style|refactor|perf|test|chore|build|ci`
        - Scope must be one of `frontend|backend|controller`, or none if multiple components are affected
        - Subject must be commit message in English starting with a lower-case letter or number and not longer than 50 characters
- Merge request (MR) is created as early as possible during development (with **dev** as target!)
    - Author adds themselves as assignee
    - MR is marked as Draft until Development is finished
    - If code has been written, author must add at least one **Quality Manager** (Adam/Julius) as reviewer
        - Reviews the coding style and safety requirements
    - If config files are changed, author must add **Technical Manager** (Lars) as reviewer
        - Ensures that changes to CI process are correct
    - If any architecture/communication code is written, author must add **Integration Manager** (Maxim) as reviewer
        - Ensures that the component, data and protocol definitions are either adhered to or updated to match the code
    - CI pipeline automatically validates commit messages and performs linting and tests
    - Fixes and requested changes from the review process must be added as additional commits
        - No force pushing during the review process! (makes reviewing changes more difficult)
- When all reviewers have approved the MR **and** the CI pipeline is passing, the author may merge the MR to **dev**
    - If more commits were added during the review process, the changes should be squashed using the GitLab UI or using a force push to the issue branch
    - The issue branch must be deleted after it has been merged
- **Technical Manager** (Lars) periodically merges stable code to **main**