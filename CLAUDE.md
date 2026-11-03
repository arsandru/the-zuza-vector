# the-zuza-vector: working rules

**Start of every session: read `HANDOFF.md` first (state, decisions, open items), then `README.md`. Update `HANDOFF.md` before ending a session.**

- Everything here is exploratory. Say so in reports and figure captions, and say when a rule (word list, mapping, threshold) was written after looking at the data.
- Multiplicity: Benjamini-Hochberg FDR within each family of tests (not Holm). Report estimates with intervals; say "no evidence of a difference" for a null.
- Unit of inference is the participant. Cleaning, embedding space and wheel mapping decisions are recorded in `HANDOFF.md`; do not change them silently or choose a method because of its result.
- Use `np.einsum` for similarity matrices (spurious overflow warnings with `@` on this machine).
- Re-running a script overwrites tracked outputs: check `git status` and `git diff --stat` and tell the user what changed numerically.
- `data/tDCS.csv` is participant data: keep the repository private and do not copy the data elsewhere.
- Commit and push only when asked.
