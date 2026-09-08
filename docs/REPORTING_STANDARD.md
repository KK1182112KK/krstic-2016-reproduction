# Reporting standard for each reproduction project

Every project report must make the chain **source equation → implementation → conditions → observed result → interpretation** explicit. This convention applies to new reports and updates; it is not a claim that unlisted experiments have been performed.

## Required structure

1. **Source and scope.** Give title, authors, year, DOI, example/section, printed page number, and figure number where relevant. Say when the paper has no numerical figure for the selected example.
2. **Equation-to-code map.** Cite paper equation numbers separately for the physical plant, controller, predictor/transform, assumptions, and target/reference. Name and link the actual implementation functions.
3. **Experimental conditions.** Record the state and input histories, numerical parameter values, simulation horizon, controller sampling/hold convention, solver, tolerances, interpolation, guards, and source revision. Identify choices absent from the paper as repository choices or hypotheses.
4. **Measured results.** Link committed JSON/CSV/log evidence and state how every metric is calculated. Include failed or incomplete cases rather than retaining only favorable cases. Report all stored refinement rows for a comparison.
5. **Interpretation and limitations.** Explain the numerical outcome and what it does not establish. Distinguish convergence at finite T, empirical step refinement, reproduction of a published plot, and a mathematical stability guarantee.
6. **Reproduction instructions and provenance.** Provide runnable commands, output filenames, environment/source records, and the exact CI run or tested commit. Never replace dated evidence with a statement that the latest commit must also have passed.

## Equation citation rules

- Use the paper identifier when multiple papers are discussed: e.g. **[P16, Eqs. (28)–(29)]**, **[P12, Eqs. (67)–(70)]**.
- Attribute unnumbered assumptions or initial conditions to the named paragraph and page. Do not invent an equation number for them.
- Retain the original equation numbering only for an exact transcription or an explicitly explained equivalent notational restatement.
- Label a new diagnostic, simplified derivation, or corrected alternative as **repository-defined / derived**, not as the formula printed in the paper.
- Keep the printed and chain-rule-consistent variants available as separately labeled experiments. Do not silently repair a published formula before claiming reproduction.

## Numerical result rules

A numerical claim must specify the experiment, equations, conditions, value, field/file, and limit. For example:

> For [P16, (28)–(29)] with sampled evaluation of (32)–(34), D=1, zero input prehistory, X(0)=(1,1), h=0.005 and T=20, the archived Euclidean physical-state norm is 0.0728144524 (`results/direct-dde/summary.json`, `final_X_norm`). This is a finite-time observation, not the history norm in (18) or a global-stability proof.

Do not confuse an elementwise maximum with a Euclidean norm, a sampled extremum with a certified continuous extremum, a source figure with our plot, or a corrected-variant result with the printed-controller result. Display rounding is allowed; source precision is not automatically a numerical error bound.

## Evidence classification

| Label | Meaning |
|---|---|
| Paper statement | Directly supported by an identified equation, paragraph, table, or figure. |
| Derived observation | A calculation shown explicitly from the cited equations. |
| Archived numerical result | Produced by identified code/conditions and retained in a linked data/log file. |
| Visual estimate | Approximate inspection of a figure, not author-supplied raw data or digitized matching. |
| Hypothesis / unverified | Plausible explanation or proposed experiment without sufficient archived evidence. |

The theory remains attributed to its original authors. This project's contribution is its implementation, reproduction, verification, and documented corrections to its own software. The software citation and paper citations must remain distinct.
