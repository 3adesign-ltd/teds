# Contributing

Thank you for your interest in TEDS.

## API Improvements

We welcome suggestions for changes and improvements to the API.
Please raise an issue on this repository.

## Submitting Changes

If you have fixed a problem or thought of an improvement, submit a merge request in the usual way:

1. Create a branch
2. For more significant changes, consider starting by writing an ADR: see [the ADR readme](./docs/adr/README.md)
3. Make, commit and push your changes
   - Make sure the commit message contains your email address
   - Where appropriate, make sure the commit message includes a line with one of the following:
      - `sem-ver: api-break`: where a breaking change is made
      - `sem-ver: feature`: where a new feature has been added
      - `sem-ver: deprecation`: where an existing feature has been marked as deprecated, but not yet removed
4. Run `make lint` before opening a merge request: see [Development](./README.md#development)
5. Open a merge request.
   Don't worry about the empty spaces in the template (it is aimed at internal contributions); fill in the description.

Every merge request needs a green pipeline to merge.

## Contributor Licence Agreement

TEDS is not yet published, and its licence has not yet been chosen (see [LICENCE.md](./LICENCE.md)).
The contributor licence arrangements will be set out here when it is.
