from infdb import InfDB

def main():

    # Load InfDB handler
    infdbhandler = InfDB(tool_name="test")

    # Database connection
    infdbclient_citydb = infdbhandler.connect(db_name="citydb")

    # Logger setup
    infdblog = infdbhandler.get_log()

    # Start message
    infdblog.info(f"Starting {infdbhandler.get_toolname()} tool")

    # Get configuration values
    input_schema = infdbhandler.get_config_value(["test", "data", "input_schema"])
    output_schema = infdbhandler.get_config_value(["test", "data", "output_schema"])




if __name__ == "__main__":
    main()