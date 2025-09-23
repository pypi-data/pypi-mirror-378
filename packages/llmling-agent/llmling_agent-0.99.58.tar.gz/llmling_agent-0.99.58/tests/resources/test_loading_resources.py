from __future__ import annotations

import pytest
import yamling

from llmling_agent.models import AgentsManifest


MANIFEST_CONFIG = """
resources:
    docs:
        type: source
        uri: "memory://"
        storage_options:
            auto_mkdir: true
    data:
        type: source
        uri: "memory://"
        storage_options:
            auto_mkdir: true
"""


async def test_resource_registry():
    """Test resource registry and unified filesystem access."""
    # Setup
    manifest = AgentsManifest.model_validate(yamling.load_yaml(MANIFEST_CONFIG))
    fs = manifest.resource_registry.get_fs()

    # Test root listing shows protocols
    root_listing = await fs._ls("/", detail=False)
    assert len(root_listing) == 2  # noqa: PLR2004
    assert all(name.endswith("://") for name in root_listing)
    assert {"docs://", "data://"} == set(root_listing)

    # Test write and read operations
    test_content = b"docs content"
    await fs._pipe_file("docs://test.txt", test_content)
    assert await fs._cat_file("docs://test.txt") == test_content

    # Test directory listing
    docs_listing = await fs._ls("docs://", detail=False)
    assert "docs://test.txt" in docs_listing

    # Test file info
    info = await fs._info("docs://test.txt")
    assert info["type"] == "file"
    assert info["name"] == "docs://test.txt"
    assert info["size"] == len(test_content)


# async def test_resource_path():
#     """Test UPath-based resource access."""
#     manifest = AgentsManifest.model_validate(yamling.load_yaml(MANIFEST_CONFIG))
#     registry = manifest.resource_registry

#     # Get path object
#     path = registry.get_path("docs")
#     assert isinstance(path, UPath)
#     assert str(path) == "docs://"
#     assert path.fs == registry.get_fs()

#     # Test write/read
#     test_content = "test content"
#     test_file = path / "test.txt"
#     await test_file.write_text(test_content)
#     assert await test_file.read_text() == test_content

#     # Test exists
#     assert await test_file.exists()
#     assert not await (path / "nonexistent.txt").exists()

#     # Test glob
#     await (path / "dir" / "file1.txt").write_text("content 1")
#     await (path / "dir" / "file2.txt").write_text("content 2")
#     files = [str(p) for p in await path.glob("dir/*.txt")]
#     assert len(files) == 2
#     assert "docs://dir/file1.txt" in files
#     assert "docs://dir/file2.txt" in files

#     # Test not found
#     with pytest.raises(ValueError, match="Resource not found"):
#         registry.get_path("nonexistent")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
