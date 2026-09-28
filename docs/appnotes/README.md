# Application Notes

This folder contains application notes in Markdown format.
They give ancillary information about the concepts in the TEDS API, and their application to real-world problems.
No part of these documents is part of the API specification, although specification-style language is allowed in examples and "opt-in" extensions.

There is a simple [appnote-template.md](../templates/appnote-template.md) describing the few restrictions on Application Notes.
Select a unique number for your Application Note, keep the numbers close together, and add it to the index in [docs/README.md](../README.md).

## Versioning

These notes are expected to change over time, so there must be a way to refer to specific versions.
As they are stored in a git repository, git commit IDs from the main branch identify a specific version.
To check whether the version you are looking at is the same as one someone else refers to, the command

```shell
git diff <commit> <commit> -- <filename>
```

shows whether the versions differ.
