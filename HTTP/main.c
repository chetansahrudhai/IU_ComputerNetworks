#include <stdio.h>
#include <string.h>

void send_http(char* host, char* msg, char* resp, size_t len);

/*
  Implement a program that takes a host, verb, and path and
  prints the contents of the response from the request
  represented by that request.
 */

int main(int argc, char* argv[]) {
        if (argc != 4) {
        printf("Invalid arguments - %s <host> <GET|POST> <path>\n", argv[0]);
        return -1;
        }
        char* host = argv[1];
        char* verb = argv[2];
        char* path = argv[3];
        char x[1000];
        strcpy(x,verb);
        strcat(x," ");
        strcat(x,path);
        strcat(x," HTTP/1.1\r\n");
        strcat(x,"Host: ");
        strcat(x,host);
        strcat(x,"\r\n\r\n");
        char response[4096];
        send_http(host,x,response,4096);
        //send_http("www.example.com", "GET / HTTP/1.0\r\nHost: www.example.com\r\n\r\n", response, 4096);
        //printf("%s\n", response);
        //send_http("www.example.com", "POST / HTTP/1.1\r\nHost: www.example.com\r\nContent-Length: 10\r\n\r\nThis is it\r\n\r\n", response, 4096);
        printf("%s\n", response);
        return 0;
}