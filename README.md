# Firebase T2 cloudsite aggregator

This repository is the durable deployment source for 0006 T2 cloudsites hosted
under `https://sumo9-cloudsites-t2.web.app/<slug>/`.

- Account scope: 0006 cloudsites only.
- Money sites, rank-and-rent sites, directories, apps, and other operating
  properties require a separate Firebase project and credentials.
- Node workflows update only `public/<slug>/` and never delete another slug.
- GitHub Actions serialises deploys and publishes the complete `public/` tree.
- Provider services are retained unless the user explicitly approves deletion.

