# Contributing

## Branches

Use short-lived branches from `main`, for example:

- `feat/data-cleaning`
- `feat/game-state-features`
- `feat/player-ratings`
- `fix/wicket-boolean`
- `docs/nwc-attribution`

## Commits

Use concise prefixes such as `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, and `chore:`.

## Pull requests

- Keep each pull request focused on one outcome.
- Explain any change to modelling definitions or dataset exclusions.
- Add or update tests for transformation logic.
- Never commit raw data, generated feature tables, or trained models to normal Git.
- Clear large notebook outputs before review.

## Reproducibility

Every material experiment should record the Git commit, data version, configuration, random seed, validation period, and evaluation metrics.

