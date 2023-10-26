# Real Estate... but its Data
A Data Engineering Project

Based on the blog post https://www.ssp.sh/blog/data-engineering-project-in-twenty-minutes/.

## Requirements

Install LocalStack:

```bash
brew install localstack
```

Create Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Execute

First, ou may need to replace some local variables in `config/default.py`, e.g. `AWS_ENDPOINT_URL`.

Secondly, set up your local AWS instance and create the S3 bucket:
```bash
./set-up-localstack.sh
```

Lastly, you can run the data exports into your local S3 bucket by executing:

```bash
python3 run.py
```

This will populate the S3 bucket with an export file with the data from website.
Since we cannot integrate our local S3 instance with Snowflake directly, we need to copy the file to our local filesystem:

```bash
awslocal s3 cp s3://real-estate/data data --region us-east-1 --endpoint-url "http://$LOCAL_IP:4566" --recursive
```

After that, you can load the file into Snowflake.

First, create the destination table

```sql
CREATE TABLE "<YOUR DB>"."<YOUR SCHEMA>"."RG_REAL_ESTATE" (
    ID TEXT,
    FINGERPRINT TEXT,
    PRICE TEXT,
    PRICE_PER_METER TEXT,
    LAST_NORMALIZED_PRICE FLOAT,
    NORMALIZED_PRICE_PER_M FLOAT,
    TYPOLOGY TEXT,
    AREA_M2 FLOAT,
    LOCATION TEXT,
    LOCATION_LATITUDE FLOAT,
    LOCATION_LONGITUDE FLOAT,
    DISTANCE_TO_CITY_CENTRE FLOAT,
    URL TEXT,
    SYNCHRONIZED_AT TIMESTAMP_NTZ
);
```

Then, upload files into your local stage in Snowflake (using `snowsql`):
```sql
PUT file://<local file path> @~/real_estate;
```

Validate that the files were correctly loaded:
```sql
LIST @~/real_estate;
```

We need to create a new file format, to parse the list inside the JSON files:
```sql
CREATE OR REPLACE FILE FORMAT my_json
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE;
```

Then, copy the data into your destination table:
```sql
COPY INTO "<your table>"
    FROM @~/real_estate
    FILE_FORMAT = my_json
    MATCH_BY_COLUMN_NAME='CASE_INSENSITIVE';
```

Once the data is correctly loaded into the table, we can grant read permissions to the Metabase role:
```sql
GRANT SELECT ON TABLE <your table> TO ROLE "METABASE_ANALYTICS";
```

## Notes
- The web scraper has no fallback mechanisms.
- We’re not deduplicating the data - we would need a dbt pipeline (or similar) to help us clean the data.
- Missing Docker image and extra configurations for orchestration/deployment.
