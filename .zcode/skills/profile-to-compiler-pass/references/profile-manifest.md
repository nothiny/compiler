# Profile manifest contract

`PROFILE_MANIFEST.json` is the normalized index for one profiling campaign.
It is evidence, not a replacement for the raw report. The manifest must be
reproducible from the raw report and the project adapter declaration.

## Backend adapter boundary

The adapter is a backend extension, implemented in the target project or the
optional `adapters/` directory. Its commands, parser dependencies, metric
vocabulary, and generated-code readers may be backend specific; the project
binds them to this experiment. The shared workflow expects four observable operations, whether they
are functions, commands, or task steps:

1. `preflight` reports versions, permissions, supported observation classes,
   and failures without collecting a partial result;
2. `collect` runs the declared measurement route on the compiler's actual
   generated artifact and retains raw reports;
3. `normalize` enumerates report instances and emits this manifest without
   dropping source names, units, scopes, or status values;
4. `attribute` links report ranges to generated code, IR, and pass trace with
   an explicit precision and limitation.

The adapter may expose additional backend operations, but these four results
must remain reproducible and must not be inferred by the shared workflow.

## Envelope

The top-level object contains at least:

~~~
{
  "schema_version": 1,
  "campaign_id": "<stable id>",
  "compiler": {
    "revision": "<revision>",
    "artifact": {"path": "<relative path>", "sha256": "<digest>"}
  },
  "target": {"fingerprint": "<fact-backed identity>", "facts": ["<fact id>"]},
  "workloads": [
    {
      "id": "<stable id>",
      "constructs": ["<declared construct this workload exercises>"],
      "shape": "<project-defined value>",
      "type": "<project-defined value>",
      "layout": "<project-defined value>"
    }
  ],
  "invocations": [{"id": "<stable id>", "configuration": {}}],
  "profiler": {
    "adapter": "<project entry point>",
    "version": "<declared version>",
    "sources": [{"uri": "<documentation or source>", "revision": "<optional>"}]
  },
  "reports": [{"path": "<relative raw report>", "sha256": "<digest>"}],
  "observations": [],
  "attribution": {"status": "mapped|partial|unavailable", "references": []}
}
~~~

The `target` object is a reference to project facts. It must not reproduce
target-specific rules in the shared skill. The `shape`, `type`, and
`layout` fields are opaque project values; do not infer a default vocabulary.

## Workloads are plural, and they are the campaign's width

`workloads` and `invocations` are **lists**. They were single objects, and that
one fact decided the shape of everything downstream: the authoritative,
digest-bound evidence of a whole round could describe exactly one case, so
"profile one case, write one pass" was the only thing the artifact could
express. A single object is still read as a one-element list, but a campaign
that profiles one workload is a campaign that has located the cost of one
case, not the cost of the compiler.

Each workload names the constructs it exercises so the optimizer can interpret
the observations and their limits. There is no coverage percentage against the
whole implemented surface. Select inputs relevant to the proposed batch, including
boundaries that could invalidate the benefit or legality hypothesis.

`compiler.revision` identifies the profiled program. After a change, assess whether
the observations still justify the next choice; reprofile when the relevant
bottleneck changes or evidence is insufficient. Historical profiles cannot certify
current performance or correctness. Additional probes and campaigns stay within
the same task unless its scope or budget requires a new decision.

## Observation record

Each observation retains the source spelling and scope:

~~~
{
  "name": "<source metric name>",
  "value": 0.0,
  "unit": "<source unit>",
  "scope": {"report": "<id>", "instance": "<id>", "workload": "<workload id>",
            "code_range": "<optional>"},
  "status": "collected",
  "source": {"path": "<raw report>", "location": "<adapter location>"},
  "notes": "<optional interpretation-free note>"
}
~~~

Allowed statuses are `collected`, `zero`, `unsupported`, `missing`,
`parse_error`, and `collection_error`. A `zero` value is valid evidence only
when the adapter actually collected it. Unknown, omitted, or failed values must
not be serialized as zero.

## Instance matching

The adapter must enumerate all report scopes and invocation instances that may
match the campaign. It chooses an instance only after checking the workload id,
invocation id, compiler revision, artifact digest, fact-backed target
fingerprint, and project-defined shape metadata. If two instances remain
ambiguous, mark the observation `missing` with an ambiguity note and request a
bounded follow-up; never silently choose one.

## Provenance and retention

Keep the exact collection command, adapter revision, environment snapshot,
raw-report digest, and parser errors in the campaign evidence. Record official
documentation or open-source parser references in the adapter's project-side
declaration, including the version consulted. The shared skill consumes this
provenance without importing assumptions from those sources.

## Minimal validity checks

An adapter must reject a manifest when:

- the artifact or report digest is absent or does not match;
- a consumed observation has no unit, scope, status, or source, or its scope
  names no `workload` the manifest declares;
- a declared workload names no `constructs`, or names one the coverage matrix
  does not record as implemented;
- the workload or invocation cannot be tied to the experiment contract;
- an unsupported or failed observation is represented as a numeric zero;
- an instance was selected without an identity match;
- attribution claims exact IR correspondence without a source mapping.
