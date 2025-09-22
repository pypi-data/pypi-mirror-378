def read_env(file_path: str = ".env"):
    env_vars = {}
    with open(file_path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                env_vars[key] = value
    return env_vars
