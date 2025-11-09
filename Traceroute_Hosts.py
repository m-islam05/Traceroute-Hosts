import socket
import time

# Note: If you get 'X) *' output check your network settings and outbound

# ----- Defaults ----- #
DEFAULT_MAX_HOPS = 30
DEFAULT_DEST_PORT = 33434
DEFAULT_TIMEOUT_SECONDS = 2.0
LOG_FILENAME = "traceroute.log"

def perform_traceroute(destination_host, max_hops, timeout_seconds):
    destination_ip = socket.gethostbyname(destination_host)
    print("Tracing route to " + destination_host + " [" + destination_ip + "]")

    for ttl in range(1, max_hops + 1):
        # UDP socket to send probe
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_socket.settimeout(timeout_seconds)

        # On Windows, use IPPROTO_IP instead of SOL_IP
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        # Bind to any port to receive ICMP replies
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        recv_socket.settimeout(timeout_seconds)
        recv_socket.bind(("", DEFAULT_DEST_PORT))

        # Send empty UDP packet to destination port
        send_socket.sendto(b"", (destination_ip, DEFAULT_DEST_PORT))

        hop_address = None
        rtt = None

        try:
            start_time = time.time()
            packet, addr = recv_socket.recvfrom(512)
            end_time = time.time()
            hop_address = addr[0]
            rtt = int((end_time - start_time) * 1000)
        except socket.timeout:
            hop_address = None
        finally:
            send_socket.close()
            recv_socket.close()

        if hop_address is None:
            line = str(ttl) + ": *"
        else:
            line = str(ttl) + ": " + hop_address + " time=" + str(rtt) + "ms"

        print(line)
        with open(LOG_FILENAME, "a") as log_file:
            log_file.write(line + "\n")

        if hop_address == destination_ip:
            print("Trace complete. Destination reached.")
            break

# ----- Main ----- #
target_host = input("Enter target domain or IP: ")
max_hops_input = input("Enter maximum hops (default 30): ")
timeout_input = input("Enter timeout in seconds (default 2.0): ")

max_hops = int(max_hops_input) if max_hops_input.strip() != "" else DEFAULT_MAX_HOPS
timeout_seconds = float(timeout_input) if timeout_input.strip() != "" else DEFAULT_TIMEOUT_SECONDS

perform_traceroute(target_host, max_hops, timeout_seconds)
