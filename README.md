# Secured Networked Video Streaming and Messaging System

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)
  - [Server](#server)
  - [Client](#client)
- [Code Description](#code-description)
  - [Client Code](#client-code)
  - [Server Code](#server-code)


### Problem Statement

In today's digital age, there is a growing need for secure and efficient communication systems that can handle multiple functionalities simultaneously. Specifically, there is a demand for systems that can provide synchronous chatting and video streaming capabilities over a reliable network protocol. The challenge is to create a robust application that ensures secure communication, real-time updates, and efficient handling of multiple client connections using TCP/IP, all while maintaining high performance and user experience.

### Solution

This project addresses the problem by implementing a secured system for video streaming and messaging using Python, socket programming, TCP/IP, OpenCV, and multithreading. The application is designed to handle synchronous chatting and video streaming concurrently, enhancing the user experience with real-time communication and media capabilities.

### Key Features

- **Secure Communication:** Utilizes RSA encryption for secure messaging between clients.
- **Concurrent Functionality:** Implements multithreading to allow simultaneous video streaming and messaging.
- **Real-Time Updates:** Clients are updated on entry and exit, demonstrating proficiency in network architecture.
- **Video Streaming:** Allows clients to request and stream video files from the server.
- **Robust Messaging:** Facilitates real-time messaging between clients.

### Prerequisites

- Python 3.x
- OpenCV
- RSA
- Numpy
- Pandas

2. Install the required libraries using pip:
    ```bash
    pip install opencv-python rsa numpy pandas


### How to Run
## Server
1. Start the server by running the following command:
      ```bash
      python server.py
      
The server will start listening for incoming connections on the specified IP and port.

## Client
1. Start the client by running the following command:
      ```bash
      python client.py
      
2. Enter your name when prompted.
   Choose to send a message or request a video stream.

### Code Description
## Client Code
1. Importing Libraries
    ```bash
      The client code imports necessary libraries such as socket, threading, json, time, rsa, cv2, and numpy.
    
    
2. RSA Key Generation
   ```bash
    The function generate_rsa_key_pair() is used to generate an RSA key pair for encryption and decryption of messages.

3. Connect to Server
   ```bash
    The function connect_to_server(name, public_key) establishes a connection to the server and sends the client's name and public key.

4. Sending and Receiving Messages
   ```bash
    send_message(client_socket) handles sending messages to selected clients.
    receive_messages(client_socket) handles receiving messages from the server.
   
5. Video Streaming
   ```bash
    request_video_list(client_socket) requests a list of available videos from the server.
    handle_video_stream(chunk_data) handles the video stream received from the server.
    play_video() plays the received video stream.
   
6. Threading
   ```bash
    send_requests(client_socket) runs in a separate thread to handle user inputs for sending messages or requesting videos.
    receive_messages(client_socket) runs in a separate thread to handle incoming messages from the server.

## Server Code
1. Importing Libraries
     ```bash
      The server code imports necessary libraries such as socket, threading, json, os, time, and cv2.

2. Handling New Clients
     ```bash
      The function handle_new_client(server_socket) handles new client connections and starts a new thread for each client.

3. Sending and Receiving Messages
     ```bash
      receive_messages(client_socket) handles incoming messages from clients.
      broadcast_message(message) broadcasts messages to all connected clients.
     
4. Video Streaming
     ```bash
      send_video_list(client_socket) sends the list of available videos to clients.
      handle_video_request(video_name, client_socket) handles video streaming to the requesting client.
5. Main Function
     ```bash
      The main() function initializes the server, binds it to the specified IP and port, and starts listening for incoming connections.
