import socket
import json
from Library_book_classes_library_system import Library, Book

def main():
    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")

    library = Library()
    library.catalog["Book1"] = Book("Book1", "Author1")
    library.catalog["Book2"] = Book("Book2", "Author2")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        while True:
            data = conn.recv(1024).decode()

            if not data:
                break  # Exit the loop if the client disconnects

            if data == "list":
                available_books = {title: book.available for title, book in library.catalog.items()}
                response = json.dumps(available_books)
                conn.send(response.encode())

            elif data.startswith("reserve"):
                book_title = data.split(" ")[1]
                if book_title in library.catalog:
                    if library.catalog[book_title].available:
                        library.catalog[book_title].available = False
                        library.checked_out[book_title] = conn
                        conn.send("Book reserved successfully.".encode())
                    else:
                        conn.send("Book not available to be reserved.".encode())
                else:
                    conn.send("Book not found in the catalog.".encode())

            elif data.startswith("return"):
                book_title = data.split(" ")[1]
                if book_title in library.checked_out and library.checked_out[book_title] == conn:
                    library.catalog[book_title].available = True
                    library.checked_out.pop(book_title)
                    conn.send("Book returned successfully.".encode())
                else:
                    conn.send("You didn't reserve this book.".encode())

        conn.close()

if __name__ == "__main__":
    main()
