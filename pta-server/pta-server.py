import os
from socket import *
serverPort = 11550

# Apresentação
def validate_client(user):
    with open("users.txt", "r") as file:
        for users in file:
            if user == users.strip():
                return 'OK'
    return 'NOK'

# Listagem
def ls(directory):
    try:
        files = os.listdir(directory)
        if len(files) == 0:
            return 'NOK'
        files_list = ','.join(files)
        return f'ARQS {len(files)} {files_list}'
    except Exception as e:
        return 'NOK'

# Requisição de arquivo
def file_request(directory, filename):
    file_path = os.path.join(directory, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            file_size = os.path.getsize(file_path)  # tamanho do arquivo
            with open(file_path, "rb") as file:
                file_bytes = file.read()  # le os bytes do arquivo
            return f'ARQ {file_size}', file_bytes
        except Exception as e:
            return 'NOK', None
    else:
        return 'NOK', None
    
# Fechamento
def closing_connection(connectionSocket, seq_num):
    try:
        connectionSocket.send(f"{seq_num} OK".encode())
        connectionSocket.shutdown(SHUT_RDWR)
        connectionSocket.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error closing connection: {e}")


if __name__ == "__main__":      
    # Cria o Socket TCP (SOCK_STREAM) para rede IPv4 (AF_INET)
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    # Socket fica ouvindo conexoes.
    serverSocket.listen(1)

    print("Server ready to receive messages. Type Ctrl+C to finish.")
    while True:
        try:
            # Aceita uma conexao de um cliente
            connectionSocket, addr = serverSocket.accept()
            print(f"Connected to client at {addr}")
            state = 'EM ESPERA' # apos estabelecer a conexão TCP a apresentação deve ser realizada
            print(state)
            
            while True:
                # Recebe a mensagem do cliente
                message = connectionSocket.recv(1024).decode()
                print(f"Received: {message}")
                # Processa a mensagem recebida
                parts = message.strip().split(' ')
                if len(parts) < 2:
                    connectionSocket.send(f"{parts[0]} NOK".encode())
                    continue
                seq_num = parts[0]  # numero da sequencia
                command = parts[1]  # comando do cliente
                
                if state == 'EM ESPERA':
                    print('CUMP ...')
                    if command == "CUMP":
                        if len(parts) < 3: # verificando se tem o argumento
                            print('incomplete message.')
                            break
                        else:
                            user = parts[2]  # nome do usuario
                            response = validate_client(user)
                            connectionSocket.send(f"{seq_num} {response}".encode())
                            if response == 'OK':
                                print('done.')
                                state = 'PRONTO'
                            else:
                                print('invalid user.')
                                connectionSocket.shutdown(SHUT_RDWR)
                                connectionSocket.close() # se o cliente não for aceito, a conexao é fechada
                                break
                    else:
                        connectionSocket.send(f"{seq_num} NOK".encode())
                        connectionSocket.shutdown(SHUT_RDWR)
                        connectionSocket.close() # se receber qualquer msg diferente, a conexão deve ser fechada
                        break

                elif state == 'PRONTO':
                    print(state)
                    # Listagem
                    if command == "LIST":
                        print(command)
                        response = ls("files")
                        connectionSocket.send(f"{seq_num} {response}".encode())
                    # Requisiçao de arquivo
                    elif command == "PEGA":
                        print(command)
                        if len(parts) < 3: # verificando se tem o argumento
                            print('incomplete message.')
                            connectionSocket.send(f"{seq_num} NOK".encode())
                        else:
                            filename = parts[2]
                            response, file_bytes = file_request("files", filename)
                            print(f"{seq_num} {response} {file_bytes}".encode() )
                            connectionSocket.send(f"{seq_num} {response} {file_bytes}".encode())

                    # Fechamento
                    elif command == "TERM":
                        print(command)
                        closing_connection(connectionSocket, seq_num)
                        break
                    else: # Comando desconhecido, mas não fecha a conexão
                        print('Unknown command.')
                        connectionSocket.send(f"{seq_num} NOK".encode())
        except (KeyboardInterrupt, SystemExit):
            print("Shutting down server...")
            break

    serverSocket.shutdown(SHUT_RDWR)
    serverSocket.close()