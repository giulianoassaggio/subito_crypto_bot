#include <unistd.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>

int main(int argc, char* argv[]){
        if (argc < 2){
                perror("error: no command provided\n");
                return 1;
        }
        char* command = argv[1];
        pid_t pid;
        pid = fork();
        if (pid < 0){
                perror("error: fork\n");
                return 1;
        }
        else if (pid > 0)
                return 0;

        // figlio: execute program

        argv++; // first argument is "deamonize"

        //create new session
        if (setsid() < 0){
                perror("error: setsid\n");
                return 1;
        }

        //change working directory to root -> full path needed
        //if (chdir("/") < 0){
        //      perror("error: chdir\n");
        //      return 1;
        //}

        //redirect I/O to /dev/null
        int fd = open("/dev/null", O_RDWR);
        if (fd < 0){
                perror("error: /dev/null\n");
                return 1;
        }
        dup2(fd, STDIN_FILENO);
        dup2(fd, STDOUT_FILENO);
        dup2(fd, STDERR_FILENO);
        close(fd);

        //execution
        execvp(argv[0], argv);
        perror("Error: execution");

        return 0;
}
