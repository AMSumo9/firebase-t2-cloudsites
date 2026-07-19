# Firebase cloudsite aggregator

This repository is the durable deployment source for 0006 cloudsites hosted on
two neutral shared-path sites:

- `https://sites-e470-1.web.app/<slug>/`
- `https://sites-e470-2.web.app/<slug>/`

- Account scope: 0006 cloudsites only.
- Money sites, rank-and-rent sites, directories, apps, and other operating
  properties require a separate Firebase project and credentials.
- T1 workers update only `public/t1/<slug>/`.
- T2 workers update only `public/t2/<slug>/`.
- GitHub Actions serialises deploys and publishes both complete trees.
- Provider services are retained unless the user explicitly approves deletion.
- Repository owner: `AMSumo9`; T2 node repositories receive only the scoped
  `AMSUMO_GITHUB_TOKEN` needed to update this aggregator.
