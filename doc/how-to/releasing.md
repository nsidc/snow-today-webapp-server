# Releasing

The `latest` image on Dockerhub will be updated with each commit to `main`.

To release a new tagged image to DockerHub:

* Update `VERSION.env` with new version
* Update `CHANGELOG.md` following existing pattern
* Commit
* Tag `vX.Y.Z` on the `main` branch (post-merge if necessary)
* Push tag: `git push origin vX.Y.Z`
