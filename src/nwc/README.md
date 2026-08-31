# Shared helpers (reserved)

The numbered notebooks under `notebooks/` are the primary project code.
Use this package only after logic is stable and shared by multiple notebooks.

Do not create a parallel pipeline here for code that belongs to a single
notebook. Any future helper must have a narrow interface and a corresponding
test or notebook-level verification cell.
