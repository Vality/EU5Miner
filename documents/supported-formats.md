# Supported Formats

## Current Implementation

### Script-like text

Supported today as structural analysis only.

The implementation now also includes a minimal CST tokenizer layer and first-pass grouping into statements and blocks for script-like text.

On top of that, the project now includes a semantic helper layer for object-like definitions and key/value access.

The first domain-specific adapters are now scripted trigger parsing, scripted effect parsing, and setup-country parsing.

Capabilities:

- comment-aware brace balancing
- quoted-string awareness
- macro detection such as `$target_rank$`
- scoped reference detection such as `scope:actor`
- typed reference detection such as `government_type:republic`
- database entry mode detection such as `INJECT:key`
- tokenization of comments, whitespace, strings, operators, braces, macros, atoms, and GUI bracket expressions
- grouping of top-level and nested statements into assignment-like entries, block entries, and scalar values
- semantic access to object-like entries, first-entry lookup, and scalar child extraction for common modding structures
- domain-level scripted trigger parsing with definition lookup and argument placeholder detection
- domain-level scripted effect parsing with definition lookup and argument placeholder detection
- domain-level setup-country parsing with tag lookup and typed access to common setup fields

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

- Full script parser and richer CST tree shapes beyond first-pass statement/block grouping
- Strongly typed semantic models for events, missions, situations, and other major domains
- Full GUI parser
- Format-preserving writers
- Image decoding for map assets
- Binary engine file support

