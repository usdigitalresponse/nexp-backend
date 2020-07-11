# NEXP Backend

## Overview

We built the NEXP bakend to support Louisiana Health Work Connect, a program administered by the state of Louisiana to connect furloughed healthcare workers with medical facilities in need of additional staff.

Healthcare workers fill out an Airtable form to be added to the system. The State itself onboards medical facilities. This system reminds facility administrators to update the State about their staffing needs at a regular cadence. With those needs documented, this system sends an email to facilities each morning with a expiring link to an excel spreadsheet of matching candidates.

## Installation & Deploys

For development:

    pipenv install

To deploy, install docker and serverless (`npm install -g serverless`). Then,

    make build
    make deploy

To deploy to production

    STAGE=prod make deploy

AWS deploys rely on a handful of SSM parameters documented in serverless.yml.

## Environment Variables

These environment variables are required:

- `SENDGRID_API_KEY`
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`
- `S3_BUCKET`
- `S3_PREFIX`
- `GOOGLE_CREDENTIALS`

These environment variables have default values:

- `NEXP_TIMEZONE="US/Central"`
- `AIRTABLE_CANDIDATES_TABLE="Candidates"`
- `AIRTABLE_FACILITIES_TABLE="Facilities"`
- `AIRTABLE_NEEDS_TABLE="Facility Staffing Needs"`
- `AIRTABLE_CONFIG_TABLE="Configuration"`
- `S3_URL_EXPIRY_SECONDS=43200`
- `OVERRIDE_EMAIL_DESTINATION # unset`
