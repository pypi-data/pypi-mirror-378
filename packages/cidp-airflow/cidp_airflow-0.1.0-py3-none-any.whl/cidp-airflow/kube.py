class KubernetesController:
    def __init__(self, config_path):
        def load_kubeconfig(config_path):
            from kubernetes import config, client
            config.load_kube_config(config_file=config_path)
            return client.CoreV1Api()

        self.api = load_kubeconfig(config_path)

    def get_my_pod_spec(self):
        import os
        pods = self.api.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            if pod.metadata.labels is not None and pod.metadata.labels.get("statefulset.kubernetes.io/pod-name",
                                                                           "none") == os.environ["HOSTNAME"]:
                return pod

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
