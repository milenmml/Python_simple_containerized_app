# Python_simple_containerized_app / URL checker

This project creates a simple Python service that queries two URLs and checks their status and response time. The service runs an HTTP server that produces metrics in Prometheus format.

## Running the Service in Kubernetes

### Prerequisites

- Ensure you have a Kubernetes cluster up and running.
- Install Helm on your local machine.
- Ensure you are on the proper Kubernetes context:
  ```bash
  kubectl config current-context
- If the context is incorrect, switch to the correct context:
  ```bash
  kubectl config use-context <your-context>

### Steps

1. **Build Docker Image**
   ```bash
   docker build -t <your-docker-registry>/url-checker .

2. **Build and Tag Docker Image**
   ```bash
   docker build -t <your-docker-registry>/url-checker:latest .

3. **Push Docker Image to Registry**
   ```bash
   docker push <your-docker-registry>/url-checker:latest

4. **Update image in Helm Chart values.yaml**
   ```bash
   image:
     repository: <your-docker-registry>/url-checker
     tag: 1

Alternatively, you can use the default image specified in the Helm chart.

5. **Deploy to Kubernetes**

Install the Helm chart:
   ```bash
   helm install url-checker ./url-checker -n url-checker --create-namespace
   ```

6. **Access the Service**

Find the NodePort assigned to your service (default is 30001):
   ```bash
   kubectl get services -n url-checker
   ```

Access the metrics at `http://<your-k8s-node-ip>:30001/metrics`.

Alternatively, if your cluster is not accessible from your PC, use `kubectl port-forward`:
   ```bash
   kubectl port-forward svc/url-checker 30001:9001 -n url-checker
   ```
Then access the metrics at `http://localhost:30001/metrics`.

**Accessing Metrics**

Once the service is running, access the metrics at `http://<your-k8s-node-ip>:30001/metrics` or `http://localhost:30001/metrics` if using port-forwarding.