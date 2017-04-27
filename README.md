Indexing the IPFS!
==================

 * get peerIDs from `ipfs log tail`
 * resolve them to get objects
 * descend into directories
 * run `file` program to determine content type
 * scrape IPFS-ish looking links from plain-text-looking files
 * store everything in local DB
 * serve REST API
