# Development

## CLI development usage

### Local

```
conda env create
# ...
python scripts/cli.py
```


### Docker

Override compose configuration with the dev compose-file:

```
ln -s docker-compose.dev.yml docker-compose.override.yml
./scripts/container_cli.sh
```
