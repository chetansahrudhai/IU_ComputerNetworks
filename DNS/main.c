#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <arpa/inet.h>

int retadd(const char*host,const char* port);

int retadd(const char* host,const char* port)
{
        struct addrinfo hostnum, *resf,*temf;
        int statcode;
        memset(&hostnum, 0 ,sizeof(hostnum));
        hostnum.ai_family = PF_UNSPEC;
        hostnum.ai_socktype = SOCK_STREAM;
        hostnum.ai_protocol = IPPROTO_TCP;
        hostnum.ai_flags = AI_PASSIVE;
        statcode = getaddrinfo(host,port,&hostnum,&temf);
        if(statcode >=1)
        {
                perror("getaddrinfo");
                return -1;
        }

        resf = temf;
        char str_adr[150];
        void* raw_addr;

        while(resf){
                inet_ntop(resf->ai_family,resf->ai_addr->sa_data,str_adr,200);
                if (resf->ai_family == AF_INET) { // Address is IPv4
                        struct sockaddr_in* tmp = (struct sockaddr_in*)resf->ai_addr; // Cast addr into AF_INET container
                        raw_addr = &(tmp->sin_addr); // Extract the address from the container
                }
                else { // Address is IPv6
                        struct sockaddr_in6* tmp = (struct sockaddr_in6*)resf->ai_addr; // Cast addr into AF_INET6 container
                        raw_addr = &(tmp->sin6_addr); // Extract the address from the container
                }
                inet_ntop (resf->ai_family,raw_addr,str_adr,200);
                printf("IPv%d %s \n", resf->ai_family != PF_INET6 ? 4 : 6,str_adr);
                resf = resf->ai_next;
        }
        freeaddrinfo(temf);
        return 0;
}

int main(int argc, char* argv[])
{
        if (argc != 3) {
                printf("Invalid arguments - %s <host> <port>", argv[0]);
                return -1;
        }
        char s1[10];
        char* host = argv[1];
        long port =(int)atoi(argv[2]);
        int portv = port ;
        sprintf(s1, "%d", portv);
        retadd(host,s1);
        return 0;
}