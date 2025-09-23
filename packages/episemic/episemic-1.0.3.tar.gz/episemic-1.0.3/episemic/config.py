"""Configuration management for Episemic Core."""

from typing import Any

from pydantic import BaseModel, Field


class QdrantConfig(BaseModel):
    """Qdrant vector database configuration."""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "episodic_memories"
    vector_size: int = 768


class DuckDBConfig(BaseModel):
    """DuckDB local database configuration."""
    db_path: str | None = None  # None for in-memory, or path to file
    model_name: str = "all-MiniLM-L6-v2"  # Sentence transformer model


class PostgreSQLConfig(BaseModel):
    """PostgreSQL database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "episemic"
    user: str = "postgres"
    password: str = "postgres"


class RedisConfig(BaseModel):
    """Redis cache configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl: int = 3600  # 1 hour default TTL


class ConsolidationConfig(BaseModel):
    """Memory consolidation configuration."""
    threshold_hours: int = 2
    access_threshold: int = 3
    auto_consolidation_enabled: bool = True
    consolidation_interval_minutes: int = 60


class EpistemicConfig(BaseModel):
    """Main configuration for Episemic Core."""
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    duckdb: DuckDBConfig = Field(default_factory=DuckDBConfig)
    postgresql: PostgreSQLConfig = Field(default_factory=PostgreSQLConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    consolidation: ConsolidationConfig = Field(default_factory=ConsolidationConfig)

    # Storage backend preference
    use_duckdb_fallback: bool = True  # Use DuckDB by default
    prefer_qdrant: bool = False  # Set to True to prefer Qdrant when available

    # Global settings - optimized for DuckDB-only usage by default
    enable_hippocampus: bool = True
    enable_cortex: bool = False  # Disable by default (requires PostgreSQL)
    enable_consolidation: bool = False  # Disable by default (requires cortex)
    enable_retrieval: bool = True

    # Development settings
    debug: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "EpistemicConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)

    @classmethod
    def from_env(cls) -> "EpistemicConfig":
        """Create configuration from environment variables."""
        import os

        config = cls()

        # Qdrant settings
        if os.getenv("QDRANT_HOST"):
            config.qdrant.host = os.getenv("QDRANT_HOST")
        if os.getenv("QDRANT_PORT"):
            config.qdrant.port = int(os.getenv("QDRANT_PORT"))
        if os.getenv("QDRANT_COLLECTION"):
            config.qdrant.collection_name = os.getenv("QDRANT_COLLECTION")

        # DuckDB settings
        if os.getenv("DUCKDB_PATH"):
            config.duckdb.db_path = os.getenv("DUCKDB_PATH")
        if os.getenv("DUCKDB_MODEL"):
            config.duckdb.model_name = os.getenv("DUCKDB_MODEL")

        # Storage backend preferences
        if os.getenv("EPISEMIC_USE_DUCKDB"):
            config.use_duckdb_fallback = os.getenv("EPISEMIC_USE_DUCKDB").lower() in ("true", "1", "yes")
        if os.getenv("EPISEMIC_PREFER_QDRANT"):
            config.prefer_qdrant = os.getenv("EPISEMIC_PREFER_QDRANT").lower() in ("true", "1", "yes")

        # PostgreSQL settings
        if os.getenv("POSTGRES_HOST"):
            config.postgresql.host = os.getenv("POSTGRES_HOST")
        if os.getenv("POSTGRES_PORT"):
            config.postgresql.port = int(os.getenv("POSTGRES_PORT"))
        if os.getenv("POSTGRES_DB"):
            config.postgresql.database = os.getenv("POSTGRES_DB")
        if os.getenv("POSTGRES_USER"):
            config.postgresql.user = os.getenv("POSTGRES_USER")
        if os.getenv("POSTGRES_PASSWORD"):
            config.postgresql.password = os.getenv("POSTGRES_PASSWORD")

        # Redis settings
        if os.getenv("REDIS_HOST"):
            config.redis.host = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            config.redis.port = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_DB"):
            config.redis.db = int(os.getenv("REDIS_DB"))

        # Debug settings
        if os.getenv("EPISEMIC_DEBUG"):
            config.debug = os.getenv("EPISEMIC_DEBUG").lower() in ("true", "1", "yes")
        if os.getenv("EPISEMIC_LOG_LEVEL"):
            config.log_level = os.getenv("EPISEMIC_LOG_LEVEL")

        return config

    def to_dict(self) -> dict[str, Any]:
        """Export configuration to dictionary."""
        return self.model_dump()
