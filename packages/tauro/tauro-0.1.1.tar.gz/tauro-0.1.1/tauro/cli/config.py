import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger  # type: ignore

from tauro.cli.core import (
    ConfigCache,
    ConfigFormat,
    ConfigLoaderProtocol,
    ConfigurationError,
    SecurityError,
    SecurityValidator,
)


class YAMLConfigLoader:
    """Loads YAML configuration files."""

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """Load and parse YAML file."""
        if not Path(file_path).exists():
            raise ConfigurationError(f"File not found: {file_path}")

        try:
            import yaml  # type: ignore
        except ImportError:
            raise ConfigurationError("PyYAML not installed. Run: pip install PyYAML")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config or {}
        except Exception as e:
            raise ConfigurationError(f"Invalid YAML in {file_path}: {e}")

    def get_format_name(self) -> str:
        return "YAML"


class JSONConfigLoader:
    """Loads JSON configuration files."""

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """Load and parse JSON file."""
        if not Path(file_path).exists():
            raise ConfigurationError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {file_path}: {e}")

    def get_format_name(self) -> str:
        return "JSON"


class DSLConfigLoader:
    """Loads hierarchical DSL configuration files."""

    SECTION_RE = re.compile(r"^\[(?P<name>.+?)\]\s*$")

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """Load and parse DSL file with [section] and key=value pairs."""
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"File not found: {file_path}")

        result: Dict[str, Any] = {}
        current_path: List[str] = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_num, raw in enumerate(f, 1):
                    self._handle_line(
                        raw.strip(), line_num, result, current_path, file_path
                    )
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Failed to parse DSL file: {e}")

        return result

    def _ensure_section(self, root: Dict[str, Any], parts: List[str]) -> Dict[str, Any]:
        node = root
        for p in parts:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        return node

    def _process_section(self, line: str) -> List[str]:
        name = self.SECTION_RE.match(line).group("name").strip()
        return [p.strip() for p in name.split(".") if p.strip()]

    def _process_key_value(self, line: str) -> Tuple[str, Any]:
        key, value = line.split("=", 1)
        key = key.strip()
        parsed = self._parse_value(value.strip())
        return key, parsed

    def _handle_line(
        self,
        line: str,
        line_num: int,
        result: Dict[str, Any],
        current_path: List[str],
        file_path: str,
    ) -> None:
        if not line or line.startswith("#"):
            return

        m = self.SECTION_RE.match(line)
        if m:
            current_path.clear()
            current_path.extend(self._process_section(line))
            self._ensure_section(result, current_path)
            return

        if "=" in line:
            key, parsed = self._process_key_value(line)
            section = self._ensure_section(result, current_path)
            section[key] = parsed
            return

        raise ConfigurationError(
            f"Unrecognized DSL syntax at {file_path}:{line_num}: {line}"
        )

    def _parse_value(self, value: str) -> Union[str, int, float, bool, List[Any]]:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]

        low = value.lower()
        if low == "true":
            return True
        if low == "false":
            return False

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            items = [i.strip() for i in inner.split(",")]
            return [self._parse_value(i) for i in items if i != ""]

        return value

    def get_format_name(self) -> str:
        return "DSL"


class ConfigDiscovery:
    """Automatically discovers configuration files in directory tree."""

    CONFIG_PATTERNS = [
        "settings_yml.json",
        "settings_json.json",
        "settings_dsl.json",
        "settings.json",
        "config.json",
        "tauro.json",
    ]

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.discovered_configs: List[Tuple[Path, str]] = []

    def discover(self, max_depth: int = 3) -> List[Tuple[Path, str]]:
        """Find all configuration files within max_depth levels."""
        cache_key = f"{self.base_path}:{max_depth}"
        cached = ConfigCache.get(cache_key)
        if cached:
            self.discovered_configs = cached
            return cached

        self.discovered_configs = []
        try:
            self._search_recursive(self.base_path, 0, max_depth)
        except Exception as e:
            logger.warning(f"Error during config discovery: {e}")

        ConfigCache.set(cache_key, self.discovered_configs)
        logger.info(f"Discovered {len(self.discovered_configs)} configurations")

        return self.discovered_configs

    def _search_recursive(self, path: Path, depth: int, max_depth: int) -> None:
        """Recursively search for config files."""
        if depth > max_depth or not path.is_dir():
            return

        try:
            for pattern in self.CONFIG_PATTERNS:
                config_file = path / pattern
                if config_file.is_file():
                    self.discovered_configs.append((path, pattern))
                    break  # Only one config per directory

            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    self._search_recursive(item, depth + 1, max_depth)

        except OSError as e:
            logger.debug(f"Skipping inaccessible directory: {path} - {e}")

    def find_best_match(
        self,
        layer_name: Optional[str] = None,
        use_case: Optional[str] = None,
        config_type: Optional[str] = None,
    ) -> Optional[Tuple[Path, str]]:
        """Find configuration that best matches the criteria."""
        if not self.discovered_configs:
            self.discover()

        if not self.discovered_configs:
            return None

        scored = []
        for config_dir, config_file in self.discovered_configs:
            score = 0

            if layer_name and layer_name.lower() in str(config_dir).lower():
                score += 30

            if use_case and use_case.lower() in str(config_dir).lower():
                score += 40

            if config_type and f"settings_{config_type}.json" == config_file:
                score += 20

            score += max(0, 10 - len(config_dir.parts))

            scored.append((score, config_dir, config_file))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0]
        logger.info(f"Best match: {best[1] / best[2]} (score: {best[0]})")
        return (best[1], best[2])

    def list_all(self) -> None:
        """Print all discovered configurations."""
        if not self.discovered_configs:
            self.discover()

        if not self.discovered_configs:
            logger.warning("No configurations found")
            return

        logger.info("Available configurations:")
        for i, (config_dir, config_file) in enumerate(self.discovered_configs, 1):
            logger.info(f"  {i}. {config_dir / config_file}")

    def select_interactive(self) -> Optional[Tuple[Path, str]]:
        """Allow user to interactively select a configuration."""
        if not self.discovered_configs:
            self.discover()

        if not self.discovered_configs:
            logger.error("No configurations found")
            return None

        if len(self.discovered_configs) == 1:
            logger.info("Using only available configuration")
            return self.discovered_configs[0]

        self.list_all()

        try:
            while True:
                choice = input(
                    f"Select configuration (1-{len(self.discovered_configs)}): "
                ).strip()
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(self.discovered_configs):
                        return self.discovered_configs[index]
                print("Invalid selection. Try again.")
        except (KeyboardInterrupt, EOFError):
            logger.warning("Selection cancelled")
            return None


class ConfigManager:
    """Manages configuration loading and format detection."""

    LOADERS = {
        ConfigFormat.YAML: YAMLConfigLoader,
        ConfigFormat.JSON: JSONConfigLoader,
        ConfigFormat.DSL: DSLConfigLoader,
    }

    CONFIG_FILES = {
        ConfigFormat.YAML: "settings_yml.json",
        ConfigFormat.JSON: "settings_json.json",
        ConfigFormat.DSL: "settings_dsl.json",
    }

    def __init__(
        self,
        base_path: Optional[str] = None,
        layer_name: Optional[str] = None,
        use_case: Optional[str] = None,
        config_type: Optional[str] = None,
        interactive: bool = False,
    ):
        self.original_cwd = Path.cwd()
        self.base_path = Path(base_path) if base_path else Path.cwd()

        self.discovery = ConfigDiscovery(str(self.base_path))
        self.active_config_dir: Optional[Path] = None
        self.active_config_file: Optional[str] = None
        self.active_format: Optional[ConfigFormat] = None

        self._initialize_config(layer_name, use_case, config_type, interactive)

    def _initialize_config(
        self,
        layer_name: Optional[str],
        use_case: Optional[str],
        config_type: Optional[str],
        interactive: bool,
    ) -> None:
        """Initialize configuration using discovery or fallback methods."""
        try:
            self._discover_config(layer_name, use_case, config_type, interactive)
        except ConfigurationError:
            logger.info("Auto-discovery failed, trying fallback method")
            self._fallback_config_detection()

    def _discover_config(
        self,
        layer_name: Optional[str],
        use_case: Optional[str],
        config_type: Optional[str],
        interactive: bool,
    ) -> None:
        """Use auto-discovery to find configuration."""
        if interactive:
            config_location = self.discovery.select_interactive()
        else:
            config_location = self.discovery.find_best_match(
                layer_name, use_case, config_type
            )

        if not config_location:
            # Try any discovered config
            discovered = self.discovery.discover()
            if discovered:
                config_location = discovered[0]

        if not config_location:
            raise ConfigurationError("No configuration files found")

        self.active_config_dir, self.active_config_file = config_location
        self._detect_format_from_filename(self.active_config_file)

        logger.info(f"Using config: {self.active_config_dir / self.active_config_file}")

    def _fallback_config_detection(self) -> None:
        """Fallback to original single-directory detection."""
        available = []
        for fmt, filename in self.CONFIG_FILES.items():
            config_path = self.base_path / filename
            if config_path.exists():
                available.append((fmt, filename))

        if not available:
            files = list(self.CONFIG_FILES.values())
            raise ConfigurationError(f"No config found. Expected one of: {files}")

        if len(available) > 1:
            files = [item[1] for item in available]
            raise ConfigurationError(f"Multiple configs found: {files}")

        self.active_format, self.active_config_file = available[0]
        self.active_config_dir = self.base_path

    def _detect_format_from_filename(self, filename: str) -> None:
        """Detect configuration format from filename."""
        if "yml" in filename or "yaml" in filename:
            self.active_format = ConfigFormat.YAML
        elif "json" in filename:
            self.active_format = ConfigFormat.JSON
        elif "dsl" in filename:
            self.active_format = ConfigFormat.DSL
        else:
            self.active_format = ConfigFormat.JSON  # Default

    def get_active_format(self) -> ConfigFormat:
        """Get the active configuration format."""
        if not self.active_format:
            raise ConfigurationError("No active configuration format")
        return self.active_format

    def get_config_file_path(self) -> str:
        """Get full path to active configuration file."""
        if not self.active_config_dir or not self.active_config_file:
            raise ConfigurationError("No active configuration file")
        return str(self.active_config_dir / self.active_config_file)

    def get_config_directory(self) -> Path:
        """Get directory containing active configuration."""
        if not self.active_config_dir:
            raise ConfigurationError("No active configuration directory")
        return self.active_config_dir

    def create_loader(self) -> ConfigLoaderProtocol:
        """Create appropriate configuration loader."""
        if not self.active_format:
            raise ConfigurationError("No active format to create loader")

        loader_class = self.LOADERS[self.active_format]
        return loader_class()

    def change_to_config_directory(self) -> None:
        """Change working directory to configuration directory."""
        if self.active_config_dir and self.active_config_dir != self.original_cwd:
            try:
                validated = SecurityValidator.validate_path(
                    self.original_cwd, self.active_config_dir
                )
                os.chdir(validated)
                logger.info(f"Changed to config directory: {validated}")
            except SecurityError as e:
                if self.active_config_dir.is_absolute() and os.getenv(
                    "TAURO_PERMISSIVE_PATH_VALIDATION", "0"
                ) in ("1", "true", "True", "yes", "YES"):
                    try:
                        os.chdir(self.active_config_dir)
                        logger.warning(
                            f"Changed to absolute config directory (permissive): {self.active_config_dir}"
                        )
                        return
                    except Exception as ex:
                        raise ConfigurationError(f"Failed to change directory: {ex}")
                raise ConfigurationError(f"Failed to change directory: {e}")

    def restore_original_directory(self) -> None:
        """Restore original working directory."""
        try:
            os.chdir(self.original_cwd)
        except OSError:
            pass  # Don't fail if restore unsuccessful


class AppConfigManager:
    """Manages application-level configuration settings."""

    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.settings = self._load_settings()
        self.base_path = Path(self.settings.get("base_path", ""))

    def _load_settings(self) -> Dict[str, Any]:
        """Load and validate settings file."""
        config_path = Path(self.config_file_path)

        if not config_path.exists():
            raise ConfigurationError(
                f"Settings file not found: {self.config_file_path}"
            )

        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in settings: {e}")

        if not isinstance(settings.get("env_config"), dict):
            raise ConfigurationError("Missing or invalid 'env_config' section")

        return settings

    def get_env_config(self, env: str) -> Dict[str, str]:
        """Get configuration paths for specific environment."""
        env = env.lower()
        env_configs = self.settings["env_config"]

        if env not in env_configs:
            available = list(env_configs.keys())
            raise ConfigurationError(
                f"Environment '{env}' not found. Available: {available}"
            )

        base_config = env_configs.get("base", {})
        env_config = env_configs.get(env, {})
        merged = {**base_config, **env_config}

        result = {}
        for key, path in merged.items():
            if path:
                full_path = self.base_path / path
                try:
                    validated = SecurityValidator.validate_path(
                        self.base_path, full_path
                    )
                    result[key] = str(validated)

                    if not validated.exists():
                        logger.warning(f"Config path missing: {validated}")
                except SecurityError as e:
                    logger.error(f"Invalid config path: {e}")
                    result[key] = str(full_path)

        return result
