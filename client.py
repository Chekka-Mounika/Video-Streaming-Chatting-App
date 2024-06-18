import socket
import threading
import json
import time
import rsa
import cv2
import numpy as np

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 4096  # Adjust buffer size as needed
private_key = None
peers = {}
video_data = b''

def generate_rsa_key_pair():
    """
    Generate RSA key pair.
    """
    global private_key
    public_key, private_key = rsa.newkeys(1024)
    return public_key

def connect_to_server(name, public_key):
    """
    Connect to the server and send client's name and public key.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    client_socket.send(name.encode())
    time.sleep(2)  # Let the server process the name first
    serialized_pub_key = public_key.save_pkcs1().decode()
    client_socket.send(serialized_pub_key.encode())
    return client_socket

def request_video_list(client_socket):
    """
    Request the server to list available videos.
    """
    client_socket.send("VIDEO_LIST_REQUEST:".encode())

def update_peers(updated_client_message):
    """
    Update the peers dictionary with the received updated client information.
    """
    try:
        if updated_client_message.startswith("UPDATE_CLIENT:"):
            updated_client_info = json.loads(updated_client_message[len("UPDATE_CLIENT:"):])
            for client_socket_str, client_info in updated_client_info.items():
                global peers
                peers[client_socket_str] = client_info
            print("Updated client list:")
            print(json.dumps(peers, indent=4))
    except Exception as e:
        print(f"Error updating peers: {e}")

def remove_client(delete_client_id):
    """
    Remove a client from the peers dictionary based on the client ID.
    """
    for client_sock in peers.keys():
        if peers[client_sock]['client_id'] == int(delete_client_id):
            del peers[client_sock]
            break
    print("Removed client with ID:", delete_client_id)
    print("Updated client list:")
    print(json.dumps(peers, indent=4))

def handle_ciphertext_message(message):
    """
    Handle the ciphertext message received from the server.
    """
    encrypted_bytes = bytes.fromhex(message[len("CIPHERTEXT:"):])
    try:
        global private_key
        clear_msg = rsa.decrypt(encrypted_bytes, private_key)
        print("Received a new message from peer:", clear_msg.decode())
    except Exception as e:
        print(f"Error decrypting message: {e}")

def handle_video_stream(chunk_data):
    """
    Handle the video stream message received from the server.
    """
    global video_data
    video_data += chunk_data
    # You can optionally print or process received chunks here

def play_video():
    """
    Play the received video stream.
    """
    global video_data
    nparr = np.frombuffer(video_data, dtype=np.uint8)
    frames = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frames is not None:
        cv2.imshow("Video Stream", frames)
        cv2.waitKey(1)  # Adjust delay as needed

def send_message(client_socket):
    """
    Send a text message to a selected client.
    """
    print("List of all peers:")
    for cli in peers.keys():
        print(f"Name: {peers[cli]['name']}, Client ID: {peers[cli]['client_id']}")
    id_input = input("Enter the client ID to send the message: ")
    msg = input("Enter the message: ")
    for cli in peers.keys():
        if peers[cli]['client_id'] == int(id_input):
            client_pub_key = rsa.PublicKey.load_pkcs1(peers[cli]['public_key'].encode())
            encry_msg = rsa.encrypt(msg.encode(), client_pub_key)
            formatted_encrypted_msg = f"CIPHERTEXT:{encry_msg.hex()}"
            client_socket.send(formatted_encrypted_msg.encode())
            time.sleep(2)  # Let the message send

def send_requests(client_socket):
    """
    Thread function for sending requests to the server.
    """
    while True:
        try:
            print("Enter 'text' to send a text message, 'video' to request a video stream, or 'QUIT' to exit:")
            choice = input(">> ")
            if choice.lower() == 'text':
                send_message(client_socket)
            elif choice.lower() == 'video':
                request_video_list(client_socket)
                print("Please wait for the list of videos...")
                time.sleep(2)  # Adjust delay if needed
                video_request = input("Enter the video name to stream: ")
                client_socket.send(f"VIDEO_REQUEST:{video_request}".encode())
            elif choice.lower() == 'quit':
                client_socket.send("QUIT".encode())
                client_socket.close()
                break
            else:
                print("Invalid choice. Try again.")
        except Exception as e:
            print(f"Error in send_requests: {e}")

def receive_messages(client_socket):
    """
    Thread function for receiving messages from the server.
    """
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if not message:
                break
            if message.startswith("UPDATE_CLIENT:"):
                update_peers(message)
            elif message.startswith("REMOVE_CLIENT:"):
                remove_client(message[len("REMOVE_CLIENT:"):])
            elif message.startswith("CIPHERTEXT:"):
                handle_ciphertext_message(message)
            elif message.startswith("VIDEO_LIST:"):
                print("Received video list from server:")
                handle_video_list(message)
            elif message.startswith("VIDEO_STREAM:"):
                handle_video_stream(message[len("VIDEO_STREAM:"):].encode())
            elif message.startswith("END_VIDEO"):
                print("Received end of video stream signal.")
                play_video()
                global video_data
                video_data = b''  # Clear video data after playback
            else:
                print("Unknown message received from server.")
        except Exception as e:
            print(f"Error in receive_messages: {e}")
            break

def handle_video_list(message):
    """
    Handle the video list message received from the server.
    """
    video_list = message[len("VIDEO_LIST:"):].split(',')
    print("Available Videos:")
    for video in video_list:
        print(video)

def main():
    global private_key
    public_key = generate_rsa_key_pair()
    name = input("Enter your name: ")
    client_socket = connect_to_server(name, public_key)
    print("[*] Connected to server")

    # Thread for receiving messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Thread for sending requests
    send_thread = threading.Thread(target=send_requests, args=(client_socket,))
    send_thread.start()

    # Wait for both threads to finish
    receive_thread.join()
    send_thread.join()

    client_socket.close()

if __name__ == "__main__":
    main()
