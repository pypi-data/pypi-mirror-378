class KubernetesController:
    def __init__(self, config_path):
        def load_kubeconfig(config_path):
            from kubernetes import config, client
            config.load_kube_config(config_file=config_path)
            return client.CoreV1Api()

        self.api = load_kubeconfig(config_path)

    def get_my_pod_spec(self):
        import os
        
        # 1. HOSTNAME으로 직접 pod 조회 (가장 효율적)
        hostname = os.environ.get("HOSTNAME")
        if not hostname:
            print("[DEBUG] HOSTNAME environment variable not found")
            return None
        
        namespace = "airflow"  # 기본값
        
        # 3. 직접 pod 조회 시도
        try:
            pod = self.api.read_namespaced_pod(name=hostname, namespace=namespace)
            print(f"[DEBUG] Found pod {hostname} in namespace {namespace}")
            return pod
        except Exception as e:
            print(f"[DEBUG] Failed to get pod {hostname} in {namespace}: {e}")
        
        # 4. Fallback: 현재 namespace에서 HOSTNAME과 매칭되는 pod 찾기
        try:
            pods = self.api.list_namespaced_pod(namespace=namespace)
            for pod in pods.items:
                if pod.metadata.name == hostname and pod.status.phase in ["Running", "Pending"]:
                    print(f"[DEBUG] Found pod by name match: {hostname}")
                    return pod
        except Exception as e:
            print(f"[DEBUG] Failed to list pods in {namespace}: {e}")
        
        # 5. 최종 Fallback: Airflow task pod 특성으로 찾기
        try:
            pods = self.api.list_namespaced_pod(
                namespace=namespace,
                field_selector="status.phase=Running"
            )
            for pod in pods.items:
                if (pod.metadata.labels and 
                    any(key in pod.metadata.labels for key in ["dag_id", "task_id", "run_id"])):
                    print(f"[DEBUG] Found airflow task pod: {pod.metadata.name}")
                    return pod
        except Exception as e:
            print(f"[DEBUG] Final fallback failed: {e}")
        
        print(f"[DEBUG] No suitable pod found for hostname: {hostname}")
        return None
    

    def get_pod_namespace(self, pod_spec):
        return pod_spec.metadata.namespace

    def get_my_pod_namespace(self):
        return self.get_pod_namespace(self.get_my_pod_spec())

    def get_pod_selector(self, pod_spec, key):
        return pod_spec.metadata.labels[key]

    def get_my_pod_app_selector(self):
        return self.get_pod_selector(self.get_my_pod_spec(), "app")

    def get_list_used_nodeport(self):
        used_ports = []
        services = self.api.list_service_for_all_namespaces(watch=False)
        for service in services.items:
            if service.spec.type == "NodePort":
                for port in service.spec.ports:
                    used_ports.append(port.node_port)
        return used_ports

    def get_available_ports(self, start=32000, end=32600, count=1):
        import random
        used_ports = self.get_list_used_nodeport()
        port_range = range(start, end + 1)
        ports = [port for port in port_range if port not in used_ports]
        return random.sample(ports, count)

    def create_spark_nodeport(self, namespace, service_name, app_name, driver_port, blockmanager_port):
        from kubernetes import client
        service = client.V1Service(api_version="v1",
                                   kind="Service",
                                   metadata=client.V1ObjectMeta(name=service_name),
                                   spec=client.V1ServiceSpec(selector={"app": app_name},
                                                             type="NodePort",
                                                             ports=[client.V1ServicePort(name="driver-port",
                                                                                         protocol="TCP",
                                                                                         port=driver_port,
                                                                                         target_port=driver_port,
                                                                                         node_port=driver_port),
                                                                    client.V1ServicePort(name="blockmanager-port",
                                                                                         protocol="TCP",
                                                                                         port=blockmanager_port,
                                                                                         target_port=blockmanager_port,
                                                                                         node_port=blockmanager_port)]
                                                             )
                                   )
        self.api.create_namespaced_service(namespace=namespace, body=service)

    def remove_spark_nodeport(self, namespace, service_name):
        self.api.delete_namespaced_service(service_name, namespace)
