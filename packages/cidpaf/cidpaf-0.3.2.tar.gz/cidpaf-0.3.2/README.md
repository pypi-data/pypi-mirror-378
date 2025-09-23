# CIDPAF

CIDPAF는 Kubernetes와 Spark 통합을 위한 유틸리티 라이브러리입니다. Airflow 환경에서 Kubernetes 리소스를 관리하고 Spark 세션을 효율적으로 생성할 수 있는 도구를 제공합니다.

## 특징

- **Kubernetes 통합**: Kubernetes 클러스터와의 상호작용을 위한 간편한 API
- **Spark 세션 관리**: 동적 포트 할당과 서비스 생성을 통한 Spark 세션 빌더
- **Airflow 최적화**: Airflow 환경에서 최적화된 워크플로우 지원

## 설치

PyPI에서 패키지를 설치할 수 있습니다:

```bash
pip install cidpaf
```

## 사용법

### Kubernetes Controller

```python
from cidpaf import KubernetesController

# Kubernetes 설정 파일로 컨트롤러 초기화
k8s_controller = KubernetesController("~/.kube/config")

# 현재 Pod의 네임스페이스 가져오기
namespace = k8s_controller.get_my_pod_namespace()

# 사용 가능한 NodePort 가져오기
available_ports = k8s_controller.get_available_ports(count=2)

# Spark NodePort 서비스 생성
k8s_controller.create_spark_nodeport(
    namespace=namespace,
    service_name="my-spark-service",
    app_name="my-app",
    driver_port=4040,
    blockmanager_port=4041
)
```

### Spark Session Builder

```python
from cidpaf import SparkSessionBuilder

# Spark 세션 빌더 생성
spark_builder = SparkSessionBuilder(k8s_config="~/.kube/config")

# Spark 세션 설정 및 생성
spark = (spark_builder
         .master("k8s://https://kubernetes.default.svc:443")
         .config("spark.executor.instances", "2")
         .config("spark.executor.memory", "2g")
         .getOrCreate())

# Spark 작업 수행
df = spark.read.csv("s3a://my-bucket/data.csv", header=True)
df.show()
```

## 요구사항

- Python 3.7+
- kubernetes>=18.0.0
- pyspark>=3.0.0

## 개발

개발 환경 설정:

```bash
git clone https://gitlab.cidp.io/common/pypi/cidpaf.git
cd cidpaf
pip install -e .
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 지원

이슈나 질문이 있으시면 [GitLab Issues](https://gitlab.cidp.io/common/pypi/cidpaf/-/issues)를 통해 문의해 주세요.

## 기여

기여를 환영합니다! Pull Request를 보내기 전에 이슈를 통해 먼저 논의해 주세요.
