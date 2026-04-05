"""
File service - GitHub upload logic.
"""
from typing import Optional
from pathlib import Path
import asyncio
from github import Github
from ..config import settings


class FileService:
    """File storage and GitHub upload logic."""

    def __init__(self):
        self.github = None
        if settings.GITHUB_TOKEN:
            self.github = Github(settings.GITHUB_TOKEN)

    async def upload_to_github(
        self,
        file_path: Path,
        repo_path: str,
        branch: str = "main"
    ) -> Optional[str]:
        """
        Upload a file to GitHub repository.
        
        Args:
            file_path: Local file path to upload
            repo_path: GitHub repo (e.g., "username/repo")
            branch: Target branch
        
        Returns:
            GitHub file URL or None on failure
        """
        if not self.github:
            print("GitHub token not configured")
            return None

        try:
            repo = self.github.get_repo(repo_path)
            
            with open(file_path, "rb") as f:
                content = f.read()
            
            # Get file path in repo
            repo_path_str = str(file_path).replace("./", "")
            
            # Check if file exists
            try:
                existing_file = repo.get_contents(repo_path_str, ref=branch)
                # Update existing file
                repo.update_file(
                    path=repo_path_str,
                    message=f"Update {file_path.name}",
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
            except Exception:
                # Create new file
                repo.create_file(
                    path=repo_path_str,
                    message=f"Upload {file_path.name}",
                    content=content,
                    branch=branch
                )
            
            return f"https://github.com/{repo_path}/blob/{branch}/{repo_path_str}"
        
        except Exception as e:
            print(f"GitHub upload error: {e}")
            return None

    async def download_from_github(
        self,
        repo_path: str,
        file_path: str,
        branch: str = "main"
    ) -> Optional[bytes]:
        """Download a file from GitHub."""
        if not self.github:
            return None

        try:
            repo = self.github.get_repo(repo_path)
            contents = repo.get_contents(file_path, ref=branch)
            return contents.decoded_content
        except Exception as e:
            print(f"GitHub download error: {e}")
            return None

    def get_local_storage_path(self, user_id: str, project_id: str, date_path: str) -> Path:
        """Get local storage path for a user's project data."""
        base = Path(settings.STORAGE_PATH) / "users" / user_id / "projects" / project_id / date_path
        base.mkdir(parents=True, exist_ok=True)
        return base

    async def save_batch_file(
        self,
        user_id: str,
        project_id: str,
        filename: str,
        content: bytes
    ) -> Path:
        """Save a batch file to local storage."""
        from ..utils.time import get_date_path
        date_path = get_date_path()
        storage_dir = self.get_local_storage_path(user_id, project_id, date_path)
        
        file_path = storage_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path

    async def upload_batch(
        self,
        user_id: str,
        project_id: str,
        batch_dir: Path
    ) -> bool:
        """Upload all files in a batch directory to GitHub."""
        if not settings.GITHUB_REPO:
            return False
        
        success = True
        for file_path in batch_dir.glob("*"):
            if file_path.is_file():
                result = await self.upload_to_github(
                    file_path,
                    settings.GITHUB_REPO
                )
                if not result:
                    success = False
        
        return success