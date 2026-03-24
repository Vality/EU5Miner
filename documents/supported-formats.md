# Supported Formats

## Current Implementation

### Script-like text

Supported today as structural analysis only.

The implementation now also includes a minimal CST tokenizer layer for script-like text.

Capabilities:

- comment-aware brace balancing
- quoted-string awareness
- macro detection such as `$target_rank$`
- scoped reference detection such as `scope:actor`
- typed reference detection such as `government_type:republic`
- database entry mode detection such as `INJECT:key`
- tokenization of comments, whitespace, strings, operators, braces, macros, atoms, and GUI bracket expressions

Applies to:

- `common/**/*.txt`
- `events/**/*.txt`
- `setup/**/*.txt`
- `.gui`
- `.map`
- `.info`

### Localization YAML

Supported as a lightweight reader for the Paradox localization structure:

- language header detection such as `l_english:`
- key/value entry extraction
- comment skipping

### JSON metadata

Supported for DLC and future mod metadata parsing.

### Semicolon CSV

Supported for map tables such as adjacency data.

## Deferred

- Full script parser and richer CST tree shapes
- Full GUI parser
- Format-preserving writers
- Image decoding for map assets
- Binary engine file support

