#!/usr/bin/python

# Programmed by hXR16F
# hXR16F.ar@gmail.com, https://github.com/hXR16F

from os import remove
from colorama import Fore
from subprocess import run
from time import sleep, time
from sys import platform, argv
from prettytable import PrettyTable


class msg(object):
    def error(*argv):
        once = False
        for text in argv:
            if not once:
                print(f"{Fore.RED}ERROR:{Fore.RESET} {text}")
                once = True
            else:
                print(f"       {text}")


    def warning(*argv):
        once = False
        for text in argv:
            if not once:
                print(f"{Fore.YELLOW}WARN:{Fore.RESET} {text}")
                once = True
            else:
                print(f"      {text}")


def main():
    filename = "output.txt"
    f = open(filename, "w")
    result = run(["ifconfig", "-s"], stdout=f)

    line_number, interfaces = 1, []
    with open(filename, "r") as file:
        for line in file:
            line_array = line.split()
            if not line_array[0] == "Iface":
                interfaces.append([line_array[0], line_number])
                line_number += 1

    file.close()

    t = PrettyTable(["#", "Interface"])
    for i in range(len(interfaces)):
        if not interfaces[i][0] == "lo":
            t.add_row([
                Fore.BLUE + str(interfaces[i][1]) + Fore.RESET,
                Fore.BLUE + str(interfaces[i][0]) + Fore.RESET
            ])
        else:
            t.add_row([
                Fore.YELLOW + str(interfaces[i][1]) + Fore.RESET,
                Fore.YELLOW + str(interfaces[i][0]) + Fore.RESET
            ])

    t.align["#"] = "r"
    t.align["Interface"] = "l"
    print(t)

    try:
        selected_interface = int(input(f"\n>>> {Fore.MAGENTA}Select interface{Fore.RESET}: "))
    except KeyboardInterrupt:
        remove(filename)
        quit()
    except ValueError:
        msg.error("Selected interface doesn't exist!")
        remove(filename)
        quit()
    
    if selected_interface < 1 or selected_interface > len(interfaces):
        msg.error("Selected interface doesn't exist!")
        remove(filename)
        quit()

    download_beginning, upload_beginning = False, False
    dl_packets_beginning, up_packets_beginning = False, False

    start_time = time()

    while True:
        try:
            f = open(filename, 'r+')
            f.truncate(0)
            download, upload = False, False
            dl_packets, up_packets = False, False

            result = run(["ifconfig", interfaces[selected_interface - 1][0]], stdout=f)
            with open(filename, "r") as file:
                for line in file:
                    if line.strip():
                        line_array = line.split()
                        try:
                            if line_array[0] == "RX" or line_array[0] == "TX":
                                if not line_array[4] == "0":
                                    if line_array[0] == "RX" and line_array[1] == "packets":
                                        download = int(line_array[4])
                                        dl_packets = int(line_array[2])
                                        if not download_beginning:
                                            download_beginning = download

                                        if not dl_packets_beginning:
                                            dl_packets_beginning = dl_packets
                                    elif line_array[0] == "TX" and line_array[1] == "packets":
                                        upload = int(line_array[4])
                                        up_packets = int(line_array[2])
                                        if not upload_beginning:
                                            upload_beginning = upload

                                        if not up_packets_beginning:
                                            up_packets_beginning = up_packets

                        finally:
                            elapsed_time = int(time() - start_time)
                            if not download == False and not upload == False and not dl_packets == False and not up_packets == False:
                                run("clear")
                                print(f"Statistics from the last {Fore.MAGENTA}{elapsed_time}{Fore.RESET} seconds ({Fore.MAGENTA}{interfaces[selected_interface - 1][0]}{Fore.RESET}):")
                                t = PrettyTable([
                                    Fore.BLUE + "Download" + Fore.RESET,
                                    Fore.BLUE + str(round((download - download_beginning) / 1024 / 1024, 2)) + " MB" + Fore.RESET,
                                    Fore.BLUE + str(download - download_beginning) + " bytes" + Fore.RESET,
                                    Fore.BLUE + str(dl_packets - dl_packets_beginning) + " packets" + Fore.RESET
                                ])
                                t.add_row([
                                    Fore.YELLOW + "Upload" + Fore.RESET,
                                    Fore.YELLOW + str(round((upload - upload_beginning) / 1024 / 1024, 2)) + " MB" + Fore.RESET,
                                    Fore.YELLOW + str(upload - upload_beginning) + " bytes" + Fore.RESET,
                                    Fore.YELLOW + str(up_packets - up_packets_beginning) + " packets" + Fore.RESET
                                ])
                                t.align[Fore.BLUE + "Download" + Fore.RESET] = "r"
                                t.align[Fore.YELLOW + "Upload" + Fore.RESET] = "r"
                                print(t)
                                print(f"Press {Fore.MAGENTA}CTRL{Fore.RESET} + {Fore.MAGENTA}C{Fore.RESET} to stop.")
                                break
                            
            sleep(0.5)
        except KeyboardInterrupt:
            remove(filename)
            quit()


if __name__ == "__main__":
    if not platform.startswith("linux", 0, 5):
        if not "-f" in argv:
            msg.warning("This program is designed to use on Linux operating system.", "Use \"-f\" to force the program to run.")
            quit()

    main()
