# STAC Catalog Builder
- [STAC Catalog Builder](#stac-catalog-builder)
  - [Setup - Installation](#setup---installation)
  - [Running the Stacbuilder Tool](#running-the-stacbuilder-tool)


This tool generates a STAC collection from a set of GeoTiff images.

It is mainly intended to create STAC collections and catalogs for use in [openEO](https://openeo.org/), with the load_stac process.

It requires a some configuration for the fields we need to fill in, but the goal is to make it much easier to generate STAC collections from a set of EO images.

For now it only supports GeoTIFFs. For example, netCDF is not supported yet, because it can be a lot more complex to extract info from than GeoTIFF.
We wanted to start with GeoTIFF and we can see about other needs later.

- [Setup - Installation](docs/installation.md)
- [How to run the STAC builder](#running-the-stacbuilder-tool)
- [Goals and User Stories](docs/goals-and-user-stories.md): A longer explanation of the goals or use case for the STAC catalog builder.

## Setup - Installation

See: [docs/installation.md](docs/installation.md)

## Running the Stacbuilder Tool

See: [docs/how-to-run-stacbuilder.md](docs/how-to-run-stacbuilder.md)
