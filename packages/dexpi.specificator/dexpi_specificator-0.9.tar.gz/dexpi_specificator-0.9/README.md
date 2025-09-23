# DEXPI Specificator

## Introduction
The **DEXPI Specificator** is a tool for generating **DEXPI specifications** in various formats. It automates the creation of engineering information models and related specification documents. This guide describes three different ways to run the Specificator:

1. **As a CI/CD pipeline in GitLab** *(Preferred method for automation)*
2. **Using Docker to run the Specificator locally**
3. **Executing the Specificator as a Python script**

---

## 1. Running the Specificator in GitLab CI/CD *(Preferred)*
The GitLab CI/CD pipeline automates the execution of the Specificator and provides the generated files as artifacts.

### **Steps to Run in GitLab CI/CD:**
1. Push your changes to the repository.
2. The GitLab pipeline will automatically build the Specificator Docker image (if necessary) and execute it.
3. After the pipeline completes, download the generated artifacts (**specification.zip** and **specification.tar.gz**) from the CI/CD job artifacts.

### **Advantages:**
✅ Fully automated execution
✅ Output files are available in GitLab artifacts
✅ No local setup required

---

## 2. Running the Specificator using Docker
You can use Docker to run the Specificator locally without setting up a Python environment.

### **Steps to Run Using Docker:**
1. Download the latest `docker_image.tar` artifact from GitLab CI/CD.
2. Load the Docker image:
   ```sh
   docker load -i docker_image.tar
   ```
3. Run the Specificator inside a Docker container:
   ```sh
   docker run --rm -v "$(pwd):/app" IMAGE_NAME python examples/flexpi\ minus/run_specificator.py
   ```
   *(Replace `IMAGE_NAME` with the actual image tag from GitLab.)*

### **Advantages:**
✅ No need to install Python or dependencies
✅ Fully isolated execution environment
✅ Works on Windows, MacOS, and Linux

---

## 3. Running the Specificator as a Python script
You can also run the Specificator directly as a Python script in a virtual environment.

### **Steps to Run Using Python:**
1. Install **Python 3.12 or later**.
2. Clone the repository:
   ```sh
   git clone <repository-url>
   cd dexpi-specificator
   ```
3. Create a virtual environment and install dependencies:
   ```sh
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install .
   ```
4. Run the Specificator:
   ```sh
   python examples/flexpi\ minus/run_specificator.py
   ```

### **Advantages:**
✅ Allows development and debugging of the Specificator
✅ Full control over dependencies and execution
✅ No need for Docker

---

## Conclusion
The **preferred way** to use the Specificator is through **GitLab CI/CD** for automation and consistency. However, **Docker** provides a flexible way to run it locally, while running it as a **Python script** allows for development and debugging.

Choose the method that best fits your needs! 🚀

