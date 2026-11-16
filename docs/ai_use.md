# Use of AI models in this study

Each use of a language model, with the model, its version, the dates and the work. New uses are added as they happen. Each commit also names its AI co-author.

| Dates | Model | Work |
|---|---|---|
| Wed Nov 4 to Sun Nov 15, 2026 | Claude Opus 5.5 (Anthropic) | Drafted the study design, `docs/preregistration.md`, `docs/event_codebook.md`, `docs/coding_prompt.md`, and wrote the code in `src/cfo` and `scripts`. |
| Thu Nov 5, 2026 | Claude Fable 5.1 (Anthropic) | Reviewed and confirmed the data sources and the test bed after the author approved them that day. |
| Sun Nov 15, 2026 | Claude Opus 5.5 (Anthropic), a separate session | One independent review of the design before the freeze; its findings were applied. |
| Mon Nov 16, 2026 | Claude Fable 5.2 (Anthropic) | A second review of the design before the freeze, as a methods reviewer; its findings were applied, the fuel labels were read at the three sources and the emission factors on the IPCC table. The same session recorded the author's confirmation of the model values, made the freeze commits and deposited the four files on Zenodo. |
| Mon Nov 16, 2026 | Claude Fable 5.2 (Anthropic), a separate session | A further independent review after the first freeze commit; its six corrections were applied before the final freeze and the deposit. |
| Mon Nov 16, 2026 | Claude Opus 5.5 (Anthropic) | Wrote the fetcher, the script coder, the event, eligibility and carbon-table code and the test bed; coded the 270 retrievable reports in 29 fresh sessions under `docs/coding_prompt.md` (`logs/coding/manifest.json`); a separate session researched the regions' general-availability pages and grid zones for `dataset/region_table.csv`, each value with its source. |

The author approved the data sources and the test bed of the design, confirmed the primary values of the recovery model, the availability target and the visibility assumption against his production experience (Mon Nov 16, 2026), codes the blind sample of the outage coding, reads the results and the paper before submission, and is responsible for every claim.
