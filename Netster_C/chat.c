#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<arpa/inet.h>
#include<unistd.h>
#include<netinet/in.h>
#include<sys/socket.h>
#include<sys/types.h>
#define mLim 256
void chat_server(char* iface, long port, int use_udp)
{
  char tempbuf[1024];
  int sFD, r, nSock, cnt = 0;
  struct sockaddr_in sAdd;
  socklen_t addr_size;
  struct sockaddr_in nAdd;
  sFD=socket(AF_INET,SOCK_STREAM,0);
  if(sFD<0)
  {
  perror("error while connecting.\n");
  exit(1);
  }
  memset(&sAdd, '\0',sizeof(sAdd));
  sAdd.sin_family=AF_INET;
  sAdd.sin_port=htons(port);
  sAdd.sin_addr.s_addr=inet_addr(iface);
  r=bind(sFD,(struct sockaddr*)&sAdd,sizeof(sAdd));
  if(r!=0)
  {
    perror("Error in binding");
    exit(1);
  }
  if(listen(sFD,25)!=0)
  {
    exit(1);
  }
while(1)
{
     nSock=accept(sFD,(struct sockaddr*)&nAdd,&addr_size);
     if(nSock<0)
     {
      exit(1);
      }
      printf("connection %d from ('%s',%d)\n",cnt,inet_ntoa(nAdd.sin_addr),ntohs(nAdd.sin_port));
          while(1)
          {
          bzero(tempbuf,1024);
          recv(nSock,tempbuf,mLim,0);
          if(strcmp(tempbuf,"goodbye")==0)
          {
            printf("got message from ('%s',%d)\n",inet_ntoa(nAdd.sin_addr),ntohs(nAdd.sin_port));
            bzero(tempbuf,1024);
            strcpy(tempbuf,"farewell");

            send(nSock,tempbuf,strlen(tempbuf),0);
            break;
          }
          else if(strcmp(tempbuf,"exit")==0)
           {
            printf("got message from ('%s',%d)\n",inet_ntoa(nAdd.sin_addr),ntohs(nAdd.sin_port));
            bzero(tempbuf,1024);
            strcpy(tempbuf,"ok");

            send(nSock,tempbuf,strlen(tempbuf),0);
           exit(1);
          }
          else if(strcmp(tempbuf,"hello")==0)
          {
            printf("got message from ('%s',%d)\n",inet_ntoa(nAdd.sin_addr),ntohs(nAdd.sin_port));
            bzero(tempbuf,1024);
             strcpy(tempbuf,"world");

            send(nSock,tempbuf,strlen(tempbuf),0);
          }
          else
          {
             printf("got message from ('%s',%d)\n",inet_ntoa(nAdd.sin_addr),ntohs(nAdd.sin_port));
             
            send(nSock,tempbuf,strlen(tempbuf),0);
          }
        }
        cnt=cnt+1;
       }
}

void chat_client(char* host, long port, int use_udp)
{
  int cSock,r;
  struct sockaddr_in sAdd;
  char tempbuf[1024];
  cSock=socket(AF_INET,SOCK_STREAM,0);
  if(cSock<0)
  {
    exit(1);
  }
  memset(&sAdd, '\0',sizeof(sAdd));
  sAdd.sin_family=AF_INET;
  sAdd.sin_port=htons(port);
  sAdd.sin_addr.s_addr=inet_addr(host);
  r=connect(cSock,(struct sockaddr*)&sAdd,sizeof(sAdd));
  if(r<0)
  {
    exit(1);
  }
  while(1)
{
char procVar[20];
if (scanf("%20s", procVar) == 1) {
if (strcmp(procVar, "hello") == 0){
bzero(tempbuf,1024);
strcpy(tempbuf,"hello");
send(cSock,tempbuf,strlen(tempbuf),0);
bzero(tempbuf,1024);
recv(cSock,tempbuf,sizeof(tempbuf),0);
printf("%s\n",tempbuf);
}
else if (strcmp(procVar, "goodbye") == 0){
bzero(tempbuf,1024);
strcpy(tempbuf,"goodbye");
send(cSock,tempbuf,strlen(tempbuf),0);
bzero(tempbuf,1024);
recv(cSock,tempbuf,sizeof(tempbuf),0);

printf("%s\n",tempbuf);
close(cSock);
exit(1);
}
else if (strcmp(procVar, "exit") == 0){
bzero(tempbuf,1024);
strcpy(tempbuf,"exit");
send(cSock,tempbuf,strlen(tempbuf),0);
bzero(tempbuf,1024);

recv(cSock,tempbuf,sizeof(tempbuf),0);
printf("%s\n",tempbuf);
close(cSock);
exit(1);
}
else
{
bzero(tempbuf,1024);
strcpy(tempbuf,procVar);
send(cSock,tempbuf,strlen(tempbuf),0);
bzero(tempbuf,1024);
recv(cSock,tempbuf,sizeof(tempbuf),0);
printf("%s\n",tempbuf);
}
}
}
}



