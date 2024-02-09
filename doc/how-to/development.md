# Development

## CLI development usage

### Local

```
conda env create
# ...
python ./snow_today_webapp_ingest/cli.py
```


### Docker

Override compose configuration with the dev compose-file:

```
ln -s compose.dev.yml compose.override.yml
./scripts/container_cli.sh
```
