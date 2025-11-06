# Open Toronto Data Index

This repository contains a weekly updated index of the datasets available on the Open Toronto portal. The index is generated using a GitHub Action that fetches the sitemap, converts the dataset pages to Markdown, and stores them in a DuckDB SQL file.

## Usage

You can use the `opendata.sql` file with DuckDB to query the indexed data. This can be useful for finding relevant datasets for your data analysis or question-answering tasks.

