#!/bin/bash

command="$1"
services="$2"
microservices="userservice productservice paymentservice orderservice wallet"
POD_PREFIX="ingress-nginx-controller-"

check_kind_kubectl() {

    if ! command -v kubectl &> /dev/null; then
        echo "kubectl is not installed. Please install kubectl before running this script."
        exit 1
    fi
    if ! command -v kind &> /dev/null; then
        echo "Kind is not installed. Please install Kind before running this script."
        exit 1
    fi
}

# Function to check the pod status
check_ingress_status() {
    local pod

    # Get the pod with the specified prefix in the namespace
    pod=$(kubectl get pods -n ingress-nginx --field-selector=status.phase!=Succeeded --output=jsonpath="{.items[0].metadata.name}" | grep "^$POD_PREFIX")

    if [[ -n "$pod" ]]; then
        local status

        # Get the status of the pod
        status=$(kubectl get pod -n ingress-nginx "$pod" -o jsonpath='{.status.phase}')

        # Print the pod name and status
        echo "Pod $pod is $status. Waiting for 10s"

        # Check if the pod is in the "Running" state
        if [[ "$status" == "Running" ]]; then
            return 0
        fi
    fi

    return 1
}

load_docker_images() {
  for service in $microservices; do
            if docker image inspect "$service:latest" &> /dev/null; then
              kind load docker-image $service:latest --name=$kind_cluster_name
            else
              echo "Docker image $service:latest does not exist."
            fi
          done
}

case $command in
    "-h")   

echo -e "Available commands:
\ndocker:\n images\n <one_by_one> - userservice, productservice, paymentservice, orderservice, wallet
\nkubernetes:\n kind -n <kind_cluster_name>\n delete -n <kind_cluster_name>
\nload images -n <kind_cluster_name>
\nhelm deploy -r <release_name>:\n  eshop, wallet\nhelm delete -r <release_name>:\n  eshop, wallet
\nkubectl apply <release_name>:\n eshop, wallet\nkubectl delete <release_name>:\n eshop, wallet
\nssl -d <domain_name>
"
       
    ;;
    "docker")   
      for service in $microservices; do
        if [[ "$services" == "images" || "$services" == "$service"  ]]; then
          if [[ -d "$service" ]]; then

          echo "build $service"

          cd "$service"
          docker build -t "$service" .
          cd ..

          else
            echo "Invalid service: $services"
            echo "Available commands: 
            to build all: images
            one by one: userservice, productservice, paymentservice, orderservice, wallet"
       
        fi      
    fi
    done
    ;;
    "kubernetes")
      if [[ "$services" == "kind"  &&  "$3" == "-n"  &&  "$4" != "" ]]; then
        kind_cluster_name="$4"
        
        check_kind_kubectl

        if kind get clusters | grep -q "$kind_cluster_name"; then
          echo "A Kind cluster with the name $kind_cluster_name already exists."
          exit 1
        fi

        # Create a Kind cluster
        kind create cluster --name "$kind_cluster_name"

        kind export kubeconfig --name $kind_cluster_name

        #Verify kind cluster is imported
        kubectl config current-context
        echo
        # Verify cluster creation
        kubectl cluster-info
        echo
        echo "Kind cluster ---> $kind_cluster_name <--- created successfully."
        echo
        echo "Deploy Ingress-Nginx into Kind Kubernetes cluster"
        # Deploy Nginx-Ingress to Kind kubernetes
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml
        
        # Check the status of the ingress-nginx
        while true; do
          if check_ingress_status; then
            break
          fi
          sleep 10
        done

        echo
        echo "Configure Ingress-Nginx to act as a local"
        kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec":{"externalTrafficPolicy":"Local"}}'
        echo 
        echo "Nginx-Ingress is deployed."
        echo
        namespaces=(
            "eshop"
            "wallet"            
          )

        for ns in "${namespaces[@]}"; do
          kubectl create namespace "$ns"
        done

        

        echo "Kind cluster ---> $kind_cluster_name <--- is prepared for usage."

      elif [[ "$services" == "delete"  &&  "$3" == "-n"  &&  "$4" != "" ]]; then
        kind_cluster_name="$4"
  
        if ! kind get clusters | grep -q "$kind_cluster_name"; then
          echo -e "A Kind cluster with the name $kind_cluster_name doesnt exist.\nPlease check available kind clusters with the command - kind get clusters"
          exit 1
        fi

        kind delete cluster --name "$kind_cluster_name"
        echo "Kind cluster ---> $kind_cluster_name <--- is deleted."
        echo

        #Show available kind clusters
        echo "Available kind clusters."
        kind get clusters
        echo
        #Show available contexts from kubeconfig
        echo "Available k8s context in your kubeconfig."
        kubectl config get-contexts
      else
        echo -e "Available commands:\nkubernetes kind -n <kind_name>\nkubernetes delete -n <kind_name>"
      fi
    ;;
    "load")
      if [[ "$services" == "images" &&  "$3" == "-k"  &&  "$4" != "" ]]; then
        kind_cluster_name="$4"
        if ! kind get clusters | grep -q "$kind_cluster_name"; then
          echo -e "A Kind cluster with the name $kind_cluster_name doesnt exist.\nPlease check available kind clusters with the command - kind get clusters"
          exit 1
        else
          load_docker_images
        fi
      else
          echo -e "Available commands:\nload images -k <kind_cluster_name>"
      fi
    ;;
      "helm")

      if ! command -v helm &> /dev/null; then
        echo "Helm is not installed. Please install Helm before running this script."
        exit 1
      fi

      if [[ "$services" == "deploy" && "$3" == "-r"  && ( "$4" == "eshop" || "$4" == "wallet" ) ]]; then
        release="$4"
        missing_images=0
        kind_node_name=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')


        for service in $microservices; do
         # Execute the command inside the Kind control plane container
          docker exec -it $kind_node_name bash -c 'crictl images' | grep -E $service  &> /dev/null
          # Check the exit code of the previous command
          if [ ! $? -eq 0 ]; then
            echo "There is no images with the name $service. Please load your images into kind cluster." >&2  
            missing_images=1
          fi
        done

        if [ $missing_images -eq 1 ]; then
          exit 1
        fi

        helm install $release helm/$release/ -n $release
        echo -e "Helm release is deployed. Please run kubectl get pods -n $release to see the status"

      elif [[ "$services" == "delete" && "$3" == "-r"  && ( "$4" == "eshop" || "$4" == "wallet" ) ]]; then
        release="$4"
        helm uninstall $release -n $release
        echo -e "Helm release is deleted. Please run kubectl get pods -n $release or kubectl get svc -n $release  to see the status"

      else
      echo -e "Available commands:\nhelm deploy -r <release_name>:\n eshop, wallet\nhelm delete -r <release_name>:\n eshop, wallet"
      fi
    ;;
      "ssl")
      if [[  "$services" == "-d"  &&  "$3" != ""  ]]; then
      domain="$3"

      # Set the certificate and key filenames
      cert_file="ssl.crt"
      key_file="ssl.key"

      # Generate a private key
      openssl genrsa -out "$key_file" 2048

      # Generate a certificate signing request (CSR)
      openssl req -new -key "$key_file" -out csr.csr -subj "/CN=$domain"

      # Generate a self-signed certificate valid for 365 days
      openssl x509 -req -days 3650 -in csr.csr -signkey "$key_file" -out "$cert_file"

      # Cleanup the CSR file
      rm csr.csr
      ssl_crt_encoded=$(cat $cert_file | base64 -w 0)
      ssl_key_encoded=$(cat $key_file | base64 -w 0)

      # Print the paths to the generated certificate and key
      echo "SSL certificate and key files generated:"
      echo "Certificate: $(pwd)/$cert_file"
      echo "Key: $(pwd)/$key_file"

      echo -e "\ncrt base64 encoded: $ssl_crt_encoded"
      echo -e "\nkey base64 encoded: $ssl_key_encoded"  
      else
        echo -e "Available commands:\nssl -d <domain_name>"
      fi
      ;;
      "kubectl")

        eshop="userservice productservice paymentservice orderservice mongodb"
        wallet="wallet postgresql"
        if [[ "$services" == "apply" || "$services" == "delete"  ]]; then
          if [[ "$3" == "eshop" ]]; then
            release=$eshop
          elif [[ "$3" == "wallet" ]]; then
            release=$wallet
          fi

          for service in $release; do
            # Apply all yaml files with kubectl
            for yaml_file in $service/k8s/*.yaml; do
              kubectl $services -f "$yaml_file" -n $3
            done
          done
        else
          echo -e "Available commands:\nkubectl apply <release_name>:\n eshop, wallet\nkubectl delete <release_name>:\n eshop, wallet"
        fi

      ;; 
    *)
    echo -e "Please run setup.sh -h to see available commands"
    exit 1
    ;;
esac