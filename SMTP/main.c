#include <stdio.h>
#include <string.h>

int connect_smtp(const char* host, int port);
void send_smtp(int sock, const char* msg, char* resp, size_t len);

/*
  Use the provided 'connect_smtp' and 'send_smtp' functions
  to connect to the "lunar.open.sice.indian.edu" smtp relay
  and send the commands to write emails as described in the
  assignment wiki.
 */

int main(int argc, char* argv[]) {
  if (argc != 3) {
    printf("Invalid arguments - %s <email-to> <email-filepath>", argv[0]);
    return -1;
  }
  char* rcpt = argv[1];
  char* filepath = argv[2];
  char i,x[1000],content[500],rx[500],mfrom[500],response[4096];
  FILE *temp;
  char* helomsg ="HELO iu.edu \n";
  char prd[10] = ".";
  int socket = connect_smtp("lunar.open.sice.indiana.edu", 25);
  send_smtp(socket,helomsg,response,4096);
  strcat(mfrom,"MAIL FROM: ");
  strcat(mfrom,rcpt);
  strcat(mfrom,"\n");
  send_smtp(socket,mfrom,response,4096);
  strcat(rx,"RCPT TO: ");
  strcat(rx,rcpt);
  strcat(rx,"\n");
  send_smtp(socket,rx,response,4096);
  strcat(content,"DATA\n");
  send_smtp(socket,content,response,4096);
  temp = fopen(filepath, "r");

  i = fgetc(temp);
  strncat(x,&i,1); //so that this construct can occur atleast once before reaching end of file

  while(i!=EOF){
      i = fgetc(temp);
      strncat(x,&i,1);
  }
  fclose(temp);
  char* op = x + 1;
  op[strlen(op)-1] = '\0'; // since end of file in C is \0 token
  //return and newlines with exit character period/fullstop
  strcat(x,"\r\n");
  strcat(x,prd);
  //final return and new lines
  strcat(x,"\r\n");
  send_smtp(socket,x,response,4096);
  printf("%s", response);
  return 0;
  /*
     STUDENT CODE HERE
   */
}