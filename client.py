import socket
import traceback

def readline(io: socket.SocketIO):
    return io.readline().decode().strip()

def writeline(io: socket.SocketIO, line: str):
    io.writelines([line.encode()])
    io.flush()

def client(host, port, password):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        io = socket.SocketIO(sock, 'rw')

        if readline(io) != "welcome":
            print("ERROR: Unexpected message, exiting")
            return
        
        writeline(io, password)
        auth_result = readline(io)
        
        if auth_result != "authenticated":
            print("ERROR: Auth unsuccesful, exiting")
            return

        print("Beginning game")

        while True:
            message = readline(io).split(":")

            match message[0]:
                case "hint":
                    print("Hint: " + message[1])
                case "hint_exhausted":
                    print("All hints have already been given")
                case "guess_correct":
                    print("Guess correct!")
                    sock.close()
                    return

            guess = input("Enter your guess:")
            writeline(io, guess)
    except Exception as e:
        print("ERROR: An exception occurred")
        traceback.print_exc()
    finally:
        sock.close()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8888
    password = "secret_password"
    client(host, port, password)