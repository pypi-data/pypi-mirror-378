# `ctf_orchestrator`

**Usage**:

```console
$ ctforch [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `info`: Display information about the current...
- `cleanup`: Delete non-existing CTFs or challenges...
- `run`: Run a command in the current active CTF...
- `challenge`: Manage challenges tracked in the active CTF.
- `config`: Change configurations used.
- `ctf`: Manage CTFs tracked.

## `ctforch info`

Display information about the current stateuration and active CTF.

**Usage**:

```console
$ ctforch info [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## `ctforch cleanup`

Delete non-existing CTFs or challenges from the active CTF.

**Usage**:

```console
$ ctforch cleanup [OPTIONS]
```

**Options**:

- `--mode [ctf|chal]`: [required]
- `--help`: Show this message and exit.

## `ctforch run`

Run a command in the current active CTF directory or active challenge directory.

**Usage**:

```console
$ ctforch run [OPTIONS] COMMAND_AND_ARGS...
```

**Arguments**:

- `COMMAND_AND_ARGS...`: The command to execute, followed by its arguments. [required]

**Options**:

- `--help`: Show this message and exit.

## `ctforch challenge`

Manage challenges tracked in the active CTF.

**Usage**:

```console
$ ctforch challenge [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `add`: Add a CTF Challenge to the Active CTF.
- `activate`: Activate a CTF challenge in the active CTF
- `deactivate`: Deactivate the current active challenge in...
- `solve`: Mark a challenge (the active challenge by...

### `ctforch challenge add`

Add a CTF Challenge to the Active CTF.

**Usage**:

```console
$ ctforch challenge add [OPTIONS] CHAL_NAME CATEGORY
```

**Arguments**:

- `CHAL_NAME`: [required]
- `CATEGORY`: [required]

**Options**:

- `--points TEXT`: [default: 0]
- `--solved TEXT`: [default: False]
- `--auto-active TEXT`: [default: True]
- `--help`: Show this message and exit.

### `ctforch challenge activate`

Activate a CTF challenge in the active CTF

**Usage**:

```console
$ ctforch challenge activate [OPTIONS] CHAL_NAME
```

**Arguments**:

- `CHAL_NAME`: [required]

**Options**:

- `--help`: Show this message and exit.

### `ctforch challenge deactivate`

Deactivate the current active challenge in the active CTF

**Usage**:

```console
$ ctforch challenge deactivate [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

### `ctforch challenge solve`

Mark a challenge (the active challenge by default) in the active CTF as solved.

**Usage**:

```console
$ ctforch challenge solve [OPTIONS]
```

**Options**:

- `--chal-name TEXT`
- `--flag TEXT`
- `--help`: Show this message and exit.

## `ctforch config`

Change configurations used.

**Usage**:

```console
$ ctforch config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `setup`: Setup the configuration in the /.ctf-orch.&#x27;

### `ctforch config setup`

Setup the configuration in the /.ctf-orch.&#x27;

**Usage**:

```console
$ ctforch config setup [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## `ctforch ctf`

Manage CTFs tracked.

**Usage**:

```console
$ ctforch ctf [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `init`: Initialize a CTF directory.
- `activate`: Activate a CTF as the current active CTF.
- `deactivate`: Deactivate the current active CTF.

### `ctforch ctf init`

Initialize a CTF directory.

**Usage**:

```console
$ ctforch ctf init [OPTIONS] CTF_NAME
```

**Arguments**:

- `CTF_NAME`: [required]

**Options**:

- `--directory TEXT`: [default: C:\Users\user\Desktop\CTF-orchestra]
- `--auto-active TEXT`: [default: True]
- `--help`: Show this message and exit.

### `ctforch ctf activate`

Activate a CTF as the current active CTF.

**Usage**:

```console
$ ctforch ctf activate [OPTIONS] CTF_NAME
```

**Arguments**:

- `CTF_NAME`: [required]

**Options**:

- `--help`: Show this message and exit.

### `ctforch ctf deactivate`

Deactivate the current active CTF.

**Usage**:

```console
$ ctforch ctf deactivate [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.
