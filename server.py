import socket
import threading
import json
import os
import time
import cv2

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 4096

clients = {}
video_directory = "./videos/"
client_id_new = 0

def handle_new_client(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        print("New connection arrived")
        client_name = client_socket.recv(BUFFER_SIZE).decode()
        public_key = client_socket.recv(BUFFER_SIZE).decode()
        print(f"[*] New client connected: {client_name}")

        global clients, client_id_new
        clients[client_socket] = {"name": client_name, "public_key": public_key, "client_id": client_id_new}
        client_id_new += 1

        send_all_conns(client_socket)
        broadcast_dictionary(client_socket)

        threading.Thread(target=receive_messages, args=(client_socket,)).start()

def send_all_conns(new_client_socket):
    for client_socket in clients.keys():
        if client_socket != new_client_socket:
            updated_client_info = {
                "name": clients[client_socket]["name"],
                "public_key": clients[client_socket]["public_key"],
                "client_id": clients[client_socket]["client_id"]
            }
            updated_client_message = f"UPDATE_CLIENT:{json.dumps({str(client_socket): updated_client_info})}"
            try:
                new_client_socket.send(updated_client_message.encode())
                time.sleep(2)
            except Exception as e:
                print(f"Error sending client data: {e}")

def broadcast_dictionary(new_client_socket):
    temp_public_key = clients[new_client_socket]["public_key"]
    updated_client_info = {
        "name": clients[new_client_socket]["name"],
        "public_key": temp_public_key,
        "client_id": clients[new_client_socket]["client_id"]
    }
    updated_client_message = f"UPDATE_CLIENT:{json.dumps({str(new_client_socket): updated_client_info})}"
    for client_socket in clients.keys():
        if client_socket != new_client_socket:
            try:
                client_socket.send(updated_client_message.encode())
            except Exception as e:
                print(f"Error broadcasting update to {clients[client_socket]['name']}: {e}")

def receive_messages(client_socket):
    contin = True
    while contin:
        try:
            origimsg = client_socket.recv(BUFFER_SIZE)
            message = origimsg.decode()
            if message.startswith("CIPHERTEXT:"):
                broadcast_message(message)
            elif message.startswith("VIDEO_REQUEST:"):
                handle_video_request(message[len("VIDEO_REQUEST:"):], client_socket)
            elif message.startswith("VIDEO_LIST_REQUEST:"):
                send_video_list(client_socket)
            elif message.startswith("QUIT"):
                temp_client_id = clients[client_socket]['client_id']
                client_socket.close()
                del clients[client_socket]
                broadcast_message(f"REMOVE_CLIENT:{temp_client_id}")
                contin = False
                break
            else:
                print(f"Received unknown message from client {clients[client_socket]['name']}: {message}")
        except Exception as e:
            contin = False
            break

def send_video_list(client_socket):
    video_list = {"video2_240.mp4", "video2_720.mp4", "video2_1080.mp4"}
    client_socket.send(f"VIDEO_LIST:{','.join(video_list)}".encode())

def broadcast_message(message):
    for client_socket in clients.keys():
        try:
            client_socket.send(message.encode())
        except Exception as e:
            print(f"Error broadcasting message to {clients[client_socket]['name']}: {e}")

def handle_video_request(video_name, client_socket):
    video_path = os.path.join(video_directory, video_name)
    if os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            chunk = buffer.tobytes()
            size = len(chunk)
            client_socket.sendall(b"VIDEO_STREAM:" + size.to_bytes(4, byteorder='big') + chunk)
            time.sleep(1 / 30)  # Assuming 30 fps
        cap.release()
        client_socket.sendall(b'END_VIDEO')
    else:
        print(f"Video file not found: {video_name}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Server listening on {SERVER_IP}:{SERVER_PORT}")
    handle_new_client(server_socket)
    server_socket.close()

if __name__ == "__main__":
    main()
