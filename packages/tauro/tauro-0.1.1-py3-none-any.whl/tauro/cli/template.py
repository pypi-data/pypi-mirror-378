import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger  # type: ignore

from .core import ConfigFormat, ExitCode, TauroError

try:
    import yaml  # type: ignore

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class TemplateType(Enum):
    """Available template types (reduced to a single, simple Medallion template)."""

    MEDALLION_BASIC = "medallion_basic"


class TemplateError(TauroError):
    """Exception for template-related errors."""

    def __init__(self, message: str):
        super().__init__(message, ExitCode.CONFIGURATION_ERROR)


class BaseTemplate(ABC):
    """Abstract base class for configuration templates."""

    def __init__(
        self, project_name: str, config_format: ConfigFormat = ConfigFormat.YAML
    ):
        self.project_name = project_name
        self.config_format = config_format
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def get_template_type(self) -> TemplateType:
        """Get the template type."""
        pass

    @abstractmethod
    def generate_global_settings(self) -> Dict[str, Any]:
        """Generate global settings configuration."""
        pass

    @abstractmethod
    def generate_pipelines_config(self) -> Dict[str, Any]:
        """Generate pipelines configuration."""
        pass

    @abstractmethod
    def generate_nodes_config(self) -> Dict[str, Any]:
        """Generate nodes configuration."""
        pass

    @abstractmethod
    def generate_input_config(self) -> Dict[str, Any]:
        """Generate input configuration."""
        pass

    @abstractmethod
    def generate_output_config(self) -> Dict[str, Any]:
        """Generate output configuration."""
        pass

    def generate_settings_json(self) -> Dict[str, Any]:
        """Generate the main settings.json file with environment mappings."""
        file_ext = self._get_file_extension()

        # Include 'pre_prod' to align with CLI environment choices
        return {
            "base_path": ".",
            "env_config": {
                "base": {
                    "global_settings_path": f"config/global_settings{file_ext}",
                    "pipelines_config_path": f"config/pipelines{file_ext}",
                    "nodes_config_path": f"config/nodes{file_ext}",
                    "input_config_path": f"config/input{file_ext}",
                    "output_config_path": f"config/output{file_ext}",
                },
                "dev": {
                    "global_settings_path": f"config/dev/global_settings{file_ext}",
                    "input_config_path": f"config/dev/input{file_ext}",
                    "output_config_path": f"config/dev/output{file_ext}",
                },
                "pre_prod": {
                    "global_settings_path": f"config/pre_prod/global_settings{file_ext}",
                    "input_config_path": f"config/pre_prod/input{file_ext}",
                    "output_config_path": f"config/pre_prod/output{file_ext}",
                },
                "prod": {
                    "global_settings_path": f"config/prod/global_settings{file_ext}",
                    "input_config_path": f"config/prod/input{file_ext}",
                    "output_config_path": f"config/prod/output{file_ext}",
                },
            },
        }

    def _get_file_extension(self) -> str:
        """Get file extension based on config format."""
        if self.config_format == ConfigFormat.YAML:
            return ".yaml"
        elif self.config_format == ConfigFormat.JSON:
            return ".json"
        else:
            return ".dsl"

    def get_common_global_settings(self) -> Dict[str, Any]:
        """Get common global settings for all templates."""
        return {
            "project_name": self.project_name,
            "version": "1.0.0",
            "created_at": self.timestamp,
            "template_type": self.get_template_type().value,
            "architecture": "medallion",
            "layers": ["bronze", "silver", "gold"],
            "mode": "local",  # change to 'databricks' or 'spark' if needed
            "max_parallel_nodes": 4,
            "fail_on_error": True,
        }


class MedallionBasicTemplate(BaseTemplate):
    """Simple Medallion template supporting batch and streaming pipelines."""

    def get_template_type(self) -> TemplateType:
        return TemplateType.MEDALLION_BASIC

    def generate_global_settings(self) -> Dict[str, Any]:
        base_settings = self.get_common_global_settings()
        base_settings.update(
            {
                "default_start_date": "2025-01-01",
                "default_end_date": "2025-12-31",
                "data_root": "data",
                "bronze_path": "data/bronze",
                "silver_path": "data/silver",
                "gold_path": "data/gold",
            }
        )
        return base_settings

    def generate_pipelines_config(self) -> Dict[str, Any]:
        # Batch pipelines and a simple streaming pipeline that lands in Bronze
        return {
            "bronze_batch_ingestion": {
                "description": "Batch ingestion from CSV files to Bronze layer",
                "type": "batch",
                "nodes": ["ingest_sales_data", "ingest_customer_data"],
                "inputs": ["sales_source_csv", "customer_source_csv"],
                "outputs": ["bronze_sales", "bronze_customers"],
            },
            "silver_transform": {
                "description": "Clean and transform Bronze data into Silver",
                "type": "batch",
                "nodes": ["clean_sales_data", "clean_customer_data"],
                "inputs": ["bronze_sales", "bronze_customers"],
                "outputs": ["silver_sales", "silver_customers"],
            },
            "gold_aggregation": {
                "description": "Aggregate data in Gold layer for analytics",
                "type": "batch",
                "nodes": ["aggregate_sales"],
                "inputs": ["silver_sales"],
                "outputs": ["gold_sales_agg"],
            },
            "bronze_streaming_ingestion": {
                "description": "Streaming ingestion from Kafka to Bronze",
                "type": "streaming",
                "nodes": ["stream_from_kafka", "process_stream", "write_stream"],
                "inputs": ["kafka_topic_sales"],
                "outputs": ["bronze_stream"],
            },
        }

    def generate_nodes_config(self) -> Dict[str, Any]:
        # Minimal node definitions with module/function placeholders
        return {
            # Bronze batch
            "ingest_sales_data": {
                "description": "Ingest sales CSV into Bronze",
                "module": "pipelines.bronze.ingestion",
                "function": "ingest_sales_data",
                "input": ["sales_source_csv"],
                "output": ["bronze_sales"],
                "dependencies": [],
            },
            "ingest_customer_data": {
                "description": "Ingest customer CSV into Bronze",
                "module": "pipelines.bronze.ingestion",
                "function": "ingest_customer_data",
                "input": ["customer_source_csv"],
                "output": ["bronze_customers"],
                "dependencies": [],
            },
            # Silver
            "clean_sales_data": {
                "description": "Clean and standardize Bronze sales data",
                "module": "pipelines.silver.transform",
                "function": "clean_sales_data",
                "input": ["bronze_sales"],
                "output": ["silver_sales"],
                "dependencies": ["ingest_sales_data"],
            },
            "clean_customer_data": {
                "description": "Clean and standardize Bronze customer data",
                "module": "pipelines.silver.transform",
                "function": "clean_customer_data",
                "input": ["bronze_customers"],
                "output": ["silver_customers"],
                "dependencies": ["ingest_customer_data"],
            },
            # Gold
            "aggregate_sales": {
                "description": "Aggregate sales for analytics",
                "module": "pipelines.gold.aggregation",
                "function": "aggregate_sales",
                "input": ["silver_sales"],
                "output": ["gold_sales_agg"],
                "dependencies": ["clean_sales_data"],
            },
            # Streaming to Bronze
            "stream_from_kafka": {
                "description": "Read sales events from Kafka",
                "module": "pipelines.bronze.streaming",
                "function": "stream_from_kafka",
                "input": ["kafka_topic_sales"],
                "output": ["raw_stream"],
                "dependencies": [],
            },
            "process_stream": {
                "description": "Parse and filter streaming events",
                "module": "pipelines.bronze.streaming",
                "function": "process_stream",
                "input": ["raw_stream"],
                "output": ["processed_stream"],
                "dependencies": ["stream_from_kafka"],
            },
            "write_stream": {
                "description": "Write streaming data to Bronze (Delta/Parquet)",
                "module": "pipelines.bronze.streaming",
                "function": "write_stream",
                "input": ["processed_stream"],
                "output": ["bronze_stream"],
                "dependencies": ["process_stream"],
            },
        }

    def generate_input_config(self) -> Dict[str, Any]:
        return {
            "sales_source_csv": {
                "description": "Sales CSV input (batch)",
                "format": "csv",
                "filepath": "data/raw/sales/*.csv",
                "options": {"header": True, "inferSchema": True},
            },
            "customer_source_csv": {
                "description": "Customer CSV input (batch)",
                "format": "csv",
                "filepath": "data/raw/customers/*.csv",
                "options": {"header": True, "inferSchema": True},
            },
            "kafka_topic_sales": {
                "description": "Kafka topic for sales events (streaming)",
                "format": "kafka",
                "kafka.bootstrap.servers": "localhost:9092",
                "subscribe": "sales_events",
                "startingOffsets": "latest",
            },
        }

    def generate_output_config(self) -> Dict[str, Any]:
        return {
            # Bronze batch outputs
            "bronze_sales": {
                "description": "Bronze sales table",
                "format": "delta",
                "filepath": "data/bronze/sales",
                "write_mode": "append",
                "vacuum": True,
            },
            "bronze_customers": {
                "description": "Bronze customers table",
                "format": "delta",
                "filepath": "data/bronze/customers",
                "write_mode": "append",
                "vacuum": True,
            },
            # Silver
            "silver_sales": {
                "description": "Silver sales table",
                "format": "delta",
                "filepath": "data/silver/sales",
                "write_mode": "overwrite",
                "vacuum": True,
            },
            "silver_customers": {
                "description": "Silver customers table",
                "format": "delta",
                "filepath": "data/silver/customers",
                "write_mode": "overwrite",
                "vacuum": True,
            },
            # Gold
            "gold_sales_agg": {
                "description": "Gold aggregated sales table",
                "format": "delta",
                "filepath": "data/gold/sales_agg",
                "write_mode": "overwrite",
                "vacuum": True,
            },
            # Streaming sink into Bronze
            "bronze_stream": {
                "description": "Bronze streaming sink (Delta)",
                "format": "delta",
                "filepath": "data/bronze/stream_sales",
                "checkpointLocation": "data/checkpoints/stream_sales",
                "outputMode": "append",
                "trigger": {"processingTime": "10 seconds"},
            },
        }


class TemplateFactory:
    """Factory for creating configuration templates (single option)."""

    TEMPLATES = {
        TemplateType.MEDALLION_BASIC: MedallionBasicTemplate,
    }

    @classmethod
    def create_template(
        cls,
        template_type: TemplateType,
        project_name: str,
        config_format: ConfigFormat = ConfigFormat.YAML,
    ) -> BaseTemplate:
        """Create a template instance."""
        if template_type not in cls.TEMPLATES:
            available = list(cls.TEMPLATES.keys())
            raise TemplateError(
                f"Template type '{template_type.value}' not supported. Available: {[t.value for t in available]}"
            )

        template_class = cls.TEMPLATES[template_type]
        return template_class(project_name, config_format)

    @classmethod
    def list_available_templates(cls) -> List[Dict[str, str]]:
        """List the single available template with a clear description."""
        return [
            {
                "type": TemplateType.MEDALLION_BASIC.value,
                "name": "Medallion (Batch + Streaming)",
                "description": "Simple Medallion architecture with batch and streaming examples (Bronze, Silver, Gold).",
            }
        ]


class TemplateGenerator:
    """Generates complete project templates with directory structure."""

    def __init__(
        self, output_path: Path, config_format: ConfigFormat = ConfigFormat.YAML
    ):
        self.output_path = Path(output_path)
        self.config_format = config_format
        self._file_extension = self._get_file_extension()

    def _get_file_extension(self) -> str:
        """Get file extension based on config format."""
        if self.config_format == ConfigFormat.YAML:
            return ".yaml"
        elif self.config_format == ConfigFormat.JSON:
            return ".json"
        else:
            return ".dsl"

    def _settings_filename(self) -> str:
        """Return settings file name aligned with ConfigDiscovery/ConfigManager expectations."""
        if self.config_format == ConfigFormat.YAML:
            return "settings_yml.json"
        elif self.config_format == ConfigFormat.JSON:
            return "settings_json.json"
        else:
            return "settings_dsl.json"

    def generate_project(
        self,
        template_type: TemplateType,
        project_name: str,
        create_sample_code: bool = True,
    ) -> None:
        """Generate complete project structure from template."""
        logger.info(
            f"Generating {template_type.value} template for project '{project_name}'"
        )

        # Create template instance
        template = TemplateFactory.create_template(
            template_type, project_name, self.config_format
        )

        # Create directory structure
        self._create_directory_structure()

        # Generate configuration files
        self._generate_config_files(template)

        # Generate sample code if requested
        if create_sample_code:
            self._generate_sample_code()

        # Generate additional project files
        self._generate_project_files(template)

        logger.success(
            f"Project '{project_name}' generated successfully at {self.output_path}"
        )

    def _create_directory_structure(self) -> None:
        """Create project directory structure."""
        directories = [
            "config",
            "config/dev",
            "config/pre_prod",
            "config/prod",
            "pipelines",
            "pipelines/bronze",
            "pipelines/silver",
            "pipelines/gold",
            "src",
            "tests",
            "docs",
            "notebooks",
            "data",
            "data/raw",
            "data/bronze",
            "data/silver",
            "data/gold",
            "data/checkpoints",
            "logs",
        ]

        for directory in directories:
            dir_path = self.output_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # Create __init__.py files for Python packages
            if directory.startswith("pipelines") or directory == "src":
                (dir_path / "__init__.py").touch()

    def _generate_config_files(self, template: BaseTemplate) -> None:
        """Generate all configuration files."""
        configs = {
            "global_settings": template.generate_global_settings(),
            "pipelines": template.generate_pipelines_config(),
            "nodes": template.generate_nodes_config(),
            "input": template.generate_input_config(),
            "output": template.generate_output_config(),
        }

        # Generate main settings file
        settings_file = self.output_path / self._settings_filename()
        self._write_json_file(settings_file, template.generate_settings_json())

        # Generate configuration files for each environment
        for env in ["base", "dev", "pre_prod", "prod"]:
            config_dir = self.output_path / "config" / (env if env != "base" else "")

            for config_name, config_data in configs.items():
                # Only generate pipelines/nodes for base environment
                if env != "base" and config_name in ["pipelines", "nodes"]:
                    continue

                file_path = config_dir / f"{config_name}{self._file_extension}"
                self._write_config_file(file_path, config_data)

    def _write_config_file(self, file_path: Path, config_data: Dict[str, Any]) -> None:
        """Write configuration file in the specified format."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if self.config_format == ConfigFormat.YAML:
            self._write_yaml_file(file_path, config_data)
        elif self.config_format == ConfigFormat.JSON:
            self._write_json_file(file_path, config_data)
        else:
            self._write_dsl_file(file_path, config_data)

    def _write_yaml_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Write YAML file."""
        if not HAS_YAML:
            raise TemplateError(
                "PyYAML not available. Install with: pip install PyYAML"
            )

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)

    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Write JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _write_dsl_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Write DSL file using [section] and [parent.child] headers."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Configuration file generated on {datetime.now()}\n\n")
            for top_key, top_val in data.items():
                if isinstance(top_val, dict):
                    self._write_dsl_sections(f, [top_key], top_val)
                else:
                    f.write(f"{top_key} = {self._fmt_dsl_value(top_val)}\n")

    def _write_dsl_sections(self, f, path: List[str], obj: Dict[str, Any]) -> None:
        """Escribe una sección [a.b.c] y sus claves escalares, luego recurre por sub-dicts."""
        section_name = ".".join(path)
        f.write(f"[{section_name}]\n")
        nested_items: List[tuple[str, Any]] = []
        for k, v in obj.items():
            if isinstance(v, dict):
                nested_items.append((k, v))
            else:
                f.write(f"{k} = {self._fmt_dsl_value(v)}\n")
        f.write("\n")
        for k, v in nested_items:
            self._write_dsl_sections(f, path + [k], v)

    def _fmt_dsl_value(self, v: Any) -> str:
        """Formatea valores para DSL (strings con comillas, bool en minúsculas, listas con elementos formateados)."""
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            items = ", ".join(self._fmt_dsl_value(x) for x in v)
            return f"[{items}]"
        if isinstance(v, dict):
            return json.dumps(v, ensure_ascii=False)
        s = str(v).replace('"', '\\"')
        return f'"{s}"'

    def _generate_sample_code(self) -> None:
        """Generate minimal sample Python code for batch and streaming."""
        # Bronze batch ingestion
        bronze_ingestion_code = '''"""Bronze layer batch ingestion functions."""
from loguru import logger

def ingest_sales_data(start_date: str, end_date: str):
    """Ingest raw sales data (CSV) into Bronze."""
    logger.info(f"Ingesting sales from {start_date} to {end_date}")
    # TODO: implement reading CSV and writing to Bronze (Delta/Parquet)
    pass

def ingest_customer_data(start_date: str, end_date: str):
    """Ingest raw customer data (CSV) into Bronze."""
    logger.info(f"Ingesting customers from {start_date} to {end_date}")
    # TODO: implement reading CSV and writing to Bronze (Delta/Parquet)
    pass
'''
        bronze_ingestion_file = (
            self.output_path / "pipelines" / "bronze" / "ingestion.py"
        )
        self._write_text_file(bronze_ingestion_file, bronze_ingestion_code)

        # Silver transformations
        silver_transform_code = '''"""Silver layer transformation functions."""
from loguru import logger

def clean_sales_data(start_date: str, end_date: str):
    """Clean and standardize Bronze sales data into Silver."""
    logger.info(f"Cleaning sales from {start_date} to {end_date}")
    # TODO: implement transformations and write to Silver
    pass

def clean_customer_data(start_date: str, end_date: str):
    """Clean and standardize Bronze customer data into Silver."""
    logger.info(f"Cleaning customers from {start_date} to {end_date}")
    # TODO: implement transformations and write to Silver
    pass
'''
        silver_transform_file = (
            self.output_path / "pipelines" / "silver" / "transform.py"
        )
        self._write_text_file(silver_transform_file, silver_transform_code)

        # Gold aggregations
        gold_aggregation_code = '''"""Gold layer aggregation functions."""
from loguru import logger

def aggregate_sales(start_date: str, end_date: str):
    """Aggregate Silver sales for analytics into Gold."""
    logger.info(f"Aggregating sales from {start_date} to {end_date}")
    # TODO: implement aggregations and write to Gold
    pass
'''
        gold_aggregation_file = (
            self.output_path / "pipelines" / "gold" / "aggregation.py"
        )
        self._write_text_file(gold_aggregation_file, gold_aggregation_code)

        # Streaming ingestion into Bronze
        bronze_streaming_code = '''"""Bronze layer streaming ingestion functions."""
from loguru import logger

def stream_from_kafka():
    """Read events from Kafka (source)."""
    logger.info("Starting Kafka source stream")
    # TODO: implement Kafka source creation
    return None

def process_stream(raw_stream=None):
    """Parse/filter streaming events."""
    logger.info("Processing streaming data")
    # TODO: implement streaming transformations
    return None

def write_stream(processed_stream=None):
    """Write streaming data to Bronze (Delta/Parquet) with checkpoints."""
    logger.info("Writing streaming data to Bronze")
    # TODO: implement sink with checkpointing
    pass
'''
        bronze_streaming_file = (
            self.output_path / "pipelines" / "bronze" / "streaming.py"
        )
        self._write_text_file(bronze_streaming_file, bronze_streaming_code)

    def _generate_project_files(self, template: BaseTemplate) -> None:
        """Generate additional project files."""
        # README.md
        readme_content = f"""# {template.project_name}

Generated using Tauro {template.get_template_type().value} template.

## What you get

- Medallion architecture (Bronze, Silver, Gold)
- Batch pipelines:
  - bronze_batch_ingestion
  - silver_transform
  - gold_aggregation
- Streaming pipeline:
  - bronze_streaming_ingestion (Kafka -> Bronze)

## Quick start

1. Install dependencies:
   pip install -r requirements.txt

2. Inspect and adjust config files under ./config and settings_*.json

3. Run a batch pipeline:
   tauro --env dev --pipeline bronze_batch_ingestion

4. Run streaming (from streaming CLI):
   tauro --streaming --streaming-command run --streaming-config ./settings_json.json --streaming-pipeline bronze_streaming_ingestion

Generated on: {template.timestamp}
"""
        readme_file = self.output_path / "README.md"
        # Use 4 backticks escaping for Markdown outside this function when needed by the platform
        self._write_text_file(readme_file, readme_content)

        # requirements.txt (minimal)
        requirements = """# Tauro framework (core CLI integration)
tauro-framework>=0.1.0

# Data processing (choose what you need)
pyspark>=3.4.0
pandas>=1.5.0

# Optional: Delta Lake for tables
delta-spark>=2.4.0

# Streaming (Kafka)
kafka-python>=2.0.2

# Utilities
loguru>=0.7.0
pyyaml>=6.0
"""
        requirements_file = self.output_path / "requirements.txt"
        self._write_text_file(requirements_file, requirements)

        # .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
env/
venv/

# Data
data/raw/*
data/bronze/*
data/silver/*
data/gold/*
!data/raw/.gitkeep

# Logs
logs/*.log

# Notebooks checkpoints
.ipynb_checkpoints/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Spark
metastore_db/
spark-warehouse/
"""
        gitignore_file = self.output_path / ".gitignore"
        self._write_text_file(gitignore_file, gitignore)

    def _write_text_file(self, file_path: Path, content: str) -> None:
        """Write text file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


TEMPLATE_GENERATION_CANCELLED = "Template generation cancelled"


class TemplateCommand:
    """Handles the --template command functionality."""

    def __init__(self):
        self.generator = None

    def handle_template_command(
        self,
        template_type: Optional[str] = None,
        project_name: Optional[str] = None,
        output_path: Optional[str] = None,
        config_format: str = "yaml",
        create_sample_code: bool = True,
        list_templates: bool = False,
        interactive: bool = False,
    ) -> int:
        """Handle template generation command."""
        try:
            if list_templates:
                return self._list_templates()

            if interactive:
                return self._interactive_generation()

            if not template_type or not project_name:
                logger.error("Template type and project name are required")
                logger.info("Use --list-templates to see available templates")
                return ExitCode.VALIDATION_ERROR.value

            return self._generate_template(
                template_type,
                project_name,
                output_path,
                config_format,
                create_sample_code,
            )

        except TemplateError as e:
            logger.error(f"Template error: {e}")
            return e.exit_code.value
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ExitCode.GENERAL_ERROR.value

    def _list_templates(self) -> int:
        """List all available templates."""
        templates = TemplateFactory.list_available_templates()

        logger.info("Available template types:")
        for template in templates:
            logger.info(f"  {template['type']:20} - {template['name']}")
            logger.info(f"  {' ' * 20}   {template['description']}")
            logger.info("")

        logger.info("Usage:")
        logger.info("  tauro --template <type> --project-name <name> [options]")
        logger.info("")
        logger.info("Examples:")
        logger.info("  tauro --template medallion_basic --project-name my_pipeline")
        logger.info(
            "  tauro --template medallion_basic --project-name my_pipeline --format json"
        )

        return ExitCode.SUCCESS.value

    def _interactive_generation(self) -> int:
        """Interactive template generation."""
        try:
            # Select template type
            templates = TemplateFactory.list_available_templates()

            print("\nAvailable templates:")
            for i, template in enumerate(templates, 1):
                print(f"  {i}. {template['name']} - {template['description']}")

            while True:
                try:
                    choice = input(f"\nSelect template (1-{len(templates)}): ").strip()
                    if choice.isdigit():
                        index = int(choice) - 1
                        if 0 <= index < len(templates):
                            selected_template = templates[index]
                            break
                    # Invalid selection -> prompt again
                    print(
                        "Invalid selection. Please try again or press Ctrl+C to cancel."
                    )
                    continue
                except (KeyboardInterrupt, EOFError):
                    logger.info("Template generation cancelled")
                    return ExitCode.GENERAL_ERROR.value

            # Get project name
            project_name = input("Enter project name: ").strip()
            if not project_name:
                logger.error("Project name cannot be empty")
                return ExitCode.VALIDATION_ERROR.value

            # Get output path
            default_output = f"./{project_name}"
            output_path = input(f"Output path (default: {default_output}): ").strip()
            if not output_path:
                output_path = default_output

            # Get config format
            formats = ["yaml", "json", "dsl"]
            print(f"\nConfig formats: {', '.join(formats)}")
            config_format = input("Config format (default: yaml): ").strip().lower()
            if not config_format:
                config_format = "yaml"
            elif config_format not in formats:
                logger.error(f"Invalid format. Use one of: {', '.join(formats)}")
                return ExitCode.VALIDATION_ERROR.value

            # Generate sample code
            create_code = input("Generate sample code? (Y/n): ").strip().lower()
            create_sample_code = create_code != "n"

            return self._generate_template(
                selected_template["type"],
                project_name,
                output_path,
                config_format,
                create_sample_code,
            )

        except Exception as e:
            logger.error(f"Interactive generation failed: {e}")
            return ExitCode.GENERAL_ERROR.value

    def _generate_template(
        self,
        template_type: str,
        project_name: str,
        output_path: Optional[str],
        config_format: str,
        create_sample_code: bool,
    ) -> int:
        """Generate template with specified parameters."""
        try:
            # Validate template type
            try:
                template_enum = TemplateType(template_type)
            except ValueError:
                available = [t.value for t in TemplateType]
                logger.error(f"Invalid template type: {template_type}")
                logger.info(f"Available types: {', '.join(available)}")
                return ExitCode.VALIDATION_ERROR.value

            # Validate config format
            try:
                format_enum = ConfigFormat(config_format)
            except ValueError:
                available = [f.value for f in ConfigFormat]
                logger.error(f"Invalid config format: {config_format}")
                logger.info(f"Available formats: {', '.join(available)}")
                return ExitCode.VALIDATION_ERROR.value

            # Set default output path
            if not output_path:
                output_path = f"./{project_name}"

            output_dir = Path(output_path)

            # Check if directory exists
            if output_dir.exists() and any(output_dir.iterdir()):
                logger.warning(
                    f"Directory {output_dir} already exists and is not empty"
                )
                logger.info("Template generation cancelled")
                return ExitCode.VALIDATION_ERROR.value

            # Generate template
            self.generator = TemplateGenerator(output_dir, format_enum)
            self.generator.generate_project(
                template_enum, project_name, create_sample_code
            )

            # Show success message with next steps
            self._show_success_message(project_name, output_dir, template_enum)

            return ExitCode.SUCCESS.value

        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            return ExitCode.GENERAL_ERROR.value

    def _show_success_message(
        self, project_name: str, output_dir: Path, template_type: TemplateType
    ) -> None:
        """Show success message with next steps."""
        logger.success(f"✅ Project '{project_name}' created successfully!")
        logger.info(f"📁 Location: {output_dir.absolute()}")
        logger.info(f"🏗️  Template: {template_type.value}")

        logger.info("\n📋 Next steps:")
        logger.info(f"1. cd {output_dir}")
        logger.info("2. pip install -r requirements.txt")
        logger.info("3. Review and customize configuration files under ./config")
        logger.info("4. Implement pipeline functions in the pipelines/ directory")

        logger.info("\n🚀 Example usage (batch):")
        logger.info("   tauro --env dev --pipeline bronze_batch_ingestion")
        logger.info("   tauro --env dev --pipeline silver_transform")
        logger.info("   tauro --env dev --pipeline gold_aggregation")

        logger.info("\n🟢 Example usage (streaming):")
        logger.info(
            "   tauro --streaming --streaming-command run --streaming-config ./settings_json.json --streaming-pipeline bronze_streaming_ingestion"
        )


# Integration with CLI system
def add_template_arguments(parser) -> None:
    """Add template-related arguments to CLI parser."""
    template_group = parser.add_argument_group("Template Generation")

    template_group.add_argument(
        "--template",
        help="Generate project template (use --list-templates to see options)",
    )

    template_group.add_argument("--project-name", help="Name for the generated project")

    template_group.add_argument(
        "--output-path",
        help="Output directory for generated project (default: ./<project-name>)",
    )

    template_group.add_argument(
        "--format",
        choices=["yaml", "json", "dsl"],
        default="yaml",
        help="Configuration file format (default: yaml)",
    )

    template_group.add_argument(
        "--no-sample-code",
        action="store_true",
        help="Skip generation of sample code files",
    )

    template_group.add_argument(
        "--list-templates", action="store_true", help="List available template types"
    )

    template_group.add_argument(
        "--template-interactive",
        action="store_true",
        help="Interactive template generation",
    )


def handle_template_command(parsed_args) -> int:
    """Handle template command execution from CLI."""
    template_cmd = TemplateCommand()

    return template_cmd.handle_template_command(
        template_type=parsed_args.template,
        project_name=parsed_args.project_name,
        output_path=parsed_args.output_path,
        config_format=parsed_args.format,
        create_sample_code=not parsed_args.no_sample_code,
        list_templates=parsed_args.list_templates,
    )
