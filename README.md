# SDN Traffic Classification System (Mininet + Ryu)

##  Problem Statement

This project implements a Software Defined Networking (SDN) solution using Mininet and Ryu controller to classify network traffic based on protocol type (TCP, UDP, ICMP). The controller analyzes packets, maintains statistics, and demonstrates network behavior.

---

## Objectives

* Identify TCP, UDP, and ICMP packets
* Maintain traffic statistics
* Display classification results
* Demonstrate SDN controller-switch interaction
* Implement flow rules using OpenFlow

---

## Concept Overview

* **Mininet**: Simulates network (hosts + switch)
* **Ryu Controller**: Controls network behavior
* **OpenFlow**: Communication protocol between switch and controller
* **Packet Classification**: Detect protocol type and count packets

---

##  Setup Instructions

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install mininet
sudo apt install python3-pip
pip3 install ryu
```

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

##  Execution Steps

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

## 📊 Expected Output

* ICMP packets detected during ping
* TCP packets detected during iperf
* UDP packets detected during UDP test
* Packet statistics displayed in controller logs

## 📸 Proof of Execution

Screenshots included:

* Ping results
* TCP/UDP iperf results
* Controller logs showing packet counts


---

##  Key Learning

* Understanding SDN architecture
* Controller-switch interaction
* Flow rule installation
* Traffic classification and monitoring

---

