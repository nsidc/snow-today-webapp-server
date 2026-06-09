# Snow Today Web App Deployment
### GitHub Repos
There are two different GitHub repos that are required for the proper functioning of the Snow Today web viewer application (<https://nsidc.org/snow-today/snow-viewer>). They are the following:
- snow-today-webapp (<https://github.com/nsidc/snow-today-webapp>)  
   Provides the code for the user facing web application
- snow-today-webapp-server (<https://github.com/nsidc/snow-today-webapp>)  
   Provides the code that generates and serves data supporting the snow-today-webapp
### Development Environments
We work in two main development environments: integration and production.
#### Jenkins Jobs
Each environment has its own separate Jenkins job for deployment.
- Integration:  
   <http://ci.jenkins-cd.apps.int.nsidc.org:8080/job/Deploy_Project_with_Garrison/>  
   This one is run by developers while testing their code changes
- Production:  
   <https://ci.jenkins-ops-2022.apps.int.nsidc.org/job/Deploy_Project_with_Garrison/>)  
   This is the one Ops runs to deploy to production
#### Applicable URLs
Each environment has its own set of URLs. One for the web application "instance" and one for the web application embedded in Snow Today web page. The web application instance is where the developers can do their testing. Generally, to see updates to the application embedded in the web page, you need a web team member to do a web deployment. Note that there are exceptions to this. See the Deployment section below for more information.
- Integration:
  - Web app instance (must be on the NSIDC VPN to view):  
     <http://integration.snow-today.apps.int.nsidc.org:8080/>
  - Embedded web app (do **not** need to be on the VPN to view):  
     <https://integration.nsidc.org/snow-today/snow-viewer>
- Production
  - Web app instance (must be on the NSIDC VPN to view):  
     <http://snow-today.apps.int.nsidc.org:8080/>
  - Embedded web app (do **not** need to be on the VPN to view):  
     <https://nsidc.org/snow-today/snow-viewer>

## Deployment

#### ************************************************************************************************

#### Snow-today-web-app

#### ************************************************************************************************

Because updates to this repo make changes to the web facing application, we must submit a web team request in Jira (e.g. SCG-4106) for these updates to be seen on the application embedded in the web site. Note: The web team will update all environments when they do their deployment: QA, integration, staging, and production. Note, we don't really utilize QA or staging. Here are the steps for releasing and deploying the snow-today-webapp after you've made updates to the repo:
- **Submit a Pull Request (PR)** - update version in the following files as part of pull request:
  - Update version in package.json
  - Update package-lock.json
    - This can be updated by running npmj job
    - Run npm i to update package-lock.json
  - Update CHANGELOG.md following existing convention.
- **Review and merge the PR**: Another NSIDC developer (if the updates are extensive) or the Project Manager (if the changes are minor) can review and merge the PR. The latest image on Dockerhub will be updated with each commit to main.
    - Commit
    - Merge to main
- **Tag the main branch** 
   To release a new tagged image to DockerHub and a new version to NPM (Node Package Manager):  
   Because there are no Releases for this repo, this is generally done from the command line:
  - Create the tag: git tag vX.Y.Z
  - Push the tag to GitHub to trigger automated releases of Docker Images and NPM bundle: git push origin vX.Y.Z
  
  *However, it can be done from the GitHub web interface with a work around:  
  A common workaround is to create a release and then immediately delete it. The underlying tag will remain. **This is the preferred method for Project Manager.**

    - Navigate to the snow-today-webapp repository on GitHub: <https://github.com/nsidc/snow-today-webapp>
    - Click on Releases then Draft a new release
    - In the **Choose a tag** dropdown menu, type a name for your new tag (e.g., v1.0.0) and click **Create new tag**.
    - Enter your desired Release title and description. Example:
      - Title: "Merge pull request #82: Remove days_without_observation"
      - Description: "Remove days_without_observation from plot dropdown menu. Upversion to v0.18.5"
    - Click Publish release
    - Immediately after publishing, delete the release. The tag will persist, but without a release entry.

- **Run the Jenkins deployment job depending on environment**. The appropriate Jenkins job can now be run. Generally done by Ops; put in a Jira PCT ticket for this work (e.g. <https://nsidc.atlassian.net/browse/PCT-3565>).
  - Integration:  
     <http://ci.jenkins-cd.apps.int.nsidc.org:8080/job/Deploy_Project_with_Garrison/>  
     This one is run by developers while testing their code changes
  - Production:  
     <https://ci.jenkins-ops-2022.apps.int.nsidc.org/job/Deploy_Project_with_Garrison/>)  
     This is the one Ops runs to deploy to production

  The application "instance" should now be updated

- **Submit a web team request** in Jira (e.g. SCG-4106) so the updated app will be pushed and embedded in the Snow Today web page.

#### ************************************************************************************************

#### Snow-today-webapp-server

#### ************************************************************************************************

For these updates to be seen on the web site, we do NOT have to submit a web team ticket but we do have to run 2 other Jenkins data ingest jobs.

Here are the steps for releasing and deploying the snow-today-webapp-server after you've made updates to the repo:

- **Submit a Pull Request (PR)** - update version in following files as part of pull request
  - Update VERSION.env with new version
  - Update CHANGELOG.md following existing pattern
- **Review and merge the PR to main**: Another NSIDC developer (if the updates are extensive) or the Project Manager (if the changes are minor) can review and merge the PR. The latest image on Dockerhub will be updated with each commit to main.
  - Navigate to the main page of snow-today-webapp-server repository on GitHub (<https://github.com/nsidc/snow-today-webapp-server>)
  - Click "Pull Requests" in top level navigation menu.
  - Click on the appropriate pull request to open it
  - Take a quick look at the changes in the "Files Changed" tab
  - If all checks have passed, click green "Merge Pull Request", add description if needed, then click "Confirm merge"
- **Tag main branch**  
   To release a new tagged image to DockerHub:

   Tag vX.Y.Z on the main branch (post-merge if necessary)  
   Can be done from the GitHub web interface using these steps. **This is the preferred method for the Project manager.**
  - Navigate to the main page of snow-today-webapp-server repository on GitHub (<https://github.com/nsidc/snow-today-webapp-server>).
  - To the right of the file list, click the **Releases** link.
  - Click **Draft a new release** or **Create a new release**.
  - In the **Choose a tag** dropdown menu, type a name for your new tag (e.g., v1.0.0) and click **Create new tag**.
  - In the **Target** dropdown, ensure the correct branch is selected - should be "main".
  - Fill in the release title and description. Example:
    - Title: "Merge pull request #73: add days w/o observation"
    - Description: "Add days without observation to list of variables and create grayscale colormap. Upversion to v0.21.3"
  - Click **Publish release** to create the tag on GitHub.

  Can also be done via the command line:

    - Create tag: git tag vX.Y.Z
    - Push tag: git push origin vX.Y.Z

- **Run the Jenkins deployment job** depending on environment. The appropriate Jenkins job can now be run. Generally done by Ops (but can be run by a dev for integration), put in a Jira PCT ticket for this work (e.g. <https://nsidc.atlassian.net/browse/PCT-3558>).
  - Integration:  
     <http://ci.jenkins-cd.apps.int.nsidc.org:8080/job/Deploy_Project_with_Garrison/>
  - Production:  
     <https://ci.jenkins-ops-2022.apps.int.nsidc.org/job/Deploy_Project_with_Garrison/>  
     Submit a Jira ticket for this (e.g. PCT-3517)
- **Run data ingest Jenkins job**  
   For snow-today-web-app-server, we need to run the Jenkins jobs that sets up the TRIGGER file so that necessary files get moved to the correct location for the web application to use. There are two Jenkins jobs that run automatically every 30 (15?) minutes, but new files are not ingested unless a TRIGGER file is present (meaning full snow today pipeline has been run including web export step).
  - Integration: <http://ci.snow-today.apps.int.nsidc.org:8080/job/snow-today_A2_Integration_Check_For_Data_And_Ingest/>
  - Production: <https://ci.jenkins-ops2022.apps.int.nsidc.org/job/Snow_Today_Ingest_Snow_Surface_Properties/>

### Example

This is an example of some minor updates that took some figuring out how to deploy.

In Feb 2026, a non-NSIDC dev made two updates (one to each repo):

- snow-today-web-app: updated the citation author list
- snow-today-webapp-server: changed of the units for y-axis in the variables.json file

After running the Jenkins jobs to deploy both repos, we did not see our change to snow-today-webapp-server (y-axis units), but we did see the change made in snow-today-web-app (author list). However, the following day, we saw the change for snow-today-webapp-server the next day. It turned out that this was because we needed to run the integration data ingest pipeline job, which ran around 7pm and that updated the static variables.json file so the integration site could use it. This is because that job pushes both statis and non-static data files. The file, variables.json is one of those static data files.

References

Snow-today-webapp releasing.md: <https://github.com/nsidc/snow-today-webapp/blob/main/doc/releasing.md>

Snow-today-webapp-server releasing.md: <https://github.com/nsidc/snow-today-webapp-server/blob/main/doc/how-to/releasing.md>
