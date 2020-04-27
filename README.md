# 677 Lab 3

This is the Git repo for 677 Lab 3. See https://marcoserafini.github.io/teaching/distributed-os/spring20/labs/lab3.html for a description of the lab. The lab is due on Apr 24th, 11:59 pm. Prior to submitting your project, replace this README file with the one that explains how to setup and run your code. Be sure to provide enough details fo us to run it in order to grade it.

---
### Deploy on a single elnux server
To deploy all services on a single server on Edlab, you will need to modify below variables in **elnux_credentials.sh**:
  - Modify the value of "Username" to your account on Edlab.
  - Make sure "TargetPath" links to source folder of this project.
  - Set "MultipleServer" to 0.
  - By default, all services would be deployed on elnux7.cs.umass.edu. Change the value of "TargetServer" if you would like to deploy them on a different machine.

After making sure that all values are properly set, you can execute **deploy_elnux.sh** on your local machine. It will set up all services on Edlab. If you would like to terminate all running processes, simply execute **terminate_elnux.sh**.

---
### Deploy on multiple elnux servers
To deploy services on multiple servers on Edlab, you will need to modify below variables in **elnux_credentials.sh**:
  - Modify the value of "Username" to your account on Edlab.
  - Make sure "TargetPath" links to source folder of this project.
  - Set "MultipleServer" to 1.

Then, you need to make sure that the address and port information of each service under "ip" field of **config.json** are correctly set. **elnux_credentials.sh** would use those information to deploy services on corresponding servers. Please make sure that those values are valid and available. Otherwise, it is highly possible to cause failure during deployment.

After making sure that all values are properly set, you can execute **deploy_elnux.sh** on your local machine.  If you would like to terminate all running processes, simply execute **terminate_elnux.sh**.

---
### Deploy on your local device with Docker containers
To deploy services using Docker containers, you will need to modify below variables in **deploy_docker.sh**:
  - Make sure the command name of docker. It is set as docker.exe to variable "CMD" since my host OS is a Windows 10. If your host OS is Unix or Unix-like, you might need to set "CMD" as docker.
  - The default name of docker image is lab3_img with tag v1. Change the value of "IMG_NAME" if you want a a different docker image name.

The docker image of this project is not appended. Therefore, you have to build one first with command **./deploy_docker.sh build** in your first run. After the docker image is built, you can deploy containers with command **./deploy_docker.sh** in following runs. Execute **./terminate_docker.sh** when you want to stop and eliminate all containers.