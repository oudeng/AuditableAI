# Framework and executable scope

The dissertation connects **a unified theoretical framework, mathematical constructions under explicit conditions, and empirical examination**. The framework is claim-centered: a model output becomes evidence only in relation to an assertion, population, reference and procedure.

## Requirements and record

| Requirement | Operational question | Record fields |
|---|---|---|
| R1 | What is asserted, for whom, at what time, in which units? | `clm`, `scp` |
| R2 | Which model, expression or readout can be inspected? | `art` |
| R3 | Which reference tests the meaning of this assertion? | `ref` |
| R4 | Which information and inferential units does the comparison permit? | `pro` |
| R5 | Which evidence supports the result, and what warrants revision? | `evd`, `bnd` |

`auditableai.records.ClaimRecord` serializes these seven fields and their content fingerprint. A populated record is not proof of its statements. The fingerprint detects changes to content; it is not independent authentication of scientific truth or an external timestamp.

## Mathematical constructions

For a direct-feature logistic gate, let `z = (x − μ)/s`, with the saved training transformation and `s > 0`. The gate is `g(z) = sigmoid(α(z − τ))`. In the native coordinate, `α_x = α/s` and `τ_x = μ + sτ`. The shared estimator exports these coordinates, its intercept, linear terms and training medians. Unit tests compare exported and host predictions, including missing and shifted inputs.

These coordinate identities and logistic properties are established mathematics. The research contribution lies in exposing the relevant objects through model construction, retaining their conditions, and testing their empirical role. A gate location is not automatically a clinical cutoff. The Japanese diagnostic checks whether existing terms are active on observed inputs; it does not estimate threshold stability across new fits.

The finite audit interface receives a declared scope, a model export, a registered reference and unlabeled probes. It never receives outcome labels or the injected-fault family. The scoring harness retains that truth separately. Its concrete checks concern schema, scope, coordinates, numerical replay and cross-artifact dependencies. The interface is a research implementation for these gates, not a general-purpose security or semantic-validation system.

## Four studies and three new applications

The four source studies are retrospectively synthesized around the requirements. This is not a claim that they were originally prospectively designed as one system. RPS separates competitive ability from roster-specific score; LGO separates a meaningful threshold from an expression location; VERA separates dependence or reliance from attention weights; CaST separates usable hierarchical knowledge from a protocol-specific retrieval metric.

The new clinical and NHANES applications fit additive gates and fair comparators. The Japanese application forecasts an institutionally defined regional health indicator and traces it to published cells. These applications test different consequences of the framework. They do not share a universal auditability score, establish clinical benefit, or measure users' time savings.

## Dispositions and boundaries

The supported outcome may be a retained claim, a narrower scope, an unsupported interpretation, or an unresolved question. Useful failures are retained: a falsely declared unit on a new input batch cannot be authenticated by replaying old probes; a strong conventional pipeline ties the structured checker; the Japanese learned models forecast upward during a declining regime. The framework helps identify the object and assumption that need examination without turning those failures into a predictive-success claim.
