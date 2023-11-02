import socket
import json

def main():
    host = "127.0.0.1"
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        print("Options:")
        print("1. List available books")
        print("2. Reserve book")
        print("3. Return book")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            client_socket.send("list".encode())
            response = client_socket.recv(1024).decode()
            books_info = json.loads(response)
            print("Available books:")
            for title, available in books_info.items():
                print(f"{title} - Available: {available}")

        elif choice == "2":
            book_title = input("Enter the title of the book to reserve: ")
            client_socket.send(f"reserve {book_title}".encode())
            response = client_socket.recv(1024).decode()
            print(response)

        elif choice == "3":
            book_title = input("Enter the title of the book to return: ")
            client_socket.send(f"return {book_title}".encode())
            response = client_socket.recv(1024).decode()
            print(response)

        elif choice == "4":
            client_socket.close()
            break

if __name__ == "__main__":
    main()
