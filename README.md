# infisical-image

Builds [Infisical](https://github.com/Infisical/infisical) with the Opteamax
DNS provider for ACME DNS-01 on top, until that provider is part of an upstream
release.

Every night the workflow looks up the latest upstream release. If it has not
been built yet, it checks out that tag, cherry-picks the commits of
[`opteamax/infisical@feat/opteamax-acme-dns`](https://github.com/opteamax/infisical/tree/feat/opteamax-acme-dns),
type-checks the backend, runs the DNS provider tests and builds upstream's own
`Dockerfile.standalone-infisical`.

| | |
| --- | --- |
| Image | `ghcr.io/opteamax/infisical:<upstream tag>` |
| Marker of a good build | a release in this repository named after the upstream tag |
| Machine-readable result | `build.json` attached to that release |

`build.json` carries the image digest, whether the patch was applied, and the
highest level from upstream's `upgrade-impact` notes since the previous build.

## When a build fails

The usual cause is that the patch no longer applies. Rebase
`feat/opteamax-acme-dns` onto upstream `main` in `opteamax/infisical`, push,
and start the workflow again by hand (**Actions → Build patched Infisical
image → Run workflow**). Nothing is published for a failed build, so whoever
consumes the releases simply stays on the previous version.

## When the patch is merged upstream

A tag that already contains the provider is built unchanged and its
`build.json` says `"patched": false`. From then on the upstream image
`infisical/infisical` can be used directly and this repository retired.
