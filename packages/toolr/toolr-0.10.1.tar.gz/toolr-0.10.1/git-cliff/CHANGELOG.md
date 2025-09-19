# Changelog

All notable changes to this project will be documented in this file.

This project uses [*git-cliff*](https://git-cliff.org/) to automatically generate changelog entries
from [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.10.1 - 2025-09-19

### <!-- 1 -->🐛 Bug Fixes

- *(parent)* Fix command nesting ([`c223dfc`](https://github.com/s0undt3ch/ToolR/commit/c223dfc88e2981dbd7cd6aed304d219fc3f8f12a))
- *(command)* We now log the `.run()` cmdline at the `INFO` level ([`1311f8d`](https://github.com/s0undt3ch/ToolR/commit/1311f8d817fd71b4aa2b061c48d3e067b8076486))
- *(tests)* Fix `ctx.which` tests to make them less brittle. ([`8a55cf3`](https://github.com/s0undt3ch/ToolR/commit/8a55cf32e5e793472b5059a5a433b3e6a90cfc38))

### <!-- 7 -->⚙️ Miscellaneous Tasks

- *(release)* Don't update ToolR action usage in workflows ([`fbe4992`](https://github.com/s0undt3ch/ToolR/commit/fbe49927887da44cfbba0e8e4892a672d14837df))
- *(release)* Add workflow that updates ToolR versions in workflows ([`9782974`](https://github.com/s0undt3ch/ToolR/commit/9782974d40ff2d62a183025c9c48dee0d3e92143))
