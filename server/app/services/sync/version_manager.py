"""
Data Versioning and Merging System

Manages data versions, tracks changes, and provides merging capabilities:
- Version creation and management
- Change tracking and metadata
- Version comparison and diffing
- Automatic and manual merge operations
- Branch management for complex scenarios
- Version history and lineage tracking
"""

import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from datetime import datetime, timedelta
import copy
import pickle
import zlib

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes that can be tracked"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    COPY = "copy"
    MERGE = "merge"


class MergeType(Enum):
    """Types of merge operations"""
    FAST_FORWARD = "fast_forward"
    THREE_WAY = "three_way"
    RECURSIVE = "recursive"
    MANUAL = "manual"


@dataclass
class FieldChange:
    """Represents a change to a specific field"""
    field_path: str
    change_type: ChangeType
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=time.time)
    author: str = ""
    device_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Version:
    """Represents a version of data"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    entity_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    parent_versions: List[str] = field(default_factory=list)
    changes: List[FieldChange] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    author: str = ""
    device_id: str = ""
    checksum: str = ""
    compressed_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
            
    def _calculate_checksum(self) -> str:
        """Calculate checksum for the version data"""
        data_str = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass 
class Branch:
    """Represents a branch in version history"""
    name: str
    head_version: str
    created_at: float = field(default_factory=time.time)
    created_by: str = ""
    description: str = ""
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MergeOperation:
    """Represents a merge operation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_versions: List[str] = field(default_factory=list)
    target_version: str = ""
    result_version: str = ""
    merge_type: MergeType = MergeType.THREE_WAY
    conflicts: List[str] = field(default_factory=list)  # conflict IDs
    timestamp: float = field(default_factory=time.time)
    author: str = ""
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class VersionManager:
    """
    Comprehensive data versioning and merging system
    
    Features:
    - Version creation and management
    - Change tracking with detailed metadata
    - Version comparison and diffing
    - Multiple merge strategies
    - Branch management
    - Version history and lineage
    - Compression for storage efficiency
    - Conflict detection and resolution integration
    """
    
    def __init__(self, storage_backend=None, enable_compression=True):
        self.storage_backend = storage_backend
        self.enable_compression = enable_compression
        
        # Version storage
        self.versions: Dict[str, Version] = {}
        self.entity_versions: Dict[str, Dict[str, List[str]]] = {}  # entity_type -> entity_id -> version_ids
        
        # Branch management
        self.branches: Dict[str, Dict[str, Branch]] = {}  # entity_type:entity_id -> branch_name -> Branch
        
        # Merge history
        self.merge_operations: List[MergeOperation] = []
        
        # Change listeners
        self.change_listeners: List[callable] = []
        
        # Statistics
        self.stats = {
            'versions_created': 0,
            'merges_performed': 0,
            'conflicts_detected': 0,
            'storage_size_bytes': 0,
            'compression_ratio': 0.0
        }
        
    async def create_version(self,
                           entity_type: str,
                           entity_id: str,
                           data: Dict[str, Any],
                           parent_versions: List[str] = None,
                           author: str = "",
                           device_id: str = "",
                           changes: List[FieldChange] = None,
                           metadata: Dict[str, Any] = None) -> Version:
        """Create a new version of data"""
        
        # Create version object
        version = Version(
            entity_type=entity_type,
            entity_id=entity_id,
            data=copy.deepcopy(data),
            parent_versions=parent_versions or [],
            changes=changes or [],
            author=author,
            device_id=device_id,
            metadata=metadata or {}
        )
        
        # Compress data if enabled
        if self.enable_compression:
            version.compressed_data = self._compress_data(data)
            
        # Store version
        self.versions[version.id] = version
        
        # Update entity version tracking
        if entity_type not in self.entity_versions:
            self.entity_versions[entity_type] = {}
        if entity_id not in self.entity_versions[entity_type]:
            self.entity_versions[entity_type][entity_id] = []
            
        self.entity_versions[entity_type][entity_id].append(version.id)
        
        # Update statistics
        self.stats['versions_created'] += 1
        self._update_storage_stats()
        
        # Notify listeners
        await self._notify_change_listeners('version_created', version)
        
        # Save to storage backend if available
        if self.storage_backend:
            await self.storage_backend.save_version(version)
            
        logger.info(f"Created version {version.id} for {entity_type}:{entity_id}")
        
        return version
        
    async def get_version(self, version_id: str) -> Optional[Version]:
        """Get a specific version by ID"""
        version = self.versions.get(version_id)
        
        if not version and self.storage_backend:
            # Try to load from storage
            version = await self.storage_backend.load_version(version_id)
            if version:
                self.versions[version_id] = version
                
        return version
        
    async def get_latest_version(self, entity_type: str, entity_id: str, branch: str = "main") -> Optional[Version]:
        """Get the latest version for an entity"""
        
        # Check if branch exists
        entity_key = f"{entity_type}:{entity_id}"
        if entity_key in self.branches and branch in self.branches[entity_key]:
            head_version_id = self.branches[entity_key][branch].head_version
            return await self.get_version(head_version_id)
            
        # Fallback to latest version in entity_versions
        if entity_type in self.entity_versions and entity_id in self.entity_versions[entity_type]:
            version_ids = self.entity_versions[entity_type][entity_id]
            if version_ids:
                latest_version_id = version_ids[-1]
                return await self.get_version(latest_version_id)
                
        return None
        
    async def get_version_history(self, 
                                entity_type: str, 
                                entity_id: str,
                                limit: int = None,
                                since: datetime = None) -> List[Version]:
        """Get version history for an entity"""
        
        if entity_type not in self.entity_versions or entity_id not in self.entity_versions[entity_type]:
            return []
            
        version_ids = self.entity_versions[entity_type][entity_id]
        versions = []
        
        for version_id in version_ids:
            version = await self.get_version(version_id)
            if version:
                # Apply filters
                if since and datetime.fromtimestamp(version.timestamp) < since:
                    continue
                    
                versions.append(version)
                
                # Apply limit
                if limit and len(versions) >= limit:
                    break
                    
        return versions
        
    async def compare_versions(self, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """Compare two versions and return differences"""
        
        version1 = await self.get_version(version1_id)
        version2 = await self.get_version(version2_id)
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
            
        # Calculate differences
        differences = self._calculate_diff(version1.data, version2.data)
        
        return {
            'version1': {
                'id': version1.id,
                'timestamp': version1.timestamp,
                'author': version1.author,
                'checksum': version1.checksum
            },
            'version2': {
                'id': version2.id,
                'timestamp': version2.timestamp,
                'author': version2.author,
                'checksum': version2.checksum
            },
            'differences': differences,
            'is_identical': len(differences) == 0
        }
        
    def _calculate_diff(self, data1: Dict[str, Any], data2: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
        """Calculate differences between two data objects"""
        differences = []
        
        # Get all keys from both objects
        all_keys = set(data1.keys()) | set(data2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            value1 = data1.get(key)
            value2 = data2.get(key)
            
            if key not in data1:
                differences.append({
                    'type': 'added',
                    'path': current_path,
                    'value': value2
                })
            elif key not in data2:
                differences.append({
                    'type': 'removed',
                    'path': current_path,
                    'value': value1
                })
            elif value1 != value2:
                if isinstance(value1, dict) and isinstance(value2, dict):
                    # Recursive diff for nested objects
                    nested_diffs = self._calculate_diff(value1, value2, current_path)
                    differences.extend(nested_diffs)
                else:
                    differences.append({
                        'type': 'modified',
                        'path': current_path,
                        'old_value': value1,
                        'new_value': value2
                    })
                    
        return differences
        
    async def merge_versions(self,
                           source_version_ids: List[str],
                           target_version_id: str,
                           merge_type: MergeType = MergeType.THREE_WAY,
                           author: str = "",
                           conflict_resolver = None) -> MergeOperation:
        """Merge multiple versions into a target version"""
        
        merge_op = MergeOperation(
            source_versions=source_version_ids,
            target_version=target_version_id,
            merge_type=merge_type,
            author=author
        )
        
        try:
            # Load all versions
            source_versions = []
            for version_id in source_version_ids:
                version = await self.get_version(version_id)
                if not version:
                    raise ValueError(f"Source version {version_id} not found")
                source_versions.append(version)
                
            target_version = await self.get_version(target_version_id)
            if not target_version:
                raise ValueError(f"Target version {target_version_id} not found")
                
            # Perform merge based on type
            if merge_type == MergeType.FAST_FORWARD:
                result = await self._fast_forward_merge(source_versions, target_version)
            elif merge_type == MergeType.THREE_WAY:
                result = await self._three_way_merge(source_versions, target_version)
            elif merge_type == MergeType.RECURSIVE:
                result = await self._recursive_merge(source_versions, target_version)
            else:
                raise ValueError(f"Unsupported merge type: {merge_type}")
                
            # Handle conflicts if any
            if result.get('conflicts') and conflict_resolver:
                resolved_result = await conflict_resolver.resolve_conflicts(
                    result['conflicts'], 
                    context={'versions': source_versions + [target_version]}
                )
                result.update(resolved_result)
                
            # Create result version
            if result.get('success', False):
                result_version = await self.create_version(
                    entity_type=target_version.entity_type,
                    entity_id=target_version.entity_id,
                    data=result['merged_data'],
                    parent_versions=[target_version_id] + source_version_ids,
                    author=author,
                    changes=result.get('changes', []),
                    metadata={
                        'merge_operation_id': merge_op.id,
                        'merge_type': merge_type.value
                    }
                )
                
                merge_op.result_version = result_version.id
                merge_op.success = True
                
            else:
                merge_op.conflicts = [c.id for c in result.get('conflicts', [])]
                merge_op.success = False
                
            # Store merge operation
            self.merge_operations.append(merge_op)
            self.stats['merges_performed'] += 1
            
            # Notify listeners
            await self._notify_change_listeners('merge_completed', merge_op)
            
            logger.info(f"Merge operation {merge_op.id} completed with success={merge_op.success}")
            
        except Exception as e:
            merge_op.success = False
            merge_op.metadata['error'] = str(e)
            logger.error(f"Merge operation {merge_op.id} failed: {e}")
            
        return merge_op
        
    async def _fast_forward_merge(self, source_versions: List[Version], target_version: Version) -> Dict[str, Any]:
        """Perform a fast-forward merge (when target is ancestor of source)"""
        
        if len(source_versions) != 1:
            return {'success': False, 'error': 'Fast-forward merge requires exactly one source version'}
            
        source_version = source_versions[0]
        
        # Check if target is ancestor of source
        if target_version.id not in self._get_ancestors(source_version.id):
            return {'success': False, 'error': 'Target is not an ancestor of source'}
            
        # Fast-forward means we just use the source version
        return {
            'success': True,
            'merged_data': source_version.data,
            'changes': source_version.changes,
            'merge_type': 'fast_forward'
        }
        
    async def _three_way_merge(self, source_versions: List[Version], target_version: Version) -> Dict[str, Any]:
        """Perform a three-way merge"""
        
        if len(source_versions) != 1:
            return {'success': False, 'error': 'Three-way merge requires exactly one source version'}
            
        source_version = source_versions[0]
        
        # Find common ancestor
        common_ancestor_id = self._find_common_ancestor(source_version.id, target_version.id)
        if not common_ancestor_id:
            return {'success': False, 'error': 'No common ancestor found'}
            
        common_ancestor = await self.get_version(common_ancestor_id)
        if not common_ancestor:
            return {'success': False, 'error': 'Common ancestor version not found'}
            
        # Perform three-way merge
        merged_data = copy.deepcopy(common_ancestor.data)
        changes = []
        conflicts = []
        
        # Get changes from both sides
        source_changes = self._get_changes_between_versions(common_ancestor, source_version)
        target_changes = self._get_changes_between_versions(common_ancestor, target_version)
        
        # Apply non-conflicting changes
        for change in source_changes + target_changes:
            if not self._has_conflicting_change(change, source_changes + target_changes):
                self._apply_change(merged_data, change)
                changes.append(change)
            else:
                # Mark as conflict
                conflicts.append(change)
                
        return {
            'success': len(conflicts) == 0,
            'merged_data': merged_data,
            'changes': changes,
            'conflicts': conflicts,
            'merge_type': 'three_way'
        }
        
    async def _recursive_merge(self, source_versions: List[Version], target_version: Version) -> Dict[str, Any]:
        """Perform a recursive merge (for multiple sources)"""
        
        # Start with target version
        current_data = copy.deepcopy(target_version.data)
        all_changes = []
        all_conflicts = []
        
        # Merge each source version sequentially
        for source_version in source_versions:
            result = await self._three_way_merge([source_version], target_version)
            
            if result['success']:
                current_data = result['merged_data']
                all_changes.extend(result['changes'])
            else:
                all_conflicts.extend(result.get('conflicts', []))
                
        return {
            'success': len(all_conflicts) == 0,
            'merged_data': current_data,
            'changes': all_changes,
            'conflicts': all_conflicts,
            'merge_type': 'recursive'
        }
        
    def _get_ancestors(self, version_id: str) -> Set[str]:
        """Get all ancestor version IDs for a version"""
        ancestors = set()
        
        def traverse(vid):
            version = self.versions.get(vid)
            if version:
                for parent_id in version.parent_versions:
                    if parent_id not in ancestors:
                        ancestors.add(parent_id)
                        traverse(parent_id)
                        
        traverse(version_id)
        return ancestors
        
    def _find_common_ancestor(self, version1_id: str, version2_id: str) -> Optional[str]:
        """Find the most recent common ancestor of two versions"""
        
        ancestors1 = self._get_ancestors(version1_id)
        ancestors2 = self._get_ancestors(version2_id)
        
        common_ancestors = ancestors1 & ancestors2
        
        if not common_ancestors:
            return None
            
        # Find the most recent common ancestor
        # This is simplified - in practice, you'd want to find the one with the latest timestamp
        # that's reachable from both versions
        return max(common_ancestors, key=lambda aid: self.versions.get(aid, Version()).timestamp)
        
    def _get_changes_between_versions(self, from_version: Version, to_version: Version) -> List[FieldChange]:
        """Get the list of changes between two versions"""
        
        changes = []
        differences = self._calculate_diff(from_version.data, to_version.data)
        
        for diff in differences:
            change_type = ChangeType.UPDATE
            if diff['type'] == 'added':
                change_type = ChangeType.CREATE
            elif diff['type'] == 'removed':
                change_type = ChangeType.DELETE
                
            change = FieldChange(
                field_path=diff['path'],
                change_type=change_type,
                old_value=diff.get('old_value'),
                new_value=diff.get('new_value', diff.get('value')),
                timestamp=to_version.timestamp,
                author=to_version.author,
                device_id=to_version.device_id
            )
            changes.append(change)
            
        return changes
        
    def _has_conflicting_change(self, change: FieldChange, all_changes: List[FieldChange]) -> bool:
        """Check if a change conflicts with other changes"""
        
        conflicting_changes = [
            c for c in all_changes 
            if c != change and c.field_path == change.field_path and c.new_value != change.new_value
        ]
        
        return len(conflicting_changes) > 0
        
    def _apply_change(self, data: Dict[str, Any], change: FieldChange):
        """Apply a change to data"""
        
        keys = change.field_path.split('.')
        current = data
        
        # Navigate to the parent object
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Apply the change
        final_key = keys[-1]
        
        if change.change_type == ChangeType.DELETE:
            current.pop(final_key, None)
        else:
            current[final_key] = change.new_value
            
    async def create_branch(self,
                          entity_type: str,
                          entity_id: str,
                          branch_name: str,
                          from_version_id: str,
                          created_by: str = "",
                          description: str = "") -> Branch:
        """Create a new branch"""
        
        entity_key = f"{entity_type}:{entity_id}"
        
        if entity_key not in self.branches:
            self.branches[entity_key] = {}
            
        if branch_name in self.branches[entity_key]:
            raise ValueError(f"Branch {branch_name} already exists")
            
        branch = Branch(
            name=branch_name,
            head_version=from_version_id,
            created_by=created_by,
            description=description
        )
        
        self.branches[entity_key][branch_name] = branch
        
        logger.info(f"Created branch {branch_name} for {entity_type}:{entity_id}")
        
        return branch
        
    async def switch_branch(self, entity_type: str, entity_id: str, branch_name: str) -> Optional[Version]:
        """Switch to a different branch and return the head version"""
        
        entity_key = f"{entity_type}:{entity_id}"
        
        if entity_key not in self.branches or branch_name not in self.branches[entity_key]:
            return None
            
        branch = self.branches[entity_key][branch_name]
        return await self.get_version(branch.head_version)
        
    def _compress_data(self, data: Dict[str, Any]) -> bytes:
        """Compress data for storage"""
        data_bytes = pickle.dumps(data)
        compressed = zlib.compress(data_bytes)
        
        # Update compression ratio stats
        if len(data_bytes) > 0:
            self.stats['compression_ratio'] = len(compressed) / len(data_bytes)
            
        return compressed
        
    def _decompress_data(self, compressed_data: bytes) -> Dict[str, Any]:
        """Decompress data from storage"""
        data_bytes = zlib.decompress(compressed_data)
        return pickle.loads(data_bytes)
        
    def _update_storage_stats(self):
        """Update storage statistics"""
        total_size = 0
        
        for version in self.versions.values():
            if version.compressed_data:
                total_size += len(version.compressed_data)
            else:
                # Estimate size from data
                data_str = json.dumps(version.data, default=str)
                total_size += len(data_str.encode())
                
        self.stats['storage_size_bytes'] = total_size
        
    async def _notify_change_listeners(self, event_type: str, data: Any):
        """Notify registered change listeners"""
        for listener in self.change_listeners:
            try:
                await listener(event_type, data)
            except Exception as e:
                logger.error(f"Error in change listener: {e}")
                
    def add_change_listener(self, listener: callable):
        """Add a change listener"""
        self.change_listeners.append(listener)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get version manager statistics"""
        return self.stats.copy()
        
    async def cleanup_old_versions(self, 
                                 keep_count: int = 100,
                                 keep_days: int = 30):
        """Clean up old versions to save storage"""
        
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        versions_to_remove = []
        
        for entity_type, entities in self.entity_versions.items():
            for entity_id, version_ids in entities.items():
                # Keep the most recent versions
                recent_versions = version_ids[-keep_count:]
                
                for version_id in version_ids[:-keep_count]:
                    version = self.versions.get(version_id)
                    if version and version.timestamp < cutoff_time:
                        versions_to_remove.append(version_id)
                        
        # Remove old versions
        for version_id in versions_to_remove:
            self.versions.pop(version_id, None)
            
            # Update entity_versions
            for entity_type, entities in self.entity_versions.items():
                for entity_id, version_ids in entities.items():
                    if version_id in version_ids:
                        version_ids.remove(version_id)
                        
        logger.info(f"Cleaned up {len(versions_to_remove)} old versions")
        
        # Update stats
        self._update_storage_stats()