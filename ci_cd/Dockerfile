# Custom Jenkins controller for the Heart Disease MLOps project.
# - Adds python3 + venv + pip, docker CLI, kubectl
# - Pre-installs the plugins required by the Jenkinsfile
# - Skips the setup wizard so JCasC can fully bootstrap on first start
#
# Build:
#   docker build -t heart-disease-jenkins:latest -f ci_cd/Dockerfile ci_cd/
FROM jenkins/jenkins:lts-jdk17

USER root

# System tools used by the pipeline.
# We use `uv` (Astral) to install a pinned Python 3.11 runtime, because the
# project's requirements (pandas==2.2.2, numpy==1.26.4, ...) don't have
# manylinux wheels for the Python 3.13 that ships with Debian Trixie, and
# building them from source on aarch64 hits Cython/GCC incompatibilities.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg lsb-release git \
 && rm -rf /var/lib/apt/lists/*

# Install uv and a pinned Python 3.11 toolchain in /opt/uv-python.
ENV UV_INSTALL_DIR=/usr/local/bin \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_UNMANAGED_INSTALL=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && uv python install 3.11 \
 && ln -s "$(uv python find 3.11)" /usr/local/bin/python3.11 \
 && ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3 \
 && python3 --version

# Docker CLI (no daemon) - the daemon is mounted from the host via /var/run/docker.sock
RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release; echo $VERSION_CODENAME) stable" \
        > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

# kubectl
RUN KUBE_VER=$(curl -fsSL https://dl.k8s.io/release/stable.txt) \
 && ARCH=$(dpkg --print-architecture) \
 && curl -fsSL "https://dl.k8s.io/release/${KUBE_VER}/bin/linux/${ARCH}/kubectl" -o /usr/local/bin/kubectl \
 && chmod +x /usr/local/bin/kubectl

# Plugins listed in the Jenkinsfile header
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Skip the setup wizard - JCasC will provision the controller
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs/jenkins.yaml

# JCasC config (mounted as the canonical CASC source on every restart)
COPY casc/jenkins.yaml /var/jenkins_home/casc_configs/jenkins.yaml

USER jenkins
