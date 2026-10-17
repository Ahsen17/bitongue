## [0.1.0] - 2026-10-17

### 🚀 Features

- Base constructions
- Message flowing within timeout ignore
- Base task handler protocols
- Base filters protocols
- Bitongue client and config
- Add api docstrings for public objects
- *(filter)* Add keyword and sparse duplicate-detection filters
- [**breaking**] Require ids on messages and results and rename data modules
- *(client)* Run the filter chain concurrently and make lifecycle idempotent
- *(filter)* Skip non-text messages in the keyword and sparse filters
- *(filter)* Add the neuro filter with LLM-based rule judgment

### 🚜 Refactor

- *(filter)* Trim root re-exports and move JiebaTokenizer to sparse

### 📚 Documentation

- Changelog doc
- Add bilingual readme and contributing guides
- Build bilingual sphinx site with guide pages and api reference
- License mod
- Enable napoleon to render google-style docstrings
- Cover the built-in filters across the bilingual docs site
- Sync the bilingual site and READMEs with ids, concurrency, and the sparse split
- Document the neuro filter across the bilingual site and READMEs

### 🧪 Testing

- Add unit tests mirroring src layout
- Add end-to-end integration tests
- *(filter)* Add unit and integration tests for the filter package
- *(filter)* Add unit and integration tests for the neuro filter

### 📦 Build System

- Make sparse filter dependencies optional
- Add the PyPI publish workflow with trusted publishing

### ⚙️ Miscellaneous Tasks

- Github workflows
