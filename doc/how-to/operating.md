# Operating

## Ingest

When `incoming/{dataset-name}/TRIGGER` is present, the supercomputer has completed
sending input data.

* `dataset-name`: `snow-surface-properties` or `snow-water-equivalent`.

At this point, ingest can begin. Run:

```
./scripts/container-cli.sh ingest-daily-ssp
```

...or...

```
./scripts/container-cli.sh ingest-daily-swe
```

depending on the dataset to be ingested.
