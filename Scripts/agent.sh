#!/bin/bash

# Stop the script on any error
set -e

echo "### Starting Jenkins Agent setup..."

# Function to install necessary packages
install_agent_packages() {
  echo "### Installing required packages for Jenkins Agent..."
  apt update
  apt install -y openjdk-17-jdk curl
}

# Function to configure /etc/hosts
configure_hosts_for_agent() {
  echo "### Configuring /etc/hosts..."
  read -p "Enter the hostname of the Jenkins master: " JENKINS_MASTER_HOSTNAME
  read -p "Enter the IP address of the Jenkins master: " JENKINS_MASTER_IP

  # Remove any existing entry and add the new one
  sed -i "/\s$JENKINS_MASTER_HOSTNAME$/d" /etc/hosts
  echo "$JENKINS_MASTER_IP $JENKINS_MASTER_HOSTNAME" >> /etc/hosts

  echo "### /etc/hosts configuration completed."
}

# Function to configure the Jenkins Agent
configure_jenkins_agent_service() {
  echo "### Configuring Jenkins Agent Service..."
  
  mkdir -p /var/jenkins_home

  # Set permissions for the Jenkins agent directory
  chown -R 1000:1000 /var/jenkins_home

  # Get Jenkins agent details from the user
  read -p "Enter the Jenkins master URL (e.g., http://<jenkins-master-ip>:8080): " JENKINS_URL
  read -p "Enter the Jenkins agent secret key: " AGENT_SECRET
  read -p "Enter the Jenkins agent name: " AGENT_NAME

  # Download the Jenkins agent JAR
  curl -o /var/jenkins_home/agent.jar ${JENKINS_URL}/jnlpJars/agent.jar

  if [[ ! -f /var/jenkins_home/agent.jar ]]; then
    echo "Error: Failed to download agent.jar. Please check the Jenkins master URL."
    exit 1
  fi

  # Create the agent's service script
  cat <<EOF > /var/jenkins_home/service.sh
#!/bin/bash
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar /var/jenkins_home/agent.jar \\
  -url $JENKINS_URL \\
  -secret $AGENT_SECRET \\
  -name $AGENT_NAME \\
  -workDir "/var/jenkins_home" \\
  -webSocket
EOF

  chmod +x /var/jenkins_home/service.sh

  # Create a systemd service for the Jenkins agent
  cat <<EOF > /etc/systemd/system/jenkins-agent.service
[Unit]
Description=Jenkins Agent Service
After=network.target

[Service]
User=root
WorkingDirectory=/var/jenkins_home
ExecStart=/bin/bash /var/jenkins_home/service.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

  # Reload systemd and start the Jenkins agent service
  systemctl daemon-reload
  systemctl enable jenkins-agent
  systemctl start jenkins-agent

  echo "### Jenkins Agent Service configured and started successfully."
}

# Main script execution
install_agent_packages          # Step 1: Install required packages
configure_hosts_for_agent       # Step 2: Configure /etc/hosts
configure_jenkins_agent_service # Step 3: Configure Jenkins Agent service

echo "### Jenkins Agent setup completed successfully."
