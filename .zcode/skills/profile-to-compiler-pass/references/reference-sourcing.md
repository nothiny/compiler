# Reference sourcing for adapters

The shared skill does not embed a measurement tool or a target convention.
Project adapters are backend-specific and may consult authoritative
documentation and established open-source report skills, then expose a small,
fact-backed interface to this workflow. Adapters live in the target project
or the optional extension directory, outside shared workflow knowledge paths;
their concrete choices must still be recorded and reproducible.

## Precedence

Use sources in this order:

1. the project's declared facts and observed environment;
2. authoritative documentation for the installed measurement system and its
   report interface;
3. a version-pinned, license-compatible open-source parser or skill;
4. local experiments that verify the parser against retained raw reports.

When sources disagree, preserve the disagreement in the adapter evidence and
do not silently merge semantics.

## Provenance record

The project-side adapter declaration records, for each consulted source:

- canonical URI or repository path;
- release, commit, or document revision;
- license and redistribution constraints;
- the purpose of the reference;
- the adapter code or rule that depends on it;
- a retained fixture or raw report used for verification.

The shared manifest carries source references but does not copy source-specific
rules into this repository.

## Adapter quality checks

An adapter built from a reference must have bounded checks for:

- report instance enumeration and unambiguous identity matching;
- preservation of source names, values, units, and scopes;
- unsupported, missing, parse-error, collection-error, and zero distinctions;
- stable normalization across repeated reads of the same raw report;
- malformed-report and version-mismatch behavior;
- attribution output that states its precision and limitations.

A parser that only works for the first report instance, assumes a fixed metric
vocabulary, or turns an unreadable value into zero is not a valid adapter.

## Licensing and maintenance

Keep third-party code and documentation in the target project or optional
extension directory, where its license and version can be audited. The workflow skill may describe the adapter
contract, but it must not vendor copied helpers or target-specific examples.
When a reference changes, rerun fixture checks, update the adapter revision,
and preserve the old campaign evidence so a manifest remains reproducible.
