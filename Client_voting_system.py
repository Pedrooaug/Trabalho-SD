"""
import socket
import pickle

def vote():
    # Set up the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("0.0.0.0", 5555))

    # Authenticate with name and ID
    voter_name = input("Enter your name: ")
    voter_id = input("Enter your ID: ")
    auth_data = f"{voter_name} {voter_id}"
    client_socket.send(auth_data.encode())

    response = client_socket.recv(1024).decode()
    if response == "Authentication failed.":
        print("Authentication failed. Exiting.")
        client_socket.close()
        return

    # Receive candidate list and vote
    candidates = pickle.loads(client_socket.recv(1024))
    print("Candidates:")
    for i, candidate in enumerate(candidates):
        print(f"{i + 1}. {candidate}")

    while True:
        try:
            vote_index = int(input("Enter the number of the candidate you want to vote for: ")) - 1
            if 0 <= vote_index < len(candidates):
                client_socket.send(candidates[vote_index].encode())
                print("Vote cast successfully. Thank you for voting!")
                break
            else:
                print("Invalid candidate number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid candidate number.")

    client_socket.close()

if __name__ == "__main__":
    vote()
"""

import socket
import json

# Connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 8080))

# Voter authentication
name = input("Enter your name: ")
voter_id = input("Enter your ID: ")

# Send voter data as JSON to the server
voter_data = {"name": name, "id": voter_id}
client.send(json.dumps(voter_data).encode())

# Receive and parse the response from the server
response_data = client.recv(1024).decode()
response = json.loads(response_data)

print(response['message'])

if 'candidates' in response:
    # Display the list of candidates
    print("Candidates:")
    for i, candidate in enumerate(response['candidates']):
        print(f"{i}: {candidate}")

    # Vote for a candidate
    vote = input("Enter the number of your chosen candidate: ")
    client.send(vote.encode())

    # Receive and parse the final response from the server
    response_data = client.recv(1024).decode()
    response = json.loads(response_data)
    print(response['message'])

client.close()

