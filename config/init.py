"""Configuration loader for Math RAG system."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class Config:
    """System configuration dataclass."""
    
    # API Keys
    groq_api_key: str
    hf_token: Optional[str]
    
    # Models
    groq_model: str
    embedding_model: str
    embedding_dimension: int
    
    # Paths
    data_dir: Path
    raw_pdf_dir: Path
    processed_dir: Path
    images_dir: Path
    tables_dir: Path
    vector_db_path: Path
    metadata_db_path: Path
    log_file: Path
    
    # Processing
    min_chunk_size: int
    max_chunk_size: int
    chunk_overlap: int
    top_k: int
    similarity_threshold: float
    log_level: str
    
    # YAML Config
    yaml_config: Dict[str, Any]


class ConfigLoader:
    """Load and manage system configuration."""
    
    def __init__(self, config_path: str = "config/config.yaml", env_path: str = ".env"):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to YAML config file
            env_path: Path to .env file
        """
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / config_path
        self.env_path = self.project_root / env_path
        
        # Load environment variables
        load_dotenv(self.env_path)
        
        # Load YAML config
        self.yaml_config = self._load_yaml()
        
        # Create config object
        self.config = self._create_config()
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_config(self) -> Config:
        """Create Config object from environment and YAML."""
        data_dir = Path(os.getenv('DATA_DIR', './data'))
        
        return Config(
            # API Keys
            groq_api_key=os.getenv('GROQ_API_KEY', ''),
            hf_token=os.getenv('HF_TOKEN'),
            
            # Models
            groq_model=os.getenv('GROQ_MODEL', self.yaml_config.get('system', {}).get('llm_model', 'llama-3.3-70b-versatile')),
            embedding_model=os.getenv('EMBEDDING_MODEL', 'BAAI/bge-large-en-v1.5'),
            embedding_dimension=int(os.getenv('EMBEDDING_DIMENSION', '1024')),
            
            # Paths
            data_dir=data_dir,
            raw_pdf_dir=Path(os.getenv('RAW_PDF_DIR', './data/raw')),
            processed_dir=Path(os.getenv('PROCESSED_DIR', './data/processed')),
            images_dir=Path(os.getenv('IMAGES_DIR', './data/images')),
            tables_dir=Path(os.getenv('TABLES_DIR', './data/tables')),
            vector_db_path=Path(os.getenv('VECTOR_DB_PATH', './data/vector_store')),
            metadata_db_path=Path(os.getenv('METADATA_DB_PATH', './data/metadata.json')),
            log_file=Path(os.getenv('LOG_FILE', './logs/math_rag.log')),
            
            # Processing
            min_chunk_size=int(os.getenv('MIN_CHUNK_SIZE', '200')),
            max_chunk_size=int(os.getenv('MAX_CHUNK_SIZE', '800')),
            chunk_overlap=int(os.getenv('CHUNK_OVERLAP', '50')),
            top_k=int(os.getenv('TOP_K', '5')),
            similarity_threshold=float(os.getenv('SIMILARITY_THRESHOLD', self.yaml_config.get('system', {}).get('similarity_threshold', 0.5))),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            
            # YAML Config
            yaml_config=self.yaml_config
        )
    
    def get(self) -> Config:
        """Get configuration object."""
        return self.config
    
    def get_yaml_section(self, section: str) -> Dict[str, Any]:
        """Get specific section from YAML config."""
        return self.yaml_config.get(section, {})


# Global config instance
_config_loader: Optional[ConfigLoader] = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.get()


def get_yaml_config(section: str) -> Dict[str, Any]:
    """Get YAML configuration section."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.get_yaml_section(section)