# eShop Microservices

This project offers a foundation for understanding microservice architecture and its management. It employs `Python Flask` for creating the microservices, with `MongoDB` and `PostgreSQL` databases to support data storage needs.

The project is designed to operate in a `docker-compose` network or to be deployed on a `Kubernetes` cluster, both of which are detailed in this guide. Furthermore, a provided `setup.sh` bash script functions as a CLI tool, streamlining the project setup process.

Please ensure to follow all steps in this documentation for successful execution.

## Requirements

| Required Technology                   | Installation Guide                                                  |
|---------------------------------------|--------------------------------------------------------------------|
| Docker                                | [Docker Installation Guide](https://docs.docker.com/get-docker/)   |
| Docker-compose                        | [Docker Compose Installation Guide](https://docs.docker.com/compose/install/) |
| Kubectl - commands against Kubernetes | [kubectl Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/) |
| Kind - Kubernetes local cluster       | [kind Installation Guide](https://kind.sigs.k8s.io/docs/user/quick-start/) |
| Helm - Kubernetes package manager     | [Helm Installation Guide](https://helm.sh/docs/intro/install/)      |

<details>

 <summary>Requirements - what is what?</summary>

`docker` - with docker we can compile our code and run inside a docker container isolated from the local environment.

`docker-compose` - with docker compose we can run our docker containeres all together which can be reachable inside docker-compose network.

`kubectl` - command line tool which can be run aginst desired kubernetes cluster.

`kind` - lightweight kubernetes cluster which is run as a single node (control-plane node) inside docker container. Its a very easy and usefull tool for creating kubernetes cluster in a local environment

`helm` - package manager for kubernetes resources. Our microservices can be deployed with kubectl - one by one configuration. With helm we can group them into release packages, apply versioning and deployed them all together.

`Bash interpreter (Windows environment)` - If you are running this project on Windows, you need to install bash interpreter.

   - When you install Git on Windows using the official Git for Windows distribution, it does include a software package known as Git Bash. Git Bash is an application that provides Git command-line features on Windows, using Bash emulation.

   - Git: It's a distributed version control system used to track file changes in a project over time.

   - Bash: It's a Unix shell and command language.

   - Git Bash: This is an application for Microsoft Windows environments, which is an emulation of a Bash environment. Git commands can be executed in this shell, along with Unix command utilities such as ssh, scp, cat, find etc.

   - A form of Bash interpreter is installed along with Git on Windows when using Git Bash. It allows you to use most of the common UNIX and Bash commands on Windows.

</details>


## Running the project

The project can be run easily in:

   - docker-compose
   - Kubernetes Kind with kubectl
   - Kubernetes Kind with Helm

This project offers a versatile learning platform, adaptable to three distinct deployment methods - Docker Compose, Kubernetes (kind) via kubectl, and Kubernetes (kind) using Helm. 

Each approach provides a unique perspective and understanding, collectively furnishing a comprehensive overview of microservice deployment strategies.

I've included a helpful Bash script, `./setup.sh`, designed to streamline your setup process, thus enabling you to focus more on the learning aspects. 

Whether you are exploring Docker Compose intricacies, kubectl's command-line interface, or Helm's package management capabilities, this script will guide you smoothly through the initial stages.


To find more about **setup.sh** , please run:

>  ./setup.sh -h 

To start with the project, please build all the docker images with command:

> ./setup.sh docker images

All the details how to run the project in docker-compose and access the services, please [Go to eShop Project - Docker Compose section](#eshop-project-docker-compose)

All the details how to create Kubernetes Kind cluster please [Go to eShop Project - Kubernetes Kind section](#eshop-project-kubernetes-kind)

All the details how to deploy to Kubernetes Kind with kubectl please [Go to eShop Project - Kubectl Deployment section](#eshop-project-kubectl-deployment)

All the details how to deploy to Kubernetes Kind with Helm please [Go to eShop Project - Helm Deployment section](#eshop-project-helm-deployment)

SSL self-siogned is included in nginx-ingress manifests with domain `*.eshop.com` and they are base64 encoded. Duration is set to 10y. 

If you want you can create new SSL with the command:

> ./setup.sh ssl -d <domain_name>

   - it will print you base64 encoded cert and key
   - please update nginx-ingress manifests with new values

Database credentials are included as kubernetes secret manifests and they are base64 encoded.

<details>

  <summary>eShop Project - Directory Structure</summary>


```
    microservices/
    ├── docker-compose.yaml
    ├── helm/
    │   ├── eshop/
    │   └── wallet/
    ├── mongodb/
    │   └── k8s/
    ├── orderservice/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── k8s/
    ├── paymentservice/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── k8s/
    ├── productservice/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── k8s/
    ├── postgresql/
    │   └── k8s/
    ├── setup.sh
    └── userservice/
        ├── app.py
        ├── requirements.txt
        ├── Dockerfile
        └── k8s/

```

The repository root houses all microservices, each featuring a Python Flask application, represented by `app.py`. Complementary to this, a `Dockerfile` alongside `requirements.txt` is provided for containerization purposes. 

Furthermore, Kubernetes deployments are facilitated through the `k8s/` directory present within each service.

Exclusively for `MongoDB` and `PostgreSQL`, Kubernetes manifests are available.

The `Helm` directory encompasses `eshop` and `wallet` subdirectories, functioning as release packages. `eshop` and `wallet` contains subcharts and their variables for deployment. Feel free to explore all the configuration.

SSL is included in nginx-ingress manifests and they are base64 encoded.
Database credentials are included as secret manifests and they are base64 encoded.

</details>


<details>

  <summary>eShop Project - Services Description</summary>



This eShop project presents a straightforward example of microservice architecture and inter-service communication. The key focus lies in creating an integrated microservice environment, fostering intercommunication, automation, and facilitating deployment to Docker Compose and Kubernetes clusters.

The eShop model operates on a microservices architecture, where distinct services handle specific functionalities. These services interact through HTTP using RESTful APIs, ensuring modularity, scalability, and maintainability of the system.


> `UserService:` Manages user creation and profile information. Its using Mongo DB.

> `ProductService:` Handles product management, including creation, retrieval, and availability. Its using Mongo DB.

> `WalletService:` WalletService is actually a simulation of the client bank or the place where client keeps his money. 
Its a seperated environment from the eShop. WalletService manages user wallets and handles funds deduction and addition. Its using PostgreSQL DB.

> `OrderService:` Handles order creation and retrieval for users. Its using Mongo DB.

> `PaymentService:` Integrates as a payment gateway acting in between Users, Products, Wallet and User Orders. It orchestrates the payment process., It doesnt have connection to any of the DB.


In the eShop project, the ``PaymentService`` acts as **the primary orchestrator** for customer transactions. It **doesnt have connection** to the **database**. 
PaymentService is running as a middleware in between other microservices.

Upon a purchase intent, a POST request is sent to the PaymentService. It facilitates several crucial validations. Firstly, it interacts with the UserService to verify the user's existence. Concurrently, it liaises with the ProductService to confirm product availability and pricing.

In tandem, the WalletService verifies the client's financial capacity and, upon successful verification, deducts the product's total price.

On receiving a successful response from all services, the PaymentService triggers the OrderService to finalize and store the order. This streamlined workflow, directed by the PaymentService, ensures efficient and secure transactions in the eShop project.

UserService, ProductService, WalletService and OrderService are running independantly. They have connection with the DB and based on the input parameters they will apply commands against DB.

### User Service

The User Service provides functionality for user creation and profile management. It allows users to create accounts and update their profile information.

|     Endpoint           | Method | Parameter      |                 cURL Command                              |
|------------------------|--------|----------------|-----------------------------------------------------------|
|   /users               |  POST  | user_name      | curl -X POST -H "Content-Type: application/json"          |
|                        |        | email          |      -d '{"user_name":"John", "email":"john@example.com", |
|                        |        | card_number    |           "card_number":"1234567890"}'                    |
|                        |        |                |      http://localhost:5000/users                          |
|   /users               |  GET   |                | curl http://localhost:5000/users                          |
|   /users/{user_id}     |  GET   | user_id        | curl http://localhost:5000/users/user123                  |
|   /health              |  GET   |                | curl http://localhost:5000/health                         |

### Product Service

The Product Service is responsible for managing products in the e-commerce system. It provides endpoints for creating new products, retrieving product details, updating the existing products and checking product availability.

|     Endpoint           | Method | Parameter      |                 cURL Command                              |
|------------------------|--------|----------------|-----------------------------------------------------------|
|   /products            |  GET   |                | curl http://localhost:5000/products                       |
|   /products            |  POST  | product_name   | curl -X POST -H "Content-Type: application/json"          |
|                        |        | price          |      -d '{"product_name":"Product1", "price":10,          |
|                        |        | quantity       |           "quantity":100}'                                |
|                        |        |                |      http://localhost:5000/products                       |
|   /products/deduct     |  POST  | product_name   | curl -X POST -H "Content-Type: application/json"          |
|                        |        | quantity       |      -d '{"product_name":"Product1", "quantity":10}'      |
|                        |        |                |      http://localhost:5000/products/deduct                |
|   /health              |  GET   |                | curl http://localhost:5000/health                         |

### Wallet Service

The Wallet Service manages User wallets. I thandles wallet creation. fund deduction and addition. It provides endpoints for deducting funds from a user's wallet and adding funds to a user's wallet.

|     Endpoint         | Method |   Parameter   |                      cURL Command                        |  
|----------------------|--------|---------------|----------------------------------------------------------|
|   /wallet            |  GET   |               | curl http://localhost:5000/wallet                        |          
|   /wallet/add        |  POST  |  user_name    | curl -X POST -H "Content-Type: application/json"         |     
|                      |        |  card_number  |      -d '{"user_name":"John", "card_number":"1234567890",|     
|                      |        |  amount       |           "amount":100}'                                 |         
|                      |        |               |      http://localhost:5000/wallet/add                    |            
|   /wallet/deduct     |  POST  |  user_name    | curl -X POST -H "Content-Type: application/json"         |            
|                      |        |  card_number  |      -d '{"user_name":"John", "card_number":"1234567890",|            
|                      |        |  amount       |           "amount":50}'                                  |              
|                      |        |               |      http://localhost:5000/wallet/deduct                 |             
|   /health            |  GET   |               | curl http://localhost:5000/health                        |             

### Order Service

The Order Service handles order creation and retrieval for users. It allows PaymentService to create new orders, retrieve their order history, and view the status of their orders.


|       Endpoint             | Method |   Parameter   |                      cURL Command                         |
|----------------------------|--------|---------------|-----------------------------------------------------------|
|   /orders                  |  POST  |  user_id      | curl -X POST -H "Content-Type: application/json"          |
|                            |        |  user_name    |      -d '{"user_id":"user123", "user_name":"John",        |
|                            |        |  product_name |           "product_name":"Product1", "quantity":10,       |
|                            |        |  quantity     |           "amount":100, "datetime":"2023-07-05T12:00:00"}'|
|                            |        |  amount       |      http://localhost:5000/orders                         |
|   /orders/user/{user_id}   |  GET   |  user_id      | curl http://localhost:5000/orders/user/user123            |
|   /orders                  |  GET   |               | curl http://localhost:5000/orders                         |
|   /health                  |  GET   |               | curl http://localhost:5000/health                         |

### Payment Service

The Payment Service integrates with the payment gateway and orchestrates the payment process. It receives payment requests from the clinet, verifies the order details, and processes the payment transaction against UserService, ProductService, WalletService and OrderService.

|     Endpoint    | Method |   Parameter   |                      cURL Command                        |
|-----------------|--------|---------------|----------------------------------------------------------|
|   /payment      |  POST  |  user_id      | curl -X POST -H "Content-Type: application/json"         |
|                 |        |  user_name    |      -d '{"user_id":"user123", "user_name":"John",       |
|                 |        |  card_number  |           "card_number":"1234567890", "product_name":    |
|                 |        |  product_name |           "Product1", "quantity":10}'                    |
|                 |        |  quantity     |      http://localhost:5000/payment                       |
|   /health       |  GET   |               | curl http://localhost:5000/health                        |


Here is the simplify workflow:

```

1. Client (POST Request)
   |
   V
2. Payment Service ---------> 3. Order Service (Check user existence in shared MongoDB)
   |  (200 OK if user exists)
   |
   V
4. Payment Service -----> 5. Wallet Service (Check user existence and funds. Wallets information are in separate PostgreSQL DB)
   |  (200 OK if user exists and has funds)
   |
   V
6. Payment Service -----> 7. Product Service (Check product existence and quantity in shared MongoDB)
   |  (200 OK if product exists and has enough quantity)
   |
   V
8. Payment Service -----> 9. Wallet Service (Deduct total price from user's wallet in separate PostgreSQL DB)
   |
   V
10. Payment Service -----> 11. Product Service (Deduct purchased quantity from product in shared MongoDB)
   |
   V
12. Payment Service -----> 13. Order Service (Creates order in shared MongoDB, only if user exists, has funds, product exists, and has enough quantity)
```

</details>


 <a id="eshop-project-docker-compose"></a>
<details>


  <summary>eShop Project - docker-compose</summary> 
   
   1. Checkout the code and build docker images buy running:
   
      > ./setup.sh docker images
   
      The script will go through microservice directories and build the docker images.

   2. Running the project in docker-compose environment

      > docker-compose up -d

      With -d flag, docker-compose will run all the containers in the background.

      You can reach all the services on the following ports:

      **UserService:** http://localhost:5000/users and http://localhost:5000/health to check if the service is running

      **ProductsService:** http://localhost:5001/products and http://localhost:5001/health to check if the service is running

      **PaymentService:** http://localhost:5002/payments and http://localhost:5002/health to check if the service is running

      **WalletService:** http://localhost:5003/wallets and http://localhost:5003/health to check if the service is running

      **OrderService:** http://localhost:5004/orders and http://localhost:5004/health to check if the service is running

      **MongoDB:** mongodb://localhost:2717/database_name

      **PostgreSQL:** postgresql://username:password@localhost:5432/walletdb


   3. Buy default, all the database (MongoDB and PostgreSQL) are empty. The very first thing is to create Users, Products and User Wallet.
      
      1. **Create User:**
         
         > curl -X POST -H "Content-Type: application/json" -d '{"user_name":"Michael", "email":"michael@example.com", "card_number":"123-456-7890"}' http://localhost:5000/users

      2. **Create Products:**

         > curl -X POST -H "Content-Type: application/json" -d '{"product_name":"Laptop", "price":890, "quantity":100}' http://localhost:5001/products

         > curl -X POST -H "Content-Type: application/json" -d '{"product_name":"Desktop", "price":1200, "quantity":100}' http://localhost:5001/products

         > curl -X POST -H "Content-Type: application/json" -d '{"product_name":"Mobile", "price":850.9, "quantity":100}' http://localhost:5001/products

      3. **Create Wallet for the User Michael:**

         curl -X POST -H "Content-Type: application/json" -d '{"user_name":"Michael", "card_number":"123-456-7890", "amount":120000}' http://localhost:5003/wallets/add

      4. **Buy the product with user Michael:**

         Get Michael ID from the DB:

         > http://localhost:5000/users -> [{"_id":"64a6b0a476d49ca2783f5fd2","card_number":"123-456-7890","email":"michael@example.com","user_name":"Michael"}]
         
         Buy the product: 

         > curl -X POST http://localhost:5002/payments -H "Content-Type: application/json" -d '{"user_id": "64a6b0a476d49ca2783f5fd2", "user_name": "Michael", "card_number": "123-456-7890", "product_name": "Mobile", "quantity": 1}'
      
      5. **Observe the following:**

         - eShop orders:

         > http://localhost:5004/orders

         - Wallet for user Michael

         >  http://localhost:5003/wallets

         - Quantity of the product:

         > http://localhost:5001/products




</details>


<a id="eshop-project-kubernetes-kind"></a>

<details>

  <summary>eShop Project - Kubernetes Kind</summary>


   1. Checkout the code and build docker images buy running:
   
      > ./setup.sh docker images
   
      The script will go through microservice directories and build the docker images.

   2. Create Kind kubernetes cluster

      > ./setup.sh kubernetes kind -n <cluster_name>

      With this command the script will: 

            - bootstrap kubernetes kind cluster
            - export kubectl config to use our cluster <cluster_name>
            - deploy Nginx Ingress to reroute the traffic to kubernetes services
            - create namespaces eshop and wallet
      
      Run the command and observe the output: 

      > kubectl get nodes

   3. Delete Kind kubernetes cluster

      > ./setup.sh kubernetes delete -n <cluster_name>

</details>


<a id="eshop-project-kubectl-deployment"></a>


<details>


   <summary>eShop Project - Kubectl deployment</summary>


   1. When docker images are builded, usually we need to push them to some docker registry. For the simplicity of this project, i decided to avoid docker registry and to push docker images from   local repository to our Kind kubernetes cluster. Kind is running under docker container and it doesnt have access to our file system. Thats why we need to push our images inside Kind cluster.

      > ./setup.sh load images -k <kind_cluster_name>

   2. Deploy eShop release package with Helm

      > ./setup.sh kubectl apply eshop
     
      check the pod status with command: 
      
      > kubectl get pods -n eshop

      check the svc status with command: 
      
      > kubectl get svc -n eshop

      check the ingress status with command: 
      
      > kubectl get ingress -n eshop

   
   3. Deploy Wallet release package with Helm

      > ./setup.sh kubectl apply wallet
     
      check the pod status with command: 

      > kubectl get pods -n wallet

      Note: when PostgreSQL is up and running, Wallet pod will be in the running state

      check the svc status with command:

      >  kubectl get svc -n wallet

      check the ingress status with command: 
      
      > kubectl get ingress -n wallet

   4. Forward Nginx Ingress traffic to be available from the localhost
      
      > kubectl port-forward service/ingress-nginx-controller 443:443 or 80:80 -n ingress-nginx
      
   5. Buy default, all the database (MongoDB and PostgreSQL) are empty. The very first thing is to create Users, Products and User Wallet.


      1. **Create User:**
         
        > curl -k -X POST -H "Host: users.eshop.com" -H "Content-Type: application/json" -d '{"user_name":"Michael", "email":"michael@example.com", "card_number":"123-
         456-7 890"}' https://localhost:443/users

      2. **Create Products:**

        > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Laptop", "price":890, "quantity":100}' https://localhost:443/products

        > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Desktop", "price":1200, "quantity":100}' https://localhost:443/products

        > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Mobile", "price":850.9, "quantity":100}' https://localhost:443/products

      3. **Create Wallet for the User Michael:**

        > curl -k -X POST -H "Host: wallet.eshop.com" -H "Content-Type: application/json" -d '{"user_name":"Michael", "card_number":"123-456-7890", "amount":120000}' https://localhost:443/wallets/add


      4. **Buy the product with user Michael:**

         Get Michael ID from the DB
         
         > curl -k -H "Host: users.eshop.com" https://localhost:443/users -> [{"_id":"64a6b0a476d49ca2783f5fd2","card_number":"123-456-7890","email":"michael@example.com","user_name":"Michael"}]
         
         Buy the product: 

         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Laptop", "price":890, "quantity":100}' https://localhost:443/products
         
         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"user_id": "64a6b0a476d49ca2783f5fd2", "user_name": "Michael", "card_number": "123-456-7890", "product_name": "Mobile", "quantity": 1}'
      
      5. **Observe the following:**

         eShop orders: 
         
         > curl -k -H "Host: orders.eshop.com" https://localhost:443/orders
         
         Wallet for user Michael:
         
         > curl -k -H "Host: wallet.eshop.com" https://localhost:443/wallets
         
         Quantity of the products: 
         
         > curl -k -H "Host: products.eshop.com" https://localhost:443/products

      5. **Delete Kubectl deployments**
         
         > ./setup.sh kubectl delete eshop or wallet

</details>


<a id="eshop-project-helm-deployment"></a>


<details>

   <a id="eshop-project-helm-deployment"></a>

   <summary>eShop Project - Helm deployment</summary>
   
   1. When docker images are builded, usually we need to push them to some docker registry. For the simplicity of this project, i decided to avoid docker registry and to push docker images from   local repository to our Kind kubernetes cluster. Kind is running under docker container and it doesnt have access to our file system. Thats why we need to push our images inside Kind cluster.

     > ./setup.sh load images -k <kind_cluster_name>

   2. Deploy eShop release package with Helm

      > ./setup.sh helm deploy -r eshop
     
      > kubectl get pods -n eshop

      > kubectl get svc -n eshop

      > kubectl get ingress -n eshop

   
   3. Deploy Wallet release package with Helm

      > ./setup.sh helm deploy -r wallet
     
      check the pod status with command: 

      > kubectl get pods -n wallet

      Note: when PostgreSQL is up and running, Wallet pod will be in the running state

      check the svc status with command:

      > kubectl get svc -n wallet

      check the ingress status with command: 

      > kubectl get ingress -n wallet

   4. Forward Nginx Ingress traffic to be available from the localhost
      
      > kubectl port-forward service/ingress-nginx-controller 443:443 or 80:80 -n ingress-nginx
      
   5. Buy default, all the database (MongoDB and PostgreSQL) are empty. The very first thing is to create Users, Products and User Wallet.


      1. **Create User:**
         
         > curl -k -X POST -H "Host: users.eshop.com" -H "Content-Type: application/json" -d '{"user_name":"Michael", "email":"michael@example.com", "card_number":"123-
         456-7 890"}' https://localhost:443/users

      2. **Create Products:**

         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Laptop", "price":890, "quantity":100}' https://localhost:443/products

         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Desktop", "price":1200, "quantity":100}' https://localhost:443/products

         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Mobile", "price":850.9, "quantity":100}' https://localhost:443/products

      3. **Create Wallet for the User Michael:**

         > curl -k -X POST -H "Host: wallet.eshop.com" -H "Content-Type: application/json" -d '{"user_name":"Michael", "card_number":"123-456-7890", "amount":120000}' https://localhost:443/wallets/add


      4. **Buy the product with user Michael:**

         Get Michael ID from the DB:
         > curl -k -H "Host: users.eshop.com" https://localhost:443/users -> [{"_id":"64a6b0a476d49ca2783f5fd2","card_number":"123-456-7890","email":"michael@example.com","user_name":"Michael"}]
         
         Buy the product: 

         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"product_name":"Laptop", "price":890, "quantity":100}' https://localhost:443/products
         
         > curl -k -X POST -H "Host: products.eshop.com" -H "Content-Type: application/json" -d '{"user_id": "64a6b0a476d49ca2783f5fd2", "user_name": "Michael", "card_number": "123-456-7890", "product_name": "Mobile", "quantity": 1}'
      
      5. **Observe the following:**

         eShop orders:
         
         > curl -k -H "Host: orders.eshop.com" https://localhost:443/orders
         
         Wallet for user Michael:
         
         > curl -k -H "Host: wallet.eshop.com" https://localhost:443/wallets
         
         Quantity of the products: 
         
         > curl -k -H "Host: products.eshop.com" https://localhost:443/products

      5. **Uninstall Helm release**
         
         > ./setup.sh helm delete -r eshop or wallet

</details>


