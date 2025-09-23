from typing import (Any, Dict)
from pyspark.sql import SparkSession

class SparkSessionBuilder:
    def __init__(self, k8s_config="~/.kube/ciap_prd.conf") -> None:
        from datetime import datetime
        from pyspark import SparkConf
        from cidpaf.kube import KubernetesController
        import uuid
        self.spark_session = None
        self._k8s_api = KubernetesController(k8s_config)
        self._timestamp = datetime.now().strftime("%Y%m%d%H%M")
        self._suffix = uuid.uuid4().hex[:8]
        self._app_id = f"{self._timestamp}-{self._suffix}"
        self._service_name = f"spark-{self._app_id}"
        self._options = SparkConf()
        self._my_namespace = self._k8s_api.get_my_pod_namespace()
        self._my_appname = self._k8s_api.get_my_pod_app_selector()
        self.appName(f"{self._my_appname}-{self._app_id}")

    def config(self, k: str, v: Any) -> "SparkSessionBuilder":
        self._options.set(k, v)
        return self

    def master(self, master: str) -> "SparkSessionBuilder":
        return self.config("spark.master", master)

    def appName(self, name: str) -> "SparkSessionBuilder":
        return self.config("spark.app.name", name)

    def getOrCreate(self) -> SparkSession:
        def get_spark_nodeports():
            return self._k8s_api.get_available_ports(count=2)

        driver_port, blockmanager_port = get_spark_nodeports()
        self._k8s_api.create_spark_nodeport(self._my_namespace,
                                            self._service_name,
                                            self._my_appname,
                                            driver_port,
                                            blockmanager_port)
        (self.config("spark.driver.host", f"{self._my_appname}-{self._app_id}.spark-endpoint.cidp.io")
         .config("spark.driver.port", driver_port)
         .config("spark.blockManager.port", blockmanager_port))

        from pyspark.sql import SparkSession
        if self.spark_session is None:
            self.spark_session = SparkSession.builder.config(conf=self._options).getOrCreate()
        return self.spark_session
