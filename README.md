# Personal Website
This is my personal website. It is a server-side rendered website, built upon Flask for Python and hosted on HelioHost.

# Status
My Personal Website is marked as `Active-ish`, meaning that it is actively used however only maintained/updated as necessary. If something breaks, it will be fixed, however new features are unlikely unless a need arises.

# How It Works
`flask.wsgi` is executed by the Apache server backend running on the actual physical server, which basically acts as a proxy to `myapp.py`. `myapp.py` is a Flask application that handles the various routes, interacting with external services as needed. A MySQL database is used locally to store blog post locations in Amazon S3. Amazon S3 stores the actual blog post content, which is basically a Jinja template. Amazon Simple Email Service is used to alert the user that they submitted an email to me, along with a copy of their message; AWS Lambda is used as a proxy to Amazon Simple Email Service, instead of an SMTP client.

Each page that is shown on the website is built from Jinja templates stored in the `templates` directory. The appropriate template is selected, and is effectively made up of many cascading partials; if a partial "imports" another partial, that partial is placed in the spot it is "imported."

Blog posts are stored in a `blog post cache` directory, which caches requested blog posts until the cache is cleared. (Originally, the cache was cleared every 2 days by a "web-cron" that run a simple Python script on every even day in the month (i.e., the 2nd, 4th, 6th, etc.), however this has since been halted.)

# Services Utilized
- MySQL Database (via webhost)
- Arc.io (peer-to-peer CDN)
- Amazon Simple Email Service
- Amazon Simple Storage Service
- AWS Lambda