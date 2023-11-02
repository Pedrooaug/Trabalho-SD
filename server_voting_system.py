"""
import socket
import pickle

def start_election():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5555))
    server_socket.listen(5)
    print("Server is waiting for connections...")

    # Accept connections from clients
    client_sockets = []
    num_voters = int(input("Enter the number of voters: "))
    num_candidates = int(input("Enter the number of candidates: "))
    candidates = []

    for i in range(num_candidates):
        candidate_name = input(f"Enter the name of candidate {i + 1}: ")
        candidates.append(candidate_name)

    # Authenticate voters and receive their votes
    votes = {}

    while len(votes) < num_voters:
        client_socket, _ = server_socket.accept()
        print("Connection established with a client.")

        # Receive authentication data
        data = client_socket.recv(1024).decode()
        voter_name, voter_id = data.split()

        # Authenticate the voter
        if authenticate_voter(voter_name, voter_id):
            client_sockets.append(client_socket)
            print(f"{voter_name} authenticated and ready to vote.")
            vote = receive_vote(client_socket, candidates)
            votes[voter_name] = vote
            client_socket.close()
        else:
            client_socket.send("Authentication failed.".encode())
            client_socket.close()

    # Calculate and display the election result
    election_result = calculate_election_result(votes, candidates)
    print("Election result:")
    for candidate, votes_received in election_result.items():
        print(f"{candidate}: {votes_received} votes")

    # Close the server socket
    server_socket.close()

def authenticate_voter(voter_name, voter_id):
    # You should implement a proper authentication mechanism here
    return True

def receive_vote(client_socket, candidates):
    # Receive and validate the vote from the client
    client_socket.send(pickle.dumps(candidates))
    vote = client_socket.recv(1024).decode()
    return vote

def calculate_election_result(votes, candidates):
    # Calculate the election result
    election_result = {candidate: 0 for candidate in candidates}
    for _, vote in votes.items():
        election_result[vote] += 1
    return election_result

if __name__ == "__main__":
    start_election()
"""

import socket
import threading
import json
from collections import Counter

# Prompt for election parameters
num_voters = int(input("Enter the number of voters: "))
num_candidates = int(input("Enter the number of candidates: "))
candidates = []

# Prompt for candidate names
for i in range(num_candidates):
    candidate_name = input(f"Enter the name of Candidate {i + 1}: ")
    candidates.append(candidate_name)

voter_data = {}

# Prompt for voters' names and IDs
for i in range(num_voters):
    voter_name = input(f"Enter the name of Voter {i + 1}: ")
    voter_id = input(f"Enter the ID of Voter {i + 1}: ")
    voter_data[voter_id] = voter_name

# Create a socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8080))
server.listen(5)

# Counter to track the number of votes
vote_counter = 0
lock = threading.Lock()
votes = []

# Function to handle a client's vote
def handle_client(client_socket):
    global vote_counter
    try:
        # Receive and parse the JSON data from the client
        data = client_socket.recv(1024).decode()
        client_data = json.loads(data)

        # Authenticate the voter
        voter_name = client_data['name']
        voter_id = client_data['id']

        response = {}

        if voter_id not in voter_data:
            response['message'] = "Invalid voter ID. You are not eligible to vote."
        elif voter_id in voter_data and voter_data[voter_id] != voter_name:
            response['message'] = "Invalid voter name. Please provide the correct name for your ID."
        elif voter_id in voter_data and voter_data[voter_id] == voter_name:
            response['message'] = "Authentication successful. Please vote."

            # Display the list of candidates
            response['candidates'] = candidates

            # Send the response as JSON to the client
            client_socket.send(json.dumps(response).encode())

            # Vote for a candidate
            vote = client_socket.recv(1024).decode()
            if vote.isdigit() and 0 <= int(vote) < num_candidates:
                with lock:
                    vote_counter += 1
                    votes.append(int(vote))
                response['message'] = "Vote recorded. Thank you for voting."
            else:
                response['message'] = "Invalid vote. Please try again."

        # Send the final response as JSON to the client
        client_socket.send(json.dumps(response).encode())

        # Check if all votes have been cast
        if vote_counter >= num_voters:
            result = Counter(votes)
            winning_candidate = max(result, key=result.get)
            total_votes = sum(result.values())
            print("Election results:")
            for candidate, votes_received in result.items():
                print(f"{candidates[candidate]} received {votes_received} votes.")
            print(f"Total votes cast: {total_votes}")
            print(f"{candidates[winning_candidate]} won the election with {votes_received} votes.")
            server.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

# Wait for all voters to connect
while len(voter_data) > 0:
    client, addr = server.accept()
    print(f"Accepted connection from {addr}")
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()

# Ensure all client threads have finished before calculating results
for thread in threading.enumerate():
    if thread != threading.current_thread():
        thread.join()

# Calculate election results
result = Counter(votes)
winning_candidate = max(result, key=result.get)
total_votes = sum(result.values())

# Display election results
print("Election results:")
for candidate, votes_received in result.items():
    print(f"{candidates[candidate]} received {votes_received} votes.")
print(f"Total votes cast: {total_votes}")
print(f"{candidates[winning_candidate]} won the election with {votes_received} votes.")

server.close()
