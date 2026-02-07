# Contributing to UAL

Welcome to the Universal Action Language (UAL) project. We are not just building software; we are building the communication infrastructure for the next generation of intelligent agents.

## The "UAL Bounty Hunter" Program 💰

We are looking for the first generation of core developers to expand the UAL ecosystem. We have launched the **Bounty Hunter Program** to reward high-quality contributions.

### How to Join
1.  Check the [BOUNTIES.md](BOUNTIES.md) file for active missions.
2.  Claim a bounty by opening an issue using the "Bounty Claim" template.
3.  Submit your Pull Request (PR) referencing the issue.
4.  Get your code merged and your name enshrined in the `AUTHORS` file (and potentially receive crypto/swag rewards in the future).

## Contribution Workflow

1.  **Fork & Clone**: Fork the repository and clone it locally.
2.  **Branching**: Create a feature branch: `git checkout -b feature/my-new-feature`.
3.  **Coding Standards**:
    *   **Python**: Follow PEP 8. Use `black` for formatting.
    *   **C/Embedded**: Follow strict memory management rules. No `malloc` in critical loops.
    *   **UAL**: Keep definitions in `atlas.yaml` sorted by hex code.
4.  **Testing**:
    *   Run `pytest` before submitting.
    *   Ensure all existing tests pass.
    *   Add new tests for your feature.
5.  **Commit Messages**: Use semantic commit messages (e.g., `feat: add new drone maneuver`, `fix: parser overflow error`).
6.  **Pull Request**: Submit a PR to the `main` branch. Fill out the PR template completely.

## Code of Conduct

*   **Be Logic-Driven**: Arguments should be based on technical merit and efficiency.
*   **Be Constructive**: Code review is about improving the code, not attacking the coder.
*   **No Babel**: Keep communication clear and concise.

## Getting Help

*   Join our Discord (link coming soon).
*   Open a "Question" issue on GitHub.
