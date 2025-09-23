"""
V1-pattern backup mechanism before applying automated fixes.

Incorporates learnings from experimental v1 projects for safe automated fixes.
"""

import shutil
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib


@dataclass
class BackupInfo:
    """Information about a created backup."""
    backup_id: str
    project_path: str
    backup_path: str
    timestamp: str
    files_backed_up: List[str]
    backup_size_bytes: int
    checksum: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """Create from dictionary."""
        return cls(**data)


class BackupManager:
    """
    V1-pattern: Comprehensive backup management before applying fixes.

    Features:
    - Automatic backup creation before any automated fixes
    - Selective file backup based on scan results
    - Backup verification and integrity checking
    - Easy restoration capabilities
    - Metadata tracking for audit trails
    """

    def __init__(self, backup_root: Optional[Path] = None):
        self.backup_root = backup_root or Path.home() / ".mcp_scanner_backups"
        self.backup_root.mkdir(exist_ok=True)
        self.manifest_file = self.backup_root / "backup_manifest.json"

    def create_backup(self, project_path: Path,
                     files_to_backup: Optional[List[Path]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> BackupInfo:
        """
        Create backup of project files before applying fixes.

        Args:
            project_path: Root project directory
            files_to_backup: Specific files to backup (None = all Python files)
            metadata: Additional metadata to store with backup

        Returns:
            BackupInfo with details about created backup
        """
        # Generate unique backup ID
        timestamp = datetime.now()
        backup_id = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}_{self._generate_short_hash(str(project_path))}"

        # Create backup directory
        backup_path = self.backup_root / backup_id
        backup_path.mkdir(exist_ok=True)

        # Determine files to backup
        if files_to_backup is None:
            files_to_backup = self._discover_python_files(project_path)

        # Perform backup
        backed_up_files = []
        total_size = 0

        for file_path in files_to_backup:
            if file_path.exists() and file_path.is_file():
                # Calculate relative path for backup structure
                try:
                    rel_path = file_path.relative_to(project_path)
                except ValueError:
                    # File is outside project, use absolute path structure
                    rel_path = Path(str(file_path).lstrip('/'))

                # Create backup file path
                backup_file_path = backup_path / rel_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(file_path, backup_file_path)
                backed_up_files.append(str(rel_path))
                total_size += file_path.stat().st_size

        # Calculate backup checksum
        backup_checksum = self._calculate_backup_checksum(backup_path)

        # Create backup info
        backup_info = BackupInfo(
            backup_id=backup_id,
            project_path=str(project_path.absolute()),
            backup_path=str(backup_path.absolute()),
            timestamp=timestamp.isoformat(),
            files_backed_up=backed_up_files,
            backup_size_bytes=total_size,
            checksum=backup_checksum,
            metadata=metadata or {}
        )

        # Save backup manifest
        self._update_manifest(backup_info)

        # Create backup metadata file
        metadata_file = backup_path / "backup_info.json"
        with open(metadata_file, 'w') as f:
            json.dump(backup_info.to_dict(), f, indent=2)

        return backup_info

    def create_targeted_backup(self, scan_results: List[Dict[str, Any]],
                             project_path: Path) -> BackupInfo:
        """
        Create backup of only files that will be modified based on scan results.

        Args:
            scan_results: List of issues that will be fixed
            project_path: Root project directory

        Returns:
            BackupInfo for the targeted backup
        """
        # Extract files that will be modified
        files_to_modify = set()

        for result in scan_results:
            if isinstance(result, dict) and 'issues' in result:
                for issue in result['issues']:
                    if 'file' in issue:
                        file_path = Path(issue['file'])
                        if not file_path.is_absolute():
                            file_path = project_path / file_path
                        files_to_modify.add(file_path)

        metadata = {
            "backup_type": "targeted",
            "scan_results_count": len(scan_results),
            "files_to_modify_count": len(files_to_modify),
            "purpose": "Pre-fix backup for automated issue resolution"
        }

        return self.create_backup(
            project_path=project_path,
            files_to_backup=list(files_to_modify),
            metadata=metadata
        )

    def restore_backup(self, backup_id: str, verify_checksum: bool = True) -> bool:
        """
        Restore files from a backup.

        Args:
            backup_id: ID of backup to restore
            verify_checksum: Whether to verify backup integrity

        Returns:
            True if restoration successful, False otherwise
        """
        backup_info = self.get_backup_info(backup_id)
        if not backup_info:
            return False

        backup_path = Path(backup_info.backup_path)
        if not backup_path.exists():
            return False

        # Verify backup integrity if requested
        if verify_checksum:
            current_checksum = self._calculate_backup_checksum(backup_path)
            if current_checksum != backup_info.checksum:
                raise ValueError(f"Backup {backup_id} integrity check failed")

        # Restore files
        project_path = Path(backup_info.project_path)

        for relative_file in backup_info.files_backed_up:
            backup_file = backup_path / relative_file
            target_file = project_path / relative_file

            if backup_file.exists():
                # Create target directory if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)
                # Restore file
                shutil.copy2(backup_file, target_file)

        return True

    def list_backups(self, project_path: Optional[Path] = None) -> List[BackupInfo]:
        """
        List all available backups, optionally filtered by project.

        Args:
            project_path: Filter backups for specific project

        Returns:
            List of BackupInfo objects
        """
        manifest = self._load_manifest()
        backups = [BackupInfo.from_dict(backup_data) for backup_data in manifest.values()]

        if project_path:
            project_str = str(project_path.absolute())
            backups = [b for b in backups if b.project_path == project_str]

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups

    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """Get information about a specific backup."""
        manifest = self._load_manifest()
        backup_data = manifest.get(backup_id)
        return BackupInfo.from_dict(backup_data) if backup_data else None

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup and remove from manifest.

        Args:
            backup_id: ID of backup to delete

        Returns:
            True if deletion successful, False otherwise
        """
        backup_info = self.get_backup_info(backup_id)
        if not backup_info:
            return False

        # Remove backup directory
        backup_path = Path(backup_info.backup_path)
        if backup_path.exists():
            shutil.rmtree(backup_path)

        # Remove from manifest
        manifest = self._load_manifest()
        if backup_id in manifest:
            del manifest[backup_id]
            self._save_manifest(manifest)

        return True

    def cleanup_old_backups(self, max_age_days: int = 30,
                          max_backups_per_project: int = 10) -> int:
        """
        Clean up old backups based on age and count limits.

        Args:
            max_age_days: Maximum age of backups to keep
            max_backups_per_project: Maximum number of backups per project

        Returns:
            Number of backups deleted
        """
        cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        backups = self.list_backups()
        deleted_count = 0

        # Group backups by project
        by_project = {}
        for backup in backups:
            project = backup.project_path
            if project not in by_project:
                by_project[project] = []
            by_project[project].append(backup)

        # Clean up by age
        for backup in backups:
            backup_date = datetime.fromisoformat(backup.timestamp).timestamp()
            if backup_date < cutoff_date:
                if self.delete_backup(backup.backup_id):
                    deleted_count += 1

        # Clean up by count per project
        for project, project_backups in by_project.items():
            if len(project_backups) > max_backups_per_project:
                # Sort by timestamp and delete oldest
                project_backups.sort(key=lambda x: x.timestamp)
                excess_backups = project_backups[:-max_backups_per_project]
                for backup in excess_backups:
                    if self.delete_backup(backup.backup_id):
                        deleted_count += 1

        return deleted_count

    def _discover_python_files(self, project_path: Path) -> List[Path]:
        """Discover all Python files in project."""
        python_files = []
        for pattern in ["**/*.py", "**/*.pyi"]:
            python_files.extend(project_path.glob(pattern))
        return python_files

    def _generate_short_hash(self, text: str) -> str:
        """Generate short hash for backup ID."""
        return hashlib.md5(text.encode()).hexdigest()[:8]

    def _calculate_backup_checksum(self, backup_path: Path) -> str:
        """Calculate checksum of entire backup directory."""
        hasher = hashlib.sha256()

        for file_path in sorted(backup_path.rglob("*")):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)

        return hasher.hexdigest()

    def _load_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Load backup manifest."""
        if not self.manifest_file.exists():
            return {}

        try:
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_manifest(self, manifest: Dict[str, Dict[str, Any]]):
        """Save backup manifest."""
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _update_manifest(self, backup_info: BackupInfo):
        """Update manifest with new backup info."""
        manifest = self._load_manifest()
        manifest[backup_info.backup_id] = backup_info.to_dict()
        self._save_manifest(manifest)