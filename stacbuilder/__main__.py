"""The main module, which is run as the program.

This defines the Commane Line Interface of the application.
We want to keep this layer thin so we can write unit/integration tests for the
functionality underneath without dealing directly with the CLI.

The functions you find in this module should remain very simple.
"""
import datetime as dt
import json
import logging
import pprint
from pathlib import Path


import click
import dateutil.parser
import pydantic
import pydantic.errors


from stacbuilder.commandapi import CLICommands, HRLVVPCliCommands
from stacbuilder.config import CollectionConfig
from stacbuilder.verify_openeo import verify_in_openeo


_logger = logging.getLogger(__name__)


@click.group
@click.option("-v", "--verbose", is_flag=True, help="show debug output")
def cli(verbose):
    """Main CLI group. This is the base command.

    Everything that is in here will run at the start of every stacbuilder command.
    """

    #
    # Set up logging for the application.
    #
    log_level = logging.INFO
    if verbose:
        log_level = logging.DEBUG

    _logger.setLevel(log_level)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(levelname)-7s | %(message)s")
    ch.setFormatter(formatter)
    # add the handlers to the logger
    _logger.addHandler(ch)


@cli.command
@click.option(
    "-g",
    "--glob",
    default="*",
    type=click.STRING,
    help="glob pattern for collecting the GeoTIFF files. Example: */*.tif",
)
@click.option(
    "-c",
    "--collection-config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Configuration file for the collection",
)
@click.option("--overwrite", is_flag=True, help="Replace the entire output directory when it already exists")
@click.option("-m", "--max-files", type=int, default=-1, help="Stop processing after this maximum number of files.")
@click.option("-s", "--save-dataframe", is_flag=True, help="Also save the data to shapefile and geoparquet.")
@click.argument(
    "inputdir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@click.argument(
    "outputdir",
    type=click.Path(dir_okay=True, file_okay=False),
)
def build(glob, collection_config, overwrite, inputdir, outputdir, max_files, save_dataframe):
    """Build a STAC collection from a directory of GeoTIFF files."""
    CLICommands.build_collection(
        collection_config_path=collection_config,
        glob=glob,
        input_dir=inputdir,
        output_dir=outputdir,
        overwrite=overwrite,
        max_files=max_files,
        save_dataframe=save_dataframe,
    )


@cli.command
@click.option(
    "-g",
    "--glob",
    default="*",
    type=click.STRING,
    help="glob pattern for collecting the GeoTIFF files. Example: */*.tif",
)
@click.option(
    "-c",
    "--collection-config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Configuration file for the collection",
)
@click.option("--overwrite", is_flag=True, help="Replace the entire output directory when it already exists")
@click.option("-m", "--max-files", type=int, default=-1, help="Stop processing after this maximum number of files.")
@click.option("-s", "--save-dataframe", is_flag=True, help="Also save the data to shapefile and geoparquet.")
@click.argument(
    "inputdir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@click.argument(
    "outputdir",
    type=click.Path(dir_okay=True, file_okay=False),
)
def build_grouped_collections(glob, collection_config, overwrite, max_files, save_dataframe, inputdir, outputdir):
    """Build a STAC collection from a directory of GeoTIFF files."""
    CLICommands.build_grouped_collections(
        collection_config_path=collection_config,
        glob=glob,
        input_dir=inputdir,
        output_dir=outputdir,
        overwrite=overwrite,
        max_files=max_files,
        save_dataframe=save_dataframe,
    )


@cli.command
@click.option(
    "-g", "--glob", default="*", type=click.STRING, help="glob pattern to collect the GeoTIFF files. example */*.tif"
)
@click.argument(
    "inputdir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@click.option("-m", "--max-files", type=int, default=-1, help="Stop processing after this maximum number of files.")
def list_tiffs(glob, inputdir, max_files):
    """List which GeoTIFF files will be selected with this input dir and glob pattern."""
    CLICommands.list_input_files(glob=glob, input_dir=inputdir, max_files=max_files)


@cli.command
@click.option(
    "-g", "--glob", default="*", type=click.STRING, help="glob pattern to collect the GeoTIFF files. example */*.tif"
)
@click.option(
    "-c",
    "--collection-config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Configuration file for the collection",
)
@click.option("-m", "--max-files", type=int, default=-1, help="Stop processing after this maximum number of files.")
@click.option("-s", "--save-dataframe", is_flag=True, help="Also save the data to shapefile and geoparquet.")
@click.argument(
    "inputdir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
def list_metadata(collection_config, glob, inputdir, max_files, save_dataframe):
    """List intermediary asset metadata, one for each GeoTIFF.

    You can optionally save the metadata as a shapefile and geoparquet so you
    can inspect the bounding boxes as well as the data.
    """
    CLICommands.list_asset_metadata(
        collection_config_path=collection_config,
        glob=glob,
        input_dir=inputdir,
        max_files=max_files,
        save_dataframe=save_dataframe,
    )


@cli.command
@click.option(
    "-g", "--glob", default="*", type=click.STRING, help="glob pattern to collect the GeoTIFF files. example */*.tif"
)
@click.option(
    "-c",
    "--collection-config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Configuration file for the collection",
)
@click.option("-m", "--max-files", type=int, default=-1, help="Stop processing after this maximum number of files.")
@click.option("-s", "--save-dataframe", is_flag=True, help="Also save the data to shapefile and geoparquet.")
@click.argument(
    "inputdir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
def list_items(collection_config, glob, inputdir, max_files, save_dataframe):
    """List generated STAC items.

    You can optionally save the metadata as a shapefile and geoparquet so you
    can inspect the bounding boxes as well as the data.
    """
    CLICommands.list_stac_items(
        collection_config_path=collection_config,
        glob=glob,
        input_dir=inputdir,
        max_files=max_files,
        save_dataframe=save_dataframe,
    )


@cli.command
@click.argument("collection_file", type=click.Path(exists=True, dir_okay=False, file_okay=True))
def show_collection(collection_file):
    """Read the STAC collection file and display its contents.

    You can use this to see if it can be loaded.
    """
    CLICommands.load_collection(collection_file)


@cli.command
@click.argument("collection_file", type=click.Path(exists=True, dir_okay=False, file_okay=True))
def validate(collection_file):
    """Run STAC validation on the collection file."""
    CLICommands.validate_collection(collection_file)


@cli.command
@click.argument("collection_file", type=click.Path(exists=True, dir_okay=False, file_okay=True))
def extract_item_bboxes(collection_file):
    """Extract and save the bounding boxes of the STAC items in the collection, to both ShapeFile and GeoParquet format."""
    CLICommands.extract_item_bboxes(collection_file)


@cli.command
@click.option(
    "-o",
    "--outputdir",
    required=False,
    type=click.Path(dir_okay=True, file_okay=False),
)
@click.option(
    "-c",
    "--collection-config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Configuration file for the collection",
)
@click.argument("collection_file", type=click.Path(exists=True, dir_okay=False, file_okay=True))
def post_process(outputdir, collection_config, collection_file):
    """Run only the postprocessing.

    Optionally saves the postprocessing result as a separate collection so you
    can re-run easily.
    You make have to do that many times when debugging postpreocessing
    and waiting for collections to be build is annoying.
    """
    CLICommands.postprocess_collection(
        collection_file=collection_file, collection_config_path=collection_config, output_dir=outputdir
    )


@cli.command
@click.option("-b", "--backend-url", type=click.STRING, help="URL for openEO backend", default="openeo-dev.vito.be")
@click.option(
    "-o",
    "--out-dir",
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    help="Directory to save batch jobs outputs (GTIFF)",
    default=".",
)
@click.option("--bbox", type=click.STRING, default="", help="bounding box")
@click.option("-e", "--epsg", type=int, help="CRS of bbox as an EPSG code")
@click.option(
    "-m", "--max-extent-size", type=float, default=0.0, help="Maximum size of the spatial extent (in degrees)"
)
@click.option("--start-dt", type=click.STRING, help="Start date+time of the temporal extent")
@click.option("--end-dt", type=click.STRING, help="End date+time of the temporal extent")
@click.option("-n", "--dry-run", is_flag=True, help="Do a dry-run, don't execute the batch job")
@click.option("-v", "--verbose", is_flag=True, help="Make output more verbose")
@click.argument(
    "collection_file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
def test_openeo(backend_url, out_dir, collection_file, bbox, epsg, max_extent_size, start_dt, end_dt, dry_run, verbose):
    """Test STAC collection via load_stac in openEO.

    It guesses a reasonable spatial and temporal extent based on what
    extent the collection declares.
    """
    if bbox:
        bbox = json.loads(bbox)

    temp_start_dt = dateutil.parser.parse(start_dt) if start_dt else None
    temp_end_dt = dateutil.parser.parse(end_dt) if end_dt else None

    start_datetime = dt.datetime(
        temp_start_dt.year,
        temp_start_dt.month,
        temp_start_dt.day,
        temp_start_dt.hour,
        temp_start_dt.minute,
        temp_start_dt.second,
        temp_start_dt.microsecond,
        tzinfo=dt.timezone.utc,
    )
    end_datetime = dt.datetime(
        temp_end_dt.year,
        temp_end_dt.month,
        temp_end_dt.day,
        temp_end_dt.hour,
        temp_end_dt.minute,
        temp_end_dt.second,
        temp_end_dt.microsecond,
        tzinfo=dt.timezone.utc,
    )

    print(f"CLI test_openeo:: {start_datetime=}")
    print(f"CLI test_openeo:: {end_datetime=}")

    verify_in_openeo(
        backend_url=backend_url,
        collection_path=collection_file,
        output_dir=out_dir,
        bbox=bbox,
        epsg=epsg,
        max_spatial_ext_size=max_extent_size,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        dry_run=dry_run,
        verbose=verbose,
    )


#
# Subcommands for working with the HRL VPP pipeline"""
#


@cli.group
def hrlvpp():
    """Subcommands for the HRL VPP pipeline"""
    pass


@hrlvpp.command
def vpp_list_metadata():
    """Show the AssetMetadata objects that are generated for each VPP product.

    This is used to test the conversion and check the configuration files.
    """
    HRLVVPCliCommands.list_metadata()


@hrlvpp.command
@click.option(
    "-c",
    "--collection-config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Configuration file for the collection",
)
@click.option(
    "-m", "--max-products", type=int, default=-1, help="Stop processing after this maximum number of products."
)
# @click.option("-s", "--save-dataframe", is_flag=True, help="Also save the data to shapefile and geoparquet.")
def vpp_list_items(collection_config: str, max_products: int):
    """Show the STAC items that are generated for each VPP product.

    This is used to test the conversion and check the configuration files.
    """
    HRLVVPCliCommands.list_stac_items(collection_config_path=collection_config, max_products=max_products)


@hrlvpp.command
def vpp_build():
    """Build a STAC collection for one of the collections in HRL VPP (OpenSearch)."""
    HRLVVPCliCommands.build_hrlvpp_collection()


#
# Subcommands for working with the collection configuration file.
# Mostly to validate and troubleshoot the configuration.
#


@cli.group
def config():
    """Subcommands for collection configuration."""
    pass


@config.command
def schema():
    """Show the JSON schema for CollectionConfig files or objects."""
    schema = CollectionConfig.model_json_schema()
    click.echo(pprint.pformat(schema, indent=2))


@config.command
@click.argument("config_file", type=click.Path(exists=True, dir_okay=False, file_okay=True))
def validate_config(config_file):
    """Check whether a collection configuration file is in the correct format.
    This only checks if the format is valid. It can not check whether the contents make sense.
    """
    config_file = Path(config_file)
    if not config_file.exists():
        raise FileNotFoundError(f"config_file could not be found. {config_file=}")

    try:
        CollectionConfig.from_json_file(config_file)
    except pydantic.ValidationError as exc:
        click.echo(click.style("ERROR: NOT VALID: \n" + str(exc), fg="red"))
    else:
        click.echo(click.style("OK: is valid configuration file", fg="green"))


@config.command
@click.argument("config_file", type=click.Path(exists=True, dir_okay=False, file_okay=True))
def show_config(config_file):
    """Read the config file and show how the parsed contents.

    This is a way to check if you are getting what you expected from the configuration.
    This may be important for things like asset and band names, titles and descriptions.
    """
    config_file = Path(config_file)
    if not config_file.exists():
        raise FileNotFoundError(f"config_file could not be found. {config_file=}")

    try:
        configuration = CollectionConfig.from_json_file(config_file)
    except pydantic.ValidationError as exc:
        click.echo(click.style("ERROR: NOT VALID: \n" + str(exc), fg="red"))
    else:
        pprint.pprint(configuration.model_dump(), indent=2, width=160)
        # print(json.dumps(configuration.model_dump(), indent=2))


@config.command
def docs():
    click.echo(CollectionConfig.__doc__)

    schema = CollectionConfig.model_json_schema()
    click.echo(pprint.pformat(schema, indent=2))

    def show_descriptions(schema_dict, path=None):
        for key, value in schema_dict.items():
            if not path:
                path = [key]

            if key == "description":
                print(path, value)
            if isinstance(value, dict):
                path.append(key)
                show_descriptions(value, path)

    show_descriptions(schema)


if __name__ == "__main__":
    cli()
