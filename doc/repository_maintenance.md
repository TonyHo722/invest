# Repository Maintenance Guide

This document outlines best practices for maintaining the `invest` repository, specifically focusing on managing report data and repository size.

## Managing Report Data (`report/last/`)

The `report/last/` folder contains the latest screening results (CSV and HTML) and individual ticker reports. Since these files are numerous and change frequently, multiple commits containing these files can rapidly increase the size of the `.git` directory.

### The "Single Commit" Rule for Data
To keep the repository size small, we follow a **Single Commit Rule** for the `report/last/` folder:
- All updates to the report data should ideally be squashed into a single historical commit that represents the "latest state."
- This prevents Git from storing thousands of redundant blobs for every daily update in the history.

### How to Squash New Data into the Historical Commit
If you have made a new commit with updated reports and want to squash it into the original "add report/last folder" commit:

1. **Identify the Hashes**:
   - `LATEST_DATA_HASH`: The hash of your latest commit containing only `report/last/` changes.
   - `ORIGINAL_DATA_HASH`: The hash of the historical "add report/last folder" commit.

2. **Run an Automated Rebase**:
   Use an interactive rebase to move the latest commit and squash it into the original one. You can use a Python script as a sequence editor to automate this:

   ```bash
   # Example Python script to move and fixup the commit
   cat << 'EOF' > rebase_editor.py
   import sys
   file_path = sys.argv[1]
   with open(file_path, 'r') as f:
       lines = f.readlines()
   
   latest_hash = "YOUR_LATEST_HASH"
   target_hash = "YOUR_ORIGINAL_HASH"
   
   latest_line = None
   target_index = -1
   
   for i, line in enumerate(lines):
       if line.startswith(f"pick {latest_hash}"):
           latest_line = line.replace("pick", "f")
           del lines[i]
           break
   
   for i, line in enumerate(lines):
       if line.startswith(f"pick {target_hash}"):
           target_index = i
           break
   
   if latest_line and target_index != -1:
       lines.insert(target_index + 1, latest_line)
   
   with open(file_path, 'w') as f:
       f.writelines(lines)
   EOF
   
   GIT_SEQUENCE_EDITOR="python3 ./rebase_editor.py" git rebase -i ORIGINAL_DATA_HASH^
   ```

## Repository Health

### Pruning and Garbage Collection
To further reduce repository size after large rebases or deletions (like removing the `scratch/` folder), run:
```bash
git gc --prune=now --aggressive
```

### Git Ignore
Ensure that intermediate data, large cache files, and non-essential binaries are kept in the `scratch/` directory, which is ignored by `.gitignore`. 
- **Dated Reports**: `report/YYYYMMDD_report/` folders are ignored.
- **Cache**: `scratch/cache/` is ignored.
