import os


def env_get(envvar_name: str) -> str:
    try:
        return os.environ[envvar_name]
    except Exception as e:
        raise RuntimeError(
            f'Expected ${envvar_name} envvar to be populated: {e}'
        )
