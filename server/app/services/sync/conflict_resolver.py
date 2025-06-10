"""
Conflict Resolution System

Implements various conflict resolution algorithms for data synchronization:
- Last Write Wins (LWW) strategy
- Three-way merge algorithm
- Custom business rule-based resolution
- Operational Transform (OT) for text editing
- Conflict detection and metadata tracking
- User-driven conflict resolution with fallback strategies
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime
import difflib
import copy

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts that can occur"""
    CONCURRENT_MODIFICATION = "concurrent_modification"
    DELETE_MODIFY = "delete_modify"
    FIELD_CONFLICT = "field_conflict"
    STRUCTURAL_CONFLICT = "structural_conflict"
    PERMISSION_CONFLICT = "permission_conflict"
    VERSION_CONFLICT = "version_conflict"


class ResolutionStrategy(Enum):
    """Available conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    THREE_WAY_MERGE = "three_way_merge"
    OPERATIONAL_TRANSFORM = "operational_transform"
    CUSTOM_RULES = "custom_rules"
    USER_DECISION = "user_decision"
    MERGE_ALL_CHANGES = "merge_all_changes"


class ConflictResolution(Enum):
    """Possible conflict resolution outcomes"""
    RESOLVED = "resolved"
    NEEDS_USER_INPUT = "needs_user_input"
    FAILED = "failed"
    DEFERRED = "deferred"


@dataclass
class VersionInfo:
    """Version information for conflict detection"""
    version: str
    timestamp: float
    author: str
    device_id: str
    checksum: Optional[str] = None
    parent_version: Optional[str] = None


@dataclass
class DataChange:
    """Represents a change to data"""
    field_path: str  # e.g., "user.profile.name"
    old_value: Any
    new_value: Any
    timestamp: float
    author: str
    device_id: str
    operation: str = "update"  # update, delete, create


@dataclass
class ConflictInfo:
    """Information about a detected conflict"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ConflictType = ConflictType.CONCURRENT_MODIFICATION
    entity_type: str = ""
    entity_id: str = ""
    conflicting_versions: List[VersionInfo] = field(default_factory=list)
    conflicting_changes: List[DataChange] = field(default_factory=list)
    base_version: Optional[VersionInfo] = None
    detected_at: float = field(default_factory=time.time)
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_result: Optional[ConflictResolution] = None
    resolved_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MergeResult:
    """Result of a merge operation"""
    success: bool
    merged_data: Optional[Dict[str, Any]] = None
    conflicts: List[ConflictInfo] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConflictResolver:
    """
    Comprehensive conflict resolution system for data synchronization
    
    Features:
    - Multiple resolution strategies
    - Automatic conflict detection
    - Three-way merge algorithm
    - Operational transform for text
    - Custom business rules
    - User-driven resolution with UI callbacks
    - Conflict history and analytics
    """
    
    def __init__(self):
        # Resolution strategy handlers
        self.strategy_handlers: Dict[ResolutionStrategy, Callable] = {
            ResolutionStrategy.LAST_WRITE_WINS: self._resolve_last_write_wins,
            ResolutionStrategy.FIRST_WRITE_WINS: self._resolve_first_write_wins,
            ResolutionStrategy.THREE_WAY_MERGE: self._resolve_three_way_merge,
            ResolutionStrategy.OPERATIONAL_TRANSFORM: self._resolve_operational_transform,
            ResolutionStrategy.CUSTOM_RULES: self._resolve_custom_rules,
            ResolutionStrategy.USER_DECISION: self._resolve_user_decision,
            ResolutionStrategy.MERGE_ALL_CHANGES: self._resolve_merge_all_changes
        }
        
        # Custom rule handlers
        self.custom_rules: Dict[str, Callable] = {}
        
        # User decision callbacks
        self.user_decision_callbacks: List[Callable] = []
        
        # Conflict history
        self.conflict_history: List[ConflictInfo] = []
        
        # Statistics
        self.stats = {
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'conflicts_failed': 0,
            'user_interventions': 0,
            'strategy_usage': {strategy.value: 0 for strategy in ResolutionStrategy}
        }
        
    async def detect_conflicts(self, 
                             entity_type: str,
                             entity_id: str,
                             local_data: Dict[str, Any],
                             remote_data: Dict[str, Any],
                             local_version: VersionInfo,
                             remote_version: VersionInfo,
                             base_version: Optional[VersionInfo] = None) -> List[ConflictInfo]:
        """Detect conflicts between local and remote data"""
        
        conflicts = []
        
        # Check for version conflicts
        if local_version.version == remote_version.version:
            return conflicts  # No conflict - same version
            
        # Detect different types of conflicts
        
        # 1. Concurrent modification conflict
        if (local_version.timestamp != remote_version.timestamp and
            self._has_overlapping_changes(local_data, remote_data)):
            
            conflict = ConflictInfo(
                type=ConflictType.CONCURRENT_MODIFICATION,
                entity_type=entity_type,
                entity_id=entity_id,
                conflicting_versions=[local_version, remote_version],
                base_version=base_version
            )
            
            # Analyze specific field conflicts
            field_conflicts = self._detect_field_conflicts(local_data, remote_data)
            conflict.conflicting_changes = field_conflicts
            
            conflicts.append(conflict)
            
        # 2. Delete-modify conflict
        elif self._is_delete_modify_conflict(local_data, remote_data):
            conflict = ConflictInfo(
                type=ConflictType.DELETE_MODIFY,
                entity_type=entity_type,
                entity_id=entity_id,
                conflicting_versions=[local_version, remote_version],
                base_version=base_version
            )
            conflicts.append(conflict)
            
        # 3. Structural conflicts (schema changes)
        structural_conflicts = self._detect_structural_conflicts(local_data, remote_data)
        if structural_conflicts:
            conflict = ConflictInfo(
                type=ConflictType.STRUCTURAL_CONFLICT,
                entity_type=entity_type,
                entity_id=entity_id,
                conflicting_versions=[local_version, remote_version],
                base_version=base_version,
                conflicting_changes=structural_conflicts
            )
            conflicts.append(conflict)
            
        # Update statistics
        self.stats['conflicts_detected'] += len(conflicts)
        
        # Store in history
        self.conflict_history.extend(conflicts)
        
        logger.info(f"Detected {len(conflicts)} conflicts for {entity_type}:{entity_id}")
        
        return conflicts
        
    def _has_overlapping_changes(self, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> bool:
        """Check if local and remote data have overlapping changes"""
        # Simplified check - in production, use more sophisticated change detection
        return local_data != remote_data
        
    def _detect_field_conflicts(self, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> List[DataChange]:
        """Detect conflicts at the field level"""
        conflicts = []
        
        def compare_nested(local_obj, remote_obj, path=""):
            if isinstance(local_obj, dict) and isinstance(remote_obj, dict):
                all_keys = set(local_obj.keys()) | set(remote_obj.keys())
                for key in all_keys:
                    field_path = f"{path}.{key}" if path else key
                    
                    local_val = local_obj.get(key)
                    remote_val = remote_obj.get(key)
                    
                    if local_val != remote_val:
                        if isinstance(local_val, dict) and isinstance(remote_val, dict):
                            compare_nested(local_val, remote_val, field_path)
                        else:
                            change = DataChange(
                                field_path=field_path,
                                old_value=local_val,
                                new_value=remote_val,
                                timestamp=time.time(),
                                author="system",
                                device_id="unknown"
                            )
                            conflicts.append(change)
                            
            elif local_obj != remote_obj:
                change = DataChange(
                    field_path=path,
                    old_value=local_obj,
                    new_value=remote_obj,
                    timestamp=time.time(),
                    author="system",
                    device_id="unknown"
                )
                conflicts.append(change)
                
        compare_nested(local_data, remote_data)
        return conflicts
        
    def _is_delete_modify_conflict(self, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> bool:
        """Check if one side deleted while the other modified"""
        local_deleted = local_data.get('_deleted', False)
        remote_deleted = remote_data.get('_deleted', False)
        
        return (local_deleted and not remote_deleted) or (remote_deleted and not local_deleted)
        
    def _detect_structural_conflicts(self, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> List[DataChange]:
        """Detect structural conflicts (schema changes)"""
        conflicts = []
        
        # Check for schema version mismatches
        local_schema = local_data.get('_schema_version')
        remote_schema = remote_data.get('_schema_version')
        
        if local_schema and remote_schema and local_schema != remote_schema:
            change = DataChange(
                field_path="_schema_version",
                old_value=local_schema,
                new_value=remote_schema,
                timestamp=time.time(),
                author="system",
                device_id="unknown",
                operation="schema_change"
            )
            conflicts.append(change)
            
        return conflicts
        
    async def resolve_conflicts(self, 
                              conflicts: List[ConflictInfo],
                              strategy: ResolutionStrategy = ResolutionStrategy.THREE_WAY_MERGE,
                              context: Dict[str, Any] = None) -> List[MergeResult]:
        """Resolve a list of conflicts using the specified strategy"""
        
        results = []
        
        for conflict in conflicts:
            try:
                result = await self._resolve_single_conflict(conflict, strategy, context or {})
                results.append(result)
                
                # Update statistics
                if result.success:
                    self.stats['conflicts_resolved'] += 1
                else:
                    self.stats['conflicts_failed'] += 1
                    
                self.stats['strategy_usage'][strategy.value] += 1
                
                # Update conflict info
                conflict.resolution_strategy = strategy
                conflict.resolution_result = ConflictResolution.RESOLVED if result.success else ConflictResolution.FAILED
                conflict.resolved_data = result.merged_data
                
            except Exception as e:
                logger.error(f"Error resolving conflict {conflict.id}: {e}")
                result = MergeResult(success=False, warnings=[str(e)])
                results.append(result)
                self.stats['conflicts_failed'] += 1
                
        return results
        
    async def _resolve_single_conflict(self, 
                                     conflict: ConflictInfo,
                                     strategy: ResolutionStrategy,
                                     context: Dict[str, Any]) -> MergeResult:
        """Resolve a single conflict using the specified strategy"""
        
        handler = self.strategy_handlers.get(strategy)
        if not handler:
            raise ValueError(f"No handler for strategy: {strategy}")
            
        logger.info(f"Resolving conflict {conflict.id} using strategy {strategy}")
        
        return await handler(conflict, context)
        
    async def _resolve_last_write_wins(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict using Last Write Wins strategy"""
        
        if len(conflict.conflicting_versions) < 2:
            return MergeResult(success=False, warnings=["Insufficient version information"])
            
        # Find the version with the latest timestamp
        latest_version = max(conflict.conflicting_versions, key=lambda v: v.timestamp)
        
        # The "winning" data would need to be provided in context
        winning_data = context.get('version_data', {}).get(latest_version.version)
        
        if not winning_data:
            return MergeResult(success=False, warnings=["Latest version data not available"])
            
        return MergeResult(
            success=True,
            merged_data=winning_data,
            metadata={
                'winning_version': latest_version.version,
                'winning_author': latest_version.author,
                'winning_timestamp': latest_version.timestamp
            }
        )
        
    async def _resolve_first_write_wins(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict using First Write Wins strategy"""
        
        if len(conflict.conflicting_versions) < 2:
            return MergeResult(success=False, warnings=["Insufficient version information"])
            
        # Find the version with the earliest timestamp
        earliest_version = min(conflict.conflicting_versions, key=lambda v: v.timestamp)
        
        # The "winning" data would need to be provided in context
        winning_data = context.get('version_data', {}).get(earliest_version.version)
        
        if not winning_data:
            return MergeResult(success=False, warnings=["Earliest version data not available"])
            
        return MergeResult(
            success=True,
            merged_data=winning_data,
            metadata={
                'winning_version': earliest_version.version,
                'winning_author': earliest_version.author,
                'winning_timestamp': earliest_version.timestamp
            }
        )
        
    async def _resolve_three_way_merge(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict using three-way merge algorithm"""
        
        # Get the three versions: base, local, remote
        version_data = context.get('version_data', {})
        
        base_data = {}
        if conflict.base_version:
            base_data = version_data.get(conflict.base_version.version, {})
            
        if len(conflict.conflicting_versions) < 2:
            return MergeResult(success=False, warnings=["Insufficient versions for three-way merge"])
            
        local_data = version_data.get(conflict.conflicting_versions[0].version, {})
        remote_data = version_data.get(conflict.conflicting_versions[1].version, {})
        
        # Perform three-way merge
        merged_data = copy.deepcopy(base_data)
        warnings = []
        unresolved_conflicts = []
        
        def merge_recursive(base_obj, local_obj, remote_obj, path=""):
            if isinstance(base_obj, dict) and isinstance(local_obj, dict) and isinstance(remote_obj, dict):
                result = copy.deepcopy(base_obj)
                
                all_keys = set(base_obj.keys()) | set(local_obj.keys()) | set(remote_obj.keys())
                
                for key in all_keys:
                    field_path = f"{path}.{key}" if path else key
                    
                    base_val = base_obj.get(key)
                    local_val = local_obj.get(key)
                    remote_val = remote_obj.get(key)
                    
                    # Apply three-way merge logic
                    if local_val == remote_val:
                        # Both made the same change or no change
                        result[key] = local_val
                    elif local_val == base_val:
                        # Only remote changed
                        result[key] = remote_val
                    elif remote_val == base_val:
                        # Only local changed
                        result[key] = local_val
                    else:
                        # Both changed differently - conflict
                        if isinstance(local_val, dict) and isinstance(remote_val, dict):
                            result[key] = merge_recursive(base_val or {}, local_val, remote_val, field_path)
                        else:
                            # Cannot automatically resolve
                            unresolved_conflicts.append(ConflictInfo(
                                type=ConflictType.FIELD_CONFLICT,
                                entity_type=conflict.entity_type,
                                entity_id=conflict.entity_id,
                                conflicting_changes=[
                                    DataChange(field_path=field_path, old_value=base_val, new_value=local_val, 
                                             timestamp=conflict.conflicting_versions[0].timestamp,
                                             author=conflict.conflicting_versions[0].author,
                                             device_id=conflict.conflicting_versions[0].device_id),
                                    DataChange(field_path=field_path, old_value=base_val, new_value=remote_val,
                                             timestamp=conflict.conflicting_versions[1].timestamp, 
                                             author=conflict.conflicting_versions[1].author,
                                             device_id=conflict.conflicting_versions[1].device_id)
                                ]
                            ))
                            
                            # Use last write wins as fallback
                            if conflict.conflicting_versions[0].timestamp > conflict.conflicting_versions[1].timestamp:
                                result[key] = local_val
                            else:
                                result[key] = remote_val
                                
                            warnings.append(f"Unresolved conflict at {field_path}, used last write wins")
                            
                return result
                
            else:
                # Non-dict values - use simple comparison
                if local_obj == remote_obj:
                    return local_obj
                elif local_obj == base_obj:
                    return remote_obj  
                elif remote_obj == base_obj:
                    return local_obj
                else:
                    # Conflict - use last write wins
                    if conflict.conflicting_versions[0].timestamp > conflict.conflicting_versions[1].timestamp:
                        return local_obj
                    else:
                        return remote_obj
                        
        merged_data = merge_recursive(base_data, local_data, remote_data)
        
        return MergeResult(
            success=len(unresolved_conflicts) == 0,
            merged_data=merged_data,
            conflicts=unresolved_conflicts,
            warnings=warnings,
            metadata={
                'merge_type': 'three_way',
                'base_version': conflict.base_version.version if conflict.base_version else None,
                'merged_versions': [v.version for v in conflict.conflicting_versions]
            }
        )
        
    async def _resolve_operational_transform(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict using Operational Transform (mainly for text)"""
        
        # Simplified OT implementation for text fields
        # In production, use a proper OT library like ShareJS
        
        text_conflicts = [c for c in conflict.conflicting_changes 
                         if isinstance(c.old_value, str) and isinstance(c.new_value, str)]
        
        if not text_conflicts:
            return MergeResult(success=False, warnings=["No text conflicts found for OT"])
            
        merged_data = context.get('version_data', {}).get(conflict.conflicting_versions[0].version, {})
        
        for text_conflict in text_conflicts:
            # Simple text merge using diff
            old_text = text_conflict.old_value or ""
            local_text = text_conflict.new_value or ""
            remote_text = getattr(text_conflict, 'remote_value', old_text)
            
            # Use difflib to find the best merge
            merged_text = self._merge_text_changes(old_text, local_text, remote_text)
            
            # Update the merged data
            self._set_nested_value(merged_data, text_conflict.field_path, merged_text)
            
        return MergeResult(
            success=True,
            merged_data=merged_data,
            metadata={'merge_type': 'operational_transform'}
        )
        
    def _merge_text_changes(self, base_text: str, local_text: str, remote_text: str) -> str:
        """Merge text changes using a simple diff-based approach"""
        
        if local_text == remote_text:
            return local_text
            
        # Use difflib to create a merged version
        # This is a simplified version - production systems would use proper OT
        
        local_diff = list(difflib.unified_diff(base_text.splitlines(), local_text.splitlines(), lineterm=''))
        remote_diff = list(difflib.unified_diff(base_text.splitlines(), remote_text.splitlines(), lineterm=''))
        
        # If changes don't overlap, merge them
        # This is a very basic implementation
        if not self._diffs_overlap(local_diff, remote_diff):
            # Apply both sets of changes
            lines = base_text.splitlines()
            # Apply remote changes first, then local (order matters)
            for line in reversed(remote_diff):
                if line.startswith('+'):
                    lines.append(line[1:])
            for line in reversed(local_diff):
                if line.startswith('+'):
                    lines.append(line[1:])
            return '\n'.join(lines)
        else:
            # Conflicting changes - use local version as fallback
            return local_text
            
    def _diffs_overlap(self, diff1: List[str], diff2: List[str]) -> bool:
        """Check if two diffs overlap (simplified check)"""
        # Very basic overlap detection
        return len(diff1) > 0 and len(diff2) > 0
        
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set a value in nested dictionary using dot notation path"""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    async def _resolve_custom_rules(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict using custom business rules"""
        
        entity_type = conflict.entity_type
        rule_handler = self.custom_rules.get(entity_type)
        
        if not rule_handler:
            return MergeResult(success=False, warnings=[f"No custom rules for entity type: {entity_type}"])
            
        try:
            return await rule_handler(conflict, context)
        except Exception as e:
            return MergeResult(success=False, warnings=[f"Custom rule failed: {str(e)}"])
            
    async def _resolve_user_decision(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict by requesting user decision"""
        
        self.stats['user_interventions'] += 1
        
        # Call user decision callbacks
        for callback in self.user_decision_callbacks:
            try:
                result = await callback(conflict, context)
                if result:
                    return result
            except Exception as e:
                logger.error(f"User decision callback error: {e}")
                
        # If no callback resolved it, mark as needing user input
        conflict.resolution_result = ConflictResolution.NEEDS_USER_INPUT
        
        return MergeResult(
            success=False,
            warnings=["Conflict requires user decision"],
            metadata={'requires_user_input': True}
        )
        
    async def _resolve_merge_all_changes(self, conflict: ConflictInfo, context: Dict[str, Any]) -> MergeResult:
        """Resolve conflict by merging all non-conflicting changes"""
        
        version_data = context.get('version_data', {})
        
        if len(conflict.conflicting_versions) < 2:
            return MergeResult(success=False, warnings=["Insufficient versions for merge"])
            
        # Start with first version and apply all non-conflicting changes
        merged_data = copy.deepcopy(version_data.get(conflict.conflicting_versions[0].version, {}))
        
        for i in range(1, len(conflict.conflicting_versions)):
            version = conflict.conflicting_versions[i]
            version_data_i = version_data.get(version.version, {})
            
            # Merge non-conflicting fields
            merged_data = self._merge_non_conflicting(merged_data, version_data_i)
            
        return MergeResult(
            success=True,
            merged_data=merged_data,
            metadata={'merge_type': 'merge_all_changes'}
        )
        
    def _merge_non_conflicting(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two data objects, keeping all changes from both"""
        
        result = copy.deepcopy(data1)
        
        for key, value in data2.items():
            if key not in result:
                result[key] = value
            elif isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_non_conflicting(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                # Merge lists by combining unique elements
                result[key] = list(set(result[key] + value))
            # For conflicting scalar values, keep the existing one (data1)
            
        return result
        
    def add_custom_rule(self, entity_type: str, handler: Callable):
        """Add a custom rule handler for an entity type"""
        self.custom_rules[entity_type] = handler
        
    def add_user_decision_callback(self, callback: Callable):
        """Add a callback for user decision conflicts"""
        self.user_decision_callbacks.append(callback)
        
    def get_conflict_history(self, 
                           entity_type: str = None,
                           entity_id: str = None,
                           limit: int = 100) -> List[ConflictInfo]:
        """Get conflict history with optional filtering"""
        
        history = self.conflict_history
        
        if entity_type:
            history = [c for c in history if c.entity_type == entity_type]
            
        if entity_id:
            history = [c for c in history if c.entity_id == entity_id]
            
        return history[-limit:]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics"""
        return self.stats.copy()