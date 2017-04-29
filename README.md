Indexing the IPFS!
==================

Basic how-to
------------

Preparations

 * Set up a database supported by SQLAlchemy. I use PostgreSQL. I don't
   recommend SQLite beacuse it poorly supports paralel access.
 * Set up go_ipfs node. We need it's API to look into data.
 * Set up virtualenv and install stuff from `requirements.txt`.
 * Edit `settings.py` to match your setup. (Mainly `DB` variable.)

Utilities

 * `go_ipfs_log_scraper.py` listens for peer IDs.
 * `ipns_resolver.py` peridicaly resolves stored names to get object
   hashes.
 * `object_links_indexer.py` checks for DAG links from known object to
   other objects.
 * `file_type_indexer.py` checks file content type using awesome `file`
   program.
 * `text_ipfs_links_indexer.py` and `text_ipns_links_indexer.py` scans
   known objects for plain text links to other names and objects.
 * `rest_api.py` serves simple API to stored data using flask-restless.
   (endpoints: `localhost:5001/api/objects`, `localhost:5001/api/names`)
