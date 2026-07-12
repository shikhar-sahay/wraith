# Experiments

This folder stores experiment artifacts for both deployments documented in Ghost Cloud.

## Current Contents

- Historical Mumbai experiment reports and summaries
- Wraith daily and cumulative reports generated from JSONL telemetry
- The experiment log used to capture manual observations

## Recommended Organization

```text
experiments/
  mumbai/
    legacy reports
  wraith/
    daily reports
  cumulative.md
  experiment-log.md
```

The existing historical files remain in place and should not be deleted or overwritten.

## Related Docs

- [docs/experiment-workflow.md](../docs/experiment-workflow.md)
- [docs/telemetry-pipeline.md](../docs/telemetry-pipeline.md)