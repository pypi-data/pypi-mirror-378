LOG_EXECUTION_STARTED = "execution started."
LOG_EXECUTION_COMPLETED = "execution completed."
LOG_EXECUTION_FAILED = "execution failed."

SPARK_DEFAULT_PACKAGES = [
    # "com.amazonaws:aws-java-sdk-bundle:1.12.723",
    "com.amazonaws:aws-java-sdk-bundle:1.12.262",  # this version use with hadoop 3.3.4
    "org.apache.hadoop:hadoop-aws:3.3.4",
    "org.apache.hadoop:hadoop-azure:3.3.4",
    "com.azure:azure-storage-blob:12.31.2",
    "org.postgresql:postgresql:42.7.8",
    "com.microsoft.sqlserver:mssql-jdbc:13.2.0.jre11",
    "org.mongodb.spark:mongo-spark-connector_2.13:10.5.0",
    "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1",
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",  # pinned this for spark 3.5.0
]
