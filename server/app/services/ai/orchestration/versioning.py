"""Model versioning and management system."""

import os
import json
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import hashlib
import logging
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ModelVersion(BaseModel):
    """Represents a specific version of a model."""
    model_name: str
    version: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    path: str
    size_bytes: int
    checksum: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True
    performance_metrics: Optional[Dict[str, float]] = None


class ModelRegistry(BaseModel):
    """Registry of all models and their versions."""
    models: Dict[str, List[ModelVersion]] = Field(default_factory=dict)
    default_versions: Dict[str, str] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelVersionManager:
    """Manages model versions and lifecycle."""
    
    def __init__(self, registry_path: str):
        """Initialize model version manager."""
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.registry_path / "registry.json"
        self.models_dir = self.registry_path / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        self.registry = self._load_registry()
    
    def _load_registry(self) -> ModelRegistry:
        """Load model registry from disk."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                return ModelRegistry(**data)
            except Exception as e:
                logger.error(f"Failed to load registry: {str(e)}")
        
        return ModelRegistry()
    
    def _save_registry(self) -> None:
        """Save model registry to disk."""
        self.registry.updated_at = datetime.utcnow()
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry.dict(), f, indent=2, default=str)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def register_model(self, 
                      model_name: str,
                      version: str,
                      model_path: str,
                      metadata: Optional[Dict[str, Any]] = None,
                      tags: Optional[List[str]] = None,
                      set_as_default: bool = False) -> ModelVersion:
        """Register a new model version."""
        # Validate inputs
        source_path = Path(model_path)
        if not source_path.exists():
            raise ValueError(f"Model file not found: {model_path}")
        
        # Check if version already exists
        if model_name in self.registry.models:
            existing_versions = [v.version for v in self.registry.models[model_name]]
            if version in existing_versions:
                raise ValueError(f"Version {version} already exists for model {model_name}")
        
        # Create model directory
        model_dir = self.models_dir / model_name / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model file
        if source_path.is_file():
            dest_path = model_dir / source_path.name
            shutil.copy2(source_path, dest_path)
        else:
            # Copy entire directory
            dest_path = model_dir / source_path.name
            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
        
        # Calculate checksum and size
        if dest_path.is_file():
            checksum = self._calculate_checksum(dest_path)
            size_bytes = dest_path.stat().st_size
        else:
            # For directories, calculate combined checksum
            checksums = []
            size_bytes = 0
            for file_path in dest_path.rglob("*"):
                if file_path.is_file():
                    checksums.append(self._calculate_checksum(file_path))
                    size_bytes += file_path.stat().st_size
            checksum = hashlib.sha256("".join(sorted(checksums)).encode()).hexdigest()
        
        # Create model version
        model_version = ModelVersion(
            model_name=model_name,
            version=version,
            created_at=datetime.utcnow(),
            path=str(dest_path),
            size_bytes=size_bytes,
            checksum=checksum,
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Add to registry
        if model_name not in self.registry.models:
            self.registry.models[model_name] = []
        self.registry.models[model_name].append(model_version)
        
        # Set as default if requested or if it's the first version
        if set_as_default or model_name not in self.registry.default_versions:
            self.registry.default_versions[model_name] = version
        
        # Save registry
        self._save_registry()
        
        logger.info(f"Registered model: {model_name} v{version}")
        return model_version
    
    def get_model_version(self, model_name: str, version: Optional[str] = None) -> Optional[ModelVersion]:
        """Get a specific model version."""
        if model_name not in self.registry.models:
            return None
        
        # Use default version if not specified
        if version is None:
            version = self.registry.default_versions.get(model_name)
            if version is None:
                return None
        
        # Find specific version
        for model_version in self.registry.models[model_name]:
            if model_version.version == version and model_version.is_active:
                return model_version
        
        return None
    
    def list_models(self) -> List[str]:
        """List all registered models."""
        return list(self.registry.models.keys())
    
    def list_versions(self, model_name: str) -> List[ModelVersion]:
        """List all versions of a model."""
        return self.registry.models.get(model_name, [])
    
    def get_latest_version(self, model_name: str) -> Optional[ModelVersion]:
        """Get the latest version of a model."""
        versions = self.registry.models.get(model_name, [])
        if not versions:
            return None
        
        # Sort by creation date
        active_versions = [v for v in versions if v.is_active]
        if not active_versions:
            return None
        
        return max(active_versions, key=lambda v: v.created_at)
    
    def set_default_version(self, model_name: str, version: str) -> bool:
        """Set the default version for a model."""
        model_version = self.get_model_version(model_name, version)
        if not model_version:
            return False
        
        self.registry.default_versions[model_name] = version
        self._save_registry()
        
        logger.info(f"Set default version for {model_name}: {version}")
        return True
    
    def update_model_metadata(self, 
                            model_name: str,
                            version: str,
                            metadata: Dict[str, Any]) -> bool:
        """Update metadata for a model version."""
        if model_name not in self.registry.models:
            return False
        
        for model_version in self.registry.models[model_name]:
            if model_version.version == version:
                model_version.metadata.update(metadata)
                model_version.updated_at = datetime.utcnow()
                self._save_registry()
                return True
        
        return False
    
    def update_performance_metrics(self,
                                 model_name: str,
                                 version: str,
                                 metrics: Dict[str, float]) -> bool:
        """Update performance metrics for a model version."""
        if model_name not in self.registry.models:
            return False
        
        for model_version in self.registry.models[model_name]:
            if model_version.version == version:
                if model_version.performance_metrics is None:
                    model_version.performance_metrics = {}
                model_version.performance_metrics.update(metrics)
                model_version.updated_at = datetime.utcnow()
                self._save_registry()
                return True
        
        return False
    
    def add_tags(self, model_name: str, version: str, tags: List[str]) -> bool:
        """Add tags to a model version."""
        if model_name not in self.registry.models:
            return False
        
        for model_version in self.registry.models[model_name]:
            if model_version.version == version:
                model_version.tags.extend(tags)
                model_version.tags = list(set(model_version.tags))  # Remove duplicates
                model_version.updated_at = datetime.utcnow()
                self._save_registry()
                return True
        
        return False
    
    def deactivate_version(self, model_name: str, version: str) -> bool:
        """Deactivate a model version (soft delete)."""
        if model_name not in self.registry.models:
            return False
        
        for model_version in self.registry.models[model_name]:
            if model_version.version == version:
                model_version.is_active = False
                model_version.updated_at = datetime.utcnow()
                
                # If this was the default, set a new default
                if self.registry.default_versions.get(model_name) == version:
                    latest = self.get_latest_version(model_name)
                    if latest:
                        self.registry.default_versions[model_name] = latest.version
                    else:
                        del self.registry.default_versions[model_name]
                
                self._save_registry()
                logger.info(f"Deactivated model version: {model_name} v{version}")
                return True
        
        return False
    
    def delete_version(self, model_name: str, version: str, force: bool = False) -> bool:
        """Delete a model version (hard delete)."""
        if not force:
            # First deactivate
            if not self.deactivate_version(model_name, version):
                return False
        
        # Find and remove version
        if model_name not in self.registry.models:
            return False
        
        model_version = None
        for i, v in enumerate(self.registry.models[model_name]):
            if v.version == version:
                model_version = self.registry.models[model_name].pop(i)
                break
        
        if not model_version:
            return False
        
        # Delete files
        model_path = Path(model_version.path)
        if model_path.exists():
            if model_path.is_file():
                model_path.unlink()
            else:
                shutil.rmtree(model_path)
        
        # Clean up empty directories
        version_dir = model_path.parent
        if version_dir.exists() and not any(version_dir.iterdir()):
            version_dir.rmdir()
        
        # Remove model entry if no versions left
        if not self.registry.models[model_name]:
            del self.registry.models[model_name]
            if model_name in self.registry.default_versions:
                del self.registry.default_versions[model_name]
        
        self._save_registry()
        logger.info(f"Deleted model version: {model_name} v{version}")
        return True
    
    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions of a model."""
        v1 = self.get_model_version(model_name, version1)
        v2 = self.get_model_version(model_name, version2)
        
        if not v1 or not v2:
            return {"error": "One or both versions not found"}
        
        comparison = {
            "model_name": model_name,
            "versions": {
                "v1": version1,
                "v2": version2
            },
            "created_at": {
                "v1": v1.created_at,
                "v2": v2.created_at,
                "difference_days": (v2.created_at - v1.created_at).days
            },
            "size": {
                "v1": v1.size_bytes,
                "v2": v2.size_bytes,
                "difference": v2.size_bytes - v1.size_bytes,
                "percentage_change": ((v2.size_bytes - v1.size_bytes) / v1.size_bytes) * 100 if v1.size_bytes > 0 else 0
            },
            "checksum_changed": v1.checksum != v2.checksum,
            "metadata_diff": self._compare_dicts(v1.metadata, v2.metadata),
            "tags_diff": {
                "added": list(set(v2.tags) - set(v1.tags)),
                "removed": list(set(v1.tags) - set(v2.tags)),
                "common": list(set(v1.tags) & set(v2.tags))
            }
        }
        
        # Compare performance metrics if available
        if v1.performance_metrics and v2.performance_metrics:
            metrics_comparison = {}
            all_metrics = set(v1.performance_metrics.keys()) | set(v2.performance_metrics.keys())
            
            for metric in all_metrics:
                m1 = v1.performance_metrics.get(metric)
                m2 = v2.performance_metrics.get(metric)
                
                if m1 is not None and m2 is not None:
                    metrics_comparison[metric] = {
                        "v1": m1,
                        "v2": m2,
                        "difference": m2 - m1,
                        "percentage_change": ((m2 - m1) / m1) * 100 if m1 != 0 else 0
                    }
                elif m1 is not None:
                    metrics_comparison[metric] = {"v1": m1, "v2": None}
                else:
                    metrics_comparison[metric] = {"v1": None, "v2": m2}
            
            comparison["performance_metrics"] = metrics_comparison
        
        return comparison
    
    def _compare_dicts(self, d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two dictionaries and return differences."""
        all_keys = set(d1.keys()) | set(d2.keys())
        diff = {
            "added": {},
            "removed": {},
            "changed": {}
        }
        
        for key in all_keys:
            if key in d1 and key not in d2:
                diff["removed"][key] = d1[key]
            elif key not in d1 and key in d2:
                diff["added"][key] = d2[key]
            elif d1.get(key) != d2.get(key):
                diff["changed"][key] = {"from": d1[key], "to": d2[key]}
        
        return diff
    
    def export_registry(self, export_path: str) -> None:
        """Export the entire registry to a file."""
        with open(export_path, 'w') as f:
            json.dump(self.registry.dict(), f, indent=2, default=str)
    
    def import_registry(self, import_path: str, merge: bool = False) -> None:
        """Import a registry from a file."""
        with open(import_path, 'r') as f:
            data = json.load(f)
        
        imported_registry = ModelRegistry(**data)
        
        if merge:
            # Merge with existing registry
            for model_name, versions in imported_registry.models.items():
                if model_name not in self.registry.models:
                    self.registry.models[model_name] = []
                
                # Add non-duplicate versions
                existing_versions = {v.version for v in self.registry.models[model_name]}
                for version in versions:
                    if version.version not in existing_versions:
                        self.registry.models[model_name].append(version)
            
            # Update default versions
            self.registry.default_versions.update(imported_registry.default_versions)
        else:
            # Replace entire registry
            self.registry = imported_registry
        
        self._save_registry()