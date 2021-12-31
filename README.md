
# TON-PROXY
___
This is a proxy for solo mining coin [Toncoin (The Open Network)](https://ton.org/mining). Improves the stability of the miner and increases the percentage of accepted shares. Powered by the official miner with minor modifications.   [Visit the releases page](https://github.com/GRinvest/tonminer/releases) to select the latest version for your system. It also removes the problem with frequent shutdowns of video cards.
___
For the proxy to work, you need an Ubuntu server with a fixed ip if the farms are located in different locations or make a connection inside the network.
- [ ] The launch is quite simple and you do not need to have any special knowledge:
    - [X] [Download proxies from the releases page](https://github.com/GRinvest/ton-proxy/releases)
    ```
    wget https://github.com/GRinvest/ton-proxy/releases/download/0.1.5/ton-proxy.tar.gz
    ```
    - [X] Unpack and go to the miner folder
    ```
    tar xvf ton-proxy.tar.gz
    cd ton-proxy
    ```
    - [X] Run the file `./ton-proxy` with additional arguments, to view the list of commands, use the flag `-h` or `--help`  
Example: ` ./ton-proxy -h`  
:white_check_mark: Congratulations, you can connect the miner. By default, the proxy is configured for your external IP address and port `8080`
    (You may need to open a port, to do this, run the command `sudo ufw allow 8080`).  
    It is also advisable to run the proxy through `screen` So that he does not disconnect when exiting the terminal.
    ```
    sudo apt install screen
    screen -S proxy ./ton-proxy
    ```
___
If you don't know how to use ubuntu, there is a good article on installing and configuring the server. https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04  
The project was published under the license of MIT. If you liked my development and would like to support the project. I would be grateful for all possible help:
___
TON: EQCtpc260pZIxRlifzmbefdHm4gUTKAMbmwaFebo7WiBiGc9  
[Telegram Group](https://t.me/tonsolominingdev)
