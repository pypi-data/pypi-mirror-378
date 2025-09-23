# PyExporter

A package to help building your python apps with [PyInstaller](https://pyinstaller.org/en/stable/index.html)

# Usage

```python
from py_exporter import PyExporter

PyExporter('script.py').run()
```

For options see [PyInstaller usage](https://pyinstaller.org/en/stable/usage.html)

## Mappings

| Variable Name                                                  | PyInstaller Option                                                                                                            |
|----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `file`                                                         | [<code>scriptname</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-arg-scriptname)                              |
| `name` | [<code>name</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-n) 
| `out_dir`                                                      | [<code>distpath</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-distpath)                                      |
 | `one_dir`                                                      | [<code>onedir</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-D)                                               |
 | `one_file`                                                     | [<code>onefile</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-F)                                              |
 | `spec_path`                                                    | [<code>specpath</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-specpath)                                      |
 | `work_path`                                                    | [<code>workpath</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-workpath)                                      |
 | `no_confirm`                                                   | [<code>noconfirm</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-y)                                            |
 | `clean`                                                        | [<code>clean</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-clean)                                            |
 | `log_level`                                                    | [<code>log-level</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-log-level)                                    |
 | `contents_directory`                                           | [<code>contents-directory</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-contents-directory)                  |
 | `console`                                                      | [<code>console</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-c)                                              |
 | `windowed`                                                     | [<code>windowed</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-w)                                             |
 | `icon`                                                         | [<code>icon</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-i)                                                 |
 | `hide_console`                                                 | [<code>hide-console</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-hide-console)                              |
 | `debug`                                                        | [<code>debug</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-d)                                                |
 | `disable_windowed_traceback`                                   | [<code>disabled_windowed_traceback</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-disable-windowed-traceback) 
| Windows Specific Options                                       |                                                                                                                               |
| `version_file`                                                 | [<code>version-file</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-version-file)                              |
| `manifest`                                                     | [<code>manifest</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-manifest)                                      |
| `admin`                                                        | [<code>uac-admin</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-uac-admin)                                    |
| `remote_desktop`                                               | [<code>uiaccess</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-uac-uiaccess)                                  |
| MacOS Specific Options                                         |                                                                                                                               |
| `argv_emulation`                                               | [<code>argv-emulation</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-argv-emulation)                          |
| `osx_bundle_identifier`                                        | [<code>osx-bundle-identifier</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-osx-bundle-identifier)            |
| `target_architecture`                                          | [<code>target-architecture</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-target-architecture)                |
| `codesign_identify`                                            | [<code>codesign-identity</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-codesign-identity)                    |
| `osx_entitlements_file`                                        | [<code>osx-entitlements-file</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-osx-entitlements-file)            |

## Other options

| Function                         | Arguments                                                     | PyInstaller Option                                                                                                                                                                                                                                           |                                                                                 
|----------------------------------|---------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `add_data`                       | _source_: `str \| Path`, _destination_: `str \| Path`         | [<code>add_data</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-add-data)                                                                                                                                                                     | 
| `add_binary`                     | _source_: `str \| Path`, _destination_: `str \| Path`         | [<code>add_binary</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-add-binary)                                                                                                                                                                 | 
| `add_path`                       | _directories_: `list[str \| Path]`                            | [<code>paths</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-p)                                                                                                                                                                               | 
| `add_hidden_import`              | _module_names_: `list[str]`                                   | [<code>hidden-import</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import)                                                                                                                                                           | 
| `add_additional_hooks_directory` | _hook_paths_: `list[str \| Path]`                             | [<code>additional-hooks-dir</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-additional-hooks-dir)                                                                                                                                             | 
| `add_runtime_hook`               | _runtime_hooks_: `list[str]`                                  | [<code>runtime-hook</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-runtime-hook)                                                                                                                                                             | 
| `add_exclude_module`             | _excludes_: `list[str]`                                       | [<code>exclude-module</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-exclude-module)                                                                                                                                                         | 
| `add_copy_metadata`              | _package_names_: `list[str \| tuple[str, bool]]`              | if second argument is `False` [<code>copy-metadata</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-copy-metadata) else [<code>recursive-copy-metadata</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-recursive-copy-metadata) | 
| `add_collect`                    | _collect_type_: `CollectType`, _module_names_: `list[str]`    | Depends on `collect_type`                                                                                                                                                                                                                                    | 
| Windows Specific Options         |                                                               |                                                                                                                                                                                                                                                              |
| `add_resource` | _resources_: `list[tuple[str \| PATH, str, str, str \| int]]` | [<code>resource</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-r)

## Enums

### `CollectType`
- [_SUBMODULES_](https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-submodules)
- [_DATA_](https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-data)
- [_BINARIES_](https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-binaries)
- [_ALL_](https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-all)
### [<code>LogLevel</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-log-level)
- _TRACE_
- _DEBUG_
- _INFO_
- _WARN_
- _DEPRECATION_
- _ERROR_
- _FATAL_

### [<code>Debug</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-d)
- _ALL_
- _IMPORTS_
- _BOOTLOADER_
- _NO_ARCHIVE_

### [<code>HideConsole</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-hide-console)
- _HIDE_EARLY_
- _HIDE_LATE_
- _MINIMIZE_EARLY_
- _MINIMIZE_LATE_

### [<code>TargetArchitecture</code>](https://pyinstaller.org/en/stable/usage.html#cmdoption-target-architecture)
- _x86_64_
- _arm64_
- _universal_