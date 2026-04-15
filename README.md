


# SDN Traffic Classification System (Mininet + Ryu)

## Problem Statement

This project implements a Software Defined Networking (SDN) solution using Mininet and Ryu controller to classify network traffic based on protocol type (TCP, UDP, ICMP). The controller analyzes packets, maintains statistics, and demonstrates network behavior.

---

## Objectives

- Identify TCP, UDP, and ICMP packets  
- Maintain traffic statistics  
- Display classification results  
- Demonstrate SDN controller-switch interaction  
- Implement flow rules using OpenFlow  

---

## Concept Overview

- Mininet: Simulates network (hosts + switch)  
- Ryu Controller: Controls network behavior  
- OpenFlow: Communication protocol between switch and controller  
- Packet Classification: Detect protocol type and count packets  

---

## Setup Instructions

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install mininet
sudo apt install python3-pip
pip3 install ryu
````

---

### 2. Run Controller

```bash
ryu-manager traffic_classifier.py
```

---

### 3. Start Mininet

```bash
sudo mn --topo single,3 --controller remote --switch ovsk,protocols=OpenFlow13
```

---

## Execution Steps

### Test 1: ICMP (Ping)

```bash
h1 ping h2 -c 5
```

### Test 2: TCP Traffic

```bash
h2 iperf -s &
h1 iperf -c h2
```

### Test 3: UDP Traffic

```bash
h2 iperf -s -u &
h1 iperf -c h2 -u
```

---

## Expected Output

* ICMP packets detected during ping
* TCP packets detected during iperf
* UDP packets detected during UDP test
* Packet statistics displayed in controller logs

---

## Normal Case

Network communication is successful. Ping between hosts works correctly, and packets are classified by the controller.

---

## Failure Case

Initially, communication fails due to lack of flow rules in the switch, resulting in:

"Destination Host Unreachable"

After learning, the controller installs flow rules and communication becomes successful.

---

## Proof of Execution

### 1. Ping Failure (Before Flow Installation)

Caption: Initial ping failure due to missing flow rules in the switch.

```md
<img width="852" height="478" alt="ping_failure" src="https://github.com/user-attachments/assets/dee0e298-d05b-41fc-b9a0-426347dcd0c2" />

```

---

### 2. Ping Success (After Flow Installation)

Caption: Successful ICMP communication after the controller installs flow rules.

```md
<img width="1725" height="668" alt="ping_success" src="https://github.com/user-attachments/assets/b3c844e4-0d8e-4d14-8e78-a509845fa00b" />

```

---

### 3. TCP Traffic Test (iperf)

Caption: TCP traffic transmission showing high bandwidth between hosts.

```md
<img width="858" height="216" alt="tcp_test" src="https://github.com/user-attachments/assets/07987327-052b-423a-a2b1-5c9918684fa5" />

```

---

### 4. UDP Traffic Test (iperf)

Caption: UDP traffic test showing datagram transmission and bandwidth.

```md
<img width="1733" height="638" alt="udp_test" src="https://github.com/user-attachments/assets/c63044c2-623b-4130-9f65-314a3682fcd9" />

```

---

### 5. Controller Logs (Traffic Classification)

Caption: Ryu controller logs displaying classified packet counts (TCP, UDP, ICMP, Other).

```md
<img width="1619" height="948" alt="logs" src="https://github.com/user-attachments/assets/d77e5012-f363-4b2f-b388-3731c007c04b" />

```

---

## Key Learning

* Understanding SDN architecture
* Controller-switch interaction
* Flow rule installation
* Traffic classification and monitoring

```
```
