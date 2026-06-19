# (WIP) File Integrity Monitor: V1

A Python GUI-based File Integrity Monitor for detecting, reviewing, and responding to file changes.

## Overview
File Integrity Monitor V1 is a local cybersecurity portfolio project built with Python and Tkinter.

The tool monitors a selected folder, creates a trusted baseline, detects file changes using SHA-256 hashes, displays readable diffs for text files, and provides analyst response options such as approve, revert, overwrite, and review notes.

This project is designed to demonstrate Blue Team fundamentals in a practical desktop application.

## Features
1. Create trusted file baseline
2. Detect added files
3. Detect removed files
4. Detect modified files
5. SHA-256 hash comparison
6. Text diff output for readable files
7. Changed values highlighted in red
8. Dashboard counters for added, removed, and modified files
9. Approve Changes workflow
10. Revert Changes workflow
11. Universal Overwrite Data workflow
12. Add Review Note workflow
13. Clickable file paths in the event log
14. Open selected file using the default operating system application
15. Watchdog event monitoring
16. Polling backup every 2 seconds
17. Cross-platform support for Windows, macOS, and Linux

## Screenshots - Coming Soon
- Main GUI
- Baseline created
- Modified file detected
- Diff output with changed values highlighted
- Clickable file path selected
- Overwrite Data workflow
- Review note saved

## Requirements
- Install dependencies: ```pip install watchdog```
- Tkinter is included with most Python installations.
- On some Linux distributions, Tkinter may need to be installed separately: ```sudo apt install python3-tk```

Admin/root note:
1. Normal user permissions are usually enough for monitoring files inside your own project folder.
2. Admin/root permissions may be required if monitoring protected system directories.
3. Do not run as admin/root unless the monitored path requires it.

## How to Run
1. Download the Python script (link here)
2. Run the app: ```python file_integrity_monitor.py```
   Note: Depending on your system, you may need:```python3 file_integrity_monitor.py```

## Basic Workflow
1. Open the application.
2. Select a folder to monitor.
3. Click Create Baseline.
4. Click Start Monitoring.
5. Modify, add, or delete a file in the watched folder.
6. Review the event log.
7. Choose a response action:
   - Approve Changes
   - Revert Changes
   - Overwrite Data
   - Add Review Note

## Trusted Baseline Workflow
- The baseline is the known-good state.
- The app saves the trusted baseline to: ```fim_baseline.json```

The baseline includes:
- File path
- SHA-256 hash
- Text snapshot when readable
- File size
- Modified timestamp

IMPORTANT: Do not create a baseline after a suspicious change unless you intentionally want to trust that current state.

## Change Detection
- The app compares the current folder state against the trusted baseline.
- It identifies:
  - [ADDED]
  - [REMOVED]
  - [MODIFIED]
- Modified files are detected when the current SHA-256 hash does not match the trusted baseline hash.

## Diff Output
- For readable text files, the app displays a diff.
  Example:
  ```
  -Login Pswrd: old_value
  +Login Pswrd: new_value
  ```
- Only the new changed value is highlighted in red in the GUI.

## Analyst Response Actions
### Approve Changes
- Use this when the detected change is expected and trusted.
- Approving changes updates the trusted baseline.

### Revert Changes
- Use this when the detected change is unwanted and the previous baseline value is still trusted.

Current V1 revert behavior:
- Added files are deleted.
- Removed text files are restored from the baseline snapshot.
- Modified text files are restored from the baseline snapshot.

### Overwrite Data
- Use this when neither the old value nor the changed value should be trusted.
- Example use cases:
  - Password replacement
  - API key replacement
  - Token replacement
  - Admin flag correction
  - Configuration value correction

Example field format:
  ```
  Login Pswrd: suspicious_value
  API Key: suspicious_key
  Admin Rights: Yes
  ```
- The analyst enters a field label and a replacement value.
- The replacement value is written to the file but is not logged in the event log or notes file.

### Add Review Note
- Use this to document analyst reasoning.
- Review notes are saved to:
  ```
  fim_notes.json
  ```
Example notes:
```
- Suspicious admin flag change reviewed.
- Temporary credential replacement completed.
- Change approved after validation.
- Unauthorized modification reverted.
```

## Open Selected File
Detected file paths in the event log are clickable.

Workflow:
1. Click a detected file path.
2. Click Open Selected File.
3. The file opens in the operating system default application.

Platform behavior:
  ```
  Windows: os.startfile()
  macOS: open
  Linux: xdg-open
  ```

## Polling Backup
- Some editors save files using temporary files, delayed writes, or rename operations.
- To improve reliability, the tool uses both:
  - Watchdog event monitoring
  - Polling backup every 2 seconds

## File Structure
  ```
  file-integrity-monitor/
  │
  ├── file_integrity_monitor.py
  ├── fim_baseline.json
  ├── fim_notes.json
  └── README.md
  ```
The JSON files are generated by the tool.

## Recommended .gitignore
  ```gitignore
  __pycache__/
  *.pyc
  .DS_Store
  
  fim_baseline.json
  fim_notes.json
  
  watched/
  ```

Reason:
- `fim_baseline.json` may contain file snapshots.
- `fim_notes.json` may contain analyst notes.
- `watched/` may contain test files or sensitive lab data.

## Security Notes
- This tool is for local lab and educational use.
- Do not store real production secrets in test files.
- Replacement values are not logged, but they are still written into the selected file.
- The baseline file is not cryptographically protected in V1.
- A future version should add HMAC signing or encryption for baseline integrity.

## Known Limitations
- Binary file restore is not fully supported in V1.
- RTF files may show raw RTF formatting in diff output.
- Overwrite Data expects a field/value format using a colon.
- Baseline files are stored locally as JSON.
- This is not a production EDR or enterprise file integrity monitoring system.

## Troubleshooting
### Changes are not detected
Check:
1. A baseline was created.
2. Monitoring was started.
3. The changed file is inside the selected folder.
4. Wait up to 2 seconds for polling backup.
5. Try Scan for Changes manually.

### No baseline found
Click: ```Create Baseline```

### Open Selected File does not work
Check:
- A file path was clicked in the event log.
- The file still exists.
- The operating system has a default app for that file type.

### Overwrite Data failed
Check:
- The file is readable text.
- The field label exists.
- The field uses a colon.
- The label was entered exactly.

Example:
  ```
  Login Pswrd: value
  ```


## Future Improvement Ideas:
- Add ignore rules.
- Add CSV export.
- Add JSON report export.
- Add HMAC signing for baseline protection.
- Add binary backup and restore support.
- Add suspicious keyword detection.
- Add severity levels.
- Add search/filter in the event log.
- Add packaged builds for Windows, macOS, and Linux.
- Add Splunk or Wazuh export format.
- Add unit tests.
- Add a config file.
