"""
InforCOM ETL Adapter Main Entry Point.

This module serves as the main entry point for the InforCOM ETL adapter, which handles
the extraction, transformation, and loading of data from InforCOM systems into Nemo.
"""
from nemo_library_etl.adapter.inforcom.flow import inforcom_flow

def main() -> None:
    """
    Main function to execute the InforCOM ETL flow.

    This function initiates the complete InforCOM ETL process by calling the InforCOM_flow
    function, which orchestrates the extract, transform, and load operations.
    """
    inforcom_flow()


if __name__ == "__main__":
    main()
