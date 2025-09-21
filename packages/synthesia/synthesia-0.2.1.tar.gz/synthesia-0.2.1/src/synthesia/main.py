from importlib import resources
from typing import Annotated

import dlt
from dlt.destinations import bigquery
import pandas as pd
import typer
from synthesia.helpers import dbt

app = typer.Typer()


@app.command()
def main(dataset: str, target_schema: Annotated[str, typer.Option()], credentials_from_dbt: bool = False):
    datasets_location = resources.files("synthesia.datasets")
    datafile_paths = datasets_location.glob(f"{dataset}/*.csv")
    if credentials_from_dbt:
        credentials = dbt.get_credentials_from_current_project()
    else:
        credentials = None
    for path in datafile_paths:
        df = pd.read_csv(path, engine="pyarrow")
        table_name = path.stem
        pipeline = dlt.pipeline(
            pipeline_name=f"{dataset}.{table_name}".replace(".", "_"),
            destination=bigquery(location="EU", credentials=credentials),
            dataset_name=target_schema,
        )
        load_info = pipeline.run(df, table_name=table_name)
        print(load_info)


if __name__ == "__main__":
    typer.run(main)
