# Version Management System

## 📋 How Version Syncing Works

### Single Source of Truth
- **Primary version location**: `pyproject.toml` [project] section
- **Version format**: `version = "0.7.5"`

### Automatic Sync Process

When you run `uv build`, the following happens automatically:

1. **pyproject.toml build hooks trigger**:
   ```toml
   [tool.jupyter-releaser.hooks]
   before-build-npm = [
       "python3 sync_version.py",    # ← Syncs versions BEFORE npm build
       "python -m pip install 'jupyterlab>=4.0.0,<5'"
   ]
   before-build-python = [
       "node copy-package-json-to-labextension.cjs || true"
   ]
   ```

2. **sync_version.py script runs**:
   - Reads version from `pyproject.toml` [project] section
   - Updates `package.json` version 
   - Updates `jupyterlab_firefox_launcher/labextension/package.json` version
   - Reports what was changed

3. **Build continues** with all versions synchronized

### Manual Version Updates

To update the version:

1. **Edit only one file**: `pyproject.toml`
   ```toml
   [project]
   version = "0.7.6"  # ← Change this line only
   ```

2. **Run build**: `uv build` or `yarn build`
   - All other files are automatically updated

### Files That Get Updated Automatically
- ✅ `package.json` (frontend package)
- ✅ `jupyterlab_firefox_launcher/labextension/package.json` (built extension)
- ✅ `__init__.py` (reads from package metadata at runtime)

### Benefits
- **No version conflicts**: Single source of truth prevents mismatches
- **Automatic sync**: No manual copying of version numbers
- **Build integration**: Happens automatically during `uv build`
- **Error prevention**: Can't forget to update frontend versions

### Manual Sync (if needed)
```bash
python3 sync_version.py
```

This system ensures that when you deploy your extension, all components have matching version numbers!
