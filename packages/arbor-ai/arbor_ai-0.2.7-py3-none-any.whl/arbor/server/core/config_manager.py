import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml

from arbor.server.core.config import Config


class ConfigManager:
    def __init__(self):
        self._init_arbor_directories()

    def _init_arbor_directories(self):
        arbor_root = Path.home() / ".arbor"
        storage_dir = Path.home() / ".arbor" / "storage"  # Use default storage path

        arbor_root.mkdir(exist_ok=True)
        storage_dir.mkdir(exist_ok=True)
        (storage_dir / "logs").mkdir(exist_ok=True)
        (storage_dir / "models").mkdir(exist_ok=True)
        (storage_dir / "uploads").mkdir(exist_ok=True)

    @staticmethod
    def get_default_config_path() -> Path:
        return str(Path.home() / ".arbor" / "config.yaml")

    @staticmethod
    def get_config_template() -> Dict:
        return {"inference": {"gpu_ids": [0]}, "training": {"gpu_ids": [1, 2]}}

    @classmethod
    def update_config(
        cls,
        inference_gpus: Optional[str] = None,
        training_gpus: Optional[str] = None,
        config_path: Optional[str] = None,
    ) -> str:
        """Update existing config or create new one."""

        if config_path is None:
            config_path = Config.use_default_config()
            if config_path is None:
                config_path = str(cls.get_default_config_path())

        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or use template
        if config_file.exists():
            with open(config_file, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = cls.get_config_template()

        # Update values given - convert string inputs to lists
        if inference_gpus is not None:
            if "inference" not in config:
                config["inference"] = {}
            # Convert string like "0" or "1,2" to list of integers
            config["inference"]["gpu_ids"] = [
                int(x.strip()) for x in str(inference_gpus).split(",")
            ]

        if training_gpus is not None:
            if "training" not in config:
                config["training"] = {}
            # Convert string like "0" or "1,2" to list of integers
            config["training"]["gpu_ids"] = [
                int(x.strip()) for x in str(training_gpus).split(",")
            ]

        temp_path = config_file.with_suffix(".tmp")
        try:
            with open(temp_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, default_style="'")
            temp_path.rename(config_file)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

        return str(config_file)

    @classmethod
    def validate_config_file(cls, config_path: str) -> Tuple[bool, str]:
        """Validate a config file"""
        try:
            if not Path(config_path).exists():
                return False, f"Config file does not exist: {config_path}"

            # If we do have a config file, try to see if it will load
            Config.load_config_from_yaml(config_path)
            return True, "Config is valid"

        except Exception as e:
            return False, f"Invalid config: {e}"

    @classmethod
    def get_config_contents(cls, config_path: str) -> Tuple[bool, str]:
        try:
            with open(config_path, "r") as f:
                config_content = f.read()
            return True, config_content
        except Exception as e:
            return False, str(e)
